from flask import (
    Blueprint, render_template, redirect, url_for, flash, request, current_app
)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

from app import db, mail
from app.models import User, Worker, Requester, ServiceType
from app.forms import (
    LoginForm, UserCredentialsForm, WorkerForm, RequesterForm,
    ForgotPasswordForm, ResetPasswordForm
)
from flask_mail import Message

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


# Utilities for token generation and verification
def generate_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='password-reset-salt')


def verify_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=expiration)
        return email
    except (SignatureExpired, BadSignature):
        return None


# LOGIN
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # Redirect logged in users to their dashboard
        if current_user.role == 'worker':
            return redirect(url_for('worker.dashboard'))
        elif current_user.role == 'requester':
            return redirect(url_for('requester.dashboard'))
        elif current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('main.home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash("Connexion réussie !", "success")

            if user.role == 'worker':
                return redirect(url_for('worker.dashboard'))
            elif user.role == 'requester':
                return redirect(url_for('requester.dashboard'))
            elif user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('main.home'))
        else:
            flash("Email ou mot de passe incorrect", "danger")
    return render_template('auth/login.html', form=form)


# LOGOUT
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Déconnexion réussie.", "info")
    return redirect(url_for('auth.login'))


# REGISTER WORKER
@auth_bp.route('/register/worker', methods=['GET', 'POST'])
def register_worker():
    if current_user.is_authenticated:
        flash("Vous êtes déjà connecté.", "info")
        return redirect(url_for('main.home'))

    user_cred_form = UserCredentialsForm(prefix='user')
    worker_form = WorkerForm(prefix='worker')

    # Populate job choices
    job_choices = [(s.id, s.name) for s in db.session.query(ServiceType).order_by(ServiceType.name).all()]
    worker_form.job_primary_id.choices = job_choices
    worker_form.job_secondary_id.choices = [(0, '---')] + job_choices

    if user_cred_form.validate_on_submit() and worker_form.validate_on_submit():
        existing_user = User.query.filter(
            (User.username == user_cred_form.username.data) | 
            (User.email == user_cred_form.email.data.strip().lower())
        ).first()
        if existing_user:
            flash("Nom d'utilisateur ou email déjà utilisé.", "danger")
        else:
            user = User(
                username=user_cred_form.username.data.strip(),
                email=user_cred_form.email.data.strip().lower(),
                password_hash=generate_password_hash(user_cred_form.password.data),
                role='worker'
            )
            db.session.add(user)
            db.session.flush()

            worker = Worker(
                user_id=user.id,
                first_name=worker_form.first_name.data.strip(),
                last_name=worker_form.last_name.data.strip(),
                email=worker_form.email.data.strip().lower(),
                phone=worker_form.phone.data.strip(),
                zone=worker_form.zone.data.strip(),
                city=worker_form.city.data.strip(),
                job_primary_id=worker_form.job_primary_id.data if worker_form.job_primary_id.data != 0 else None,
                job_secondary_id=worker_form.job_secondary_id.data if worker_form.job_secondary_id.data != 0 else None,
                experience_years=worker_form.experience_years.data,
                salary_per_job=worker_form.salary_per_job.data,
                bio=worker_form.bio.data.strip(),
                status='pending',
            )
            db.session.add(worker)
            db.session.commit()
            flash("Compte prestataire créé avec succès. Veuillez vous connecter.", "success")
            return redirect(url_for('auth.login'))

    return render_template(
        'auth/register_worker.html',
        user_cred_form=user_cred_form,
        worker_form=worker_form
    )


# REGISTER REQUESTER
@auth_bp.route('/register/requester', methods=['GET', 'POST'])
def register_requester():
    if current_user.is_authenticated:
        flash("Vous êtes déjà connecté.", "info")
        return redirect(url_for('main.home'))

    user_cred_form = UserCredentialsForm(prefix='user')
    requester_form = RequesterForm(prefix='requester')

    if user_cred_form.validate_on_submit() and requester_form.validate_on_submit():
        existing_user = User.query.filter(
            (User.username == user_cred_form.username.data) | 
            (User.email == user_cred_form.email.data.strip().lower())
        ).first()
        if existing_user:
            flash("Nom d'utilisateur ou email déjà utilisé.", "danger")
        else:
            user = User(
                username=user_cred_form.username.data.strip(),
                email=user_cred_form.email.data.strip().lower(),
                password_hash=generate_password_hash(user_cred_form.password.data),
                role='requester'
            )
            db.session.add(user)
            db.session.flush()

            requester = Requester(
                user_id=user.id,
                first_name=requester_form.first_name.data.strip(),
                last_name=requester_form.last_name.data.strip(),
                email=requester_form.email.data.strip().lower(),
                phone=requester_form.phone.data.strip(),
                source=requester_form.source.data.strip() if requester_form.source.data else None,
                regular_services=requester_form.regular_services.data,
                status='pending',
            )
            db.session.add(requester)
            db.session.commit()
            flash("Compte demandeur créé avec succès. Veuillez vous connecter.", "success")
            return redirect(url_for('auth.login'))

    return render_template(
        'auth/register_requester.html',
        user_cred_form=user_cred_form,
        requester_form=requester_form
    )


# FORGOT PASSWORD
@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user:
            token = generate_token(user.email)
            reset_link = url_for('auth.reset_password', token=token, _external=True)
            msg = Message(
                "Réinitialisation du mot de passe",
                recipients=[user.email]
            )
            msg.body = f"Bonjour,\n\nCliquez ici pour réinitialiser votre mot de passe :\n{reset_link}\n\nCe lien expirera dans 1 heure."
            mail.send(msg)
        flash("Si cet email existe, un lien de réinitialisation a été envoyé.", "info")
        return redirect(url_for('auth.login'))
    return render_template("auth/forgot_password.html", form=form)


# RESET PASSWORD
@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = verify_token(token)
    if not email:
        flash("Lien invalide ou expiré.", "danger")
        return redirect(url_for('auth.forgot_password'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=email).first()
        if user:
            user.password_hash = generate_password_hash(form.password.data)
            db.session.commit()
            flash("Mot de passe réinitialisé avec succès. Connectez-vous.", "success")
            return redirect(url_for('auth.login'))
        else:
            flash("Utilisateur introuvable.", "danger")

    return render_template("auth/reset_password.html", form=form)

