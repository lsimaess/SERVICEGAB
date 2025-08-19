from flask import (
    Blueprint, render_template, redirect, url_for, flash, request, current_app
)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask_mail import Message

from app import db, mail
from app.models import User, Worker, Requester, ServiceType
from app.forms import (
    LoginForm, UserCredentialsForm, WorkerForm, RequesterForm,
    ForgotPasswordForm, ResetPasswordForm
)

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# ---------------------
# Token utilities
# ---------------------
def generate_token(identifier):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(identifier, salt='password-reset-salt')

def verify_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        return serializer.loads(token, salt='password-reset-salt', max_age=expiration)
    except (SignatureExpired, BadSignature):
        return None

# ---------------------
# Role redirect helper
# ---------------------
def redirect_user_by_role(next_page=None):
    if current_user.is_admin:
        return redirect(next_page or url_for('admin.admin_dashboard'))
    elif current_user.role_worker:
        return redirect(next_page or url_for('worker.dashboard'))
    elif current_user.role_requester:
        return redirect(next_page or url_for('requester.dashboard'))
    else:
        flash("Rôle non reconnu. Redirection vers l'accueil.", "warning")
        return redirect(url_for('main.home'))

# ---------------------
# Login Route
# ---------------------
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        identifier = form.identifier.data.strip()
        password = form.password.data

        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier.lower())
        ).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Connexion réussie !", "success")
            next_page = request.args.get('next')
            return redirect_user_by_role(next_page)
        else:
            flash("Identifiant ou mot de passe incorrect.", "danger")
            return redirect(url_for('auth.login'))

    return render_template('auth/login.html', form=form)

# ---------------------
# Logout
# ---------------------
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Déconnexion réussie.", "info")
    return redirect(url_for('auth.login'))

# ---------------------
# Register Client
# ---------------------
@auth_bp.route('/register/requester', methods=['GET', 'POST'])
def register_requester():
    if current_user.is_authenticated:
        flash("Vous êtes déjà connecté.", "info")
        return redirect(url_for('main.home'))

    user_cred_form = UserCredentialsForm(prefix='user')
    requester_form = RequesterForm(prefix='requester')

    if user_cred_form.validate_on_submit() and requester_form.validate_on_submit():
        email_value = user_cred_form.email.data.strip().lower() if user_cred_form.email.data else None
        existing_user = User.query.filter(
            (User.username == user_cred_form.username.data) |
            ((User.email != None) & (User.email == email_value))
        ).first()

        if existing_user:
            flash("Nom d'utilisateur ou email déjà utilisé.", "danger")
            return redirect(url_for('auth.register_requester'))

        user = User(
            username=user_cred_form.username.data.strip(),
            email=email_value,
            dob=user_cred_form.dob.data,
            password_hash=generate_password_hash(user_cred_form.password.data),
            role_requester=True
        )
        db.session.add(user)
        db.session.flush()

        requester = Requester(
            user_id=user.id,
            first_name=requester_form.first_name.data.strip(),
            last_name=requester_form.last_name.data.strip(),
            email=requester_form.email.data.strip().lower() if requester_form.email.data else None,
            country_code=requester_form.country_code.data.strip(),
            phone_number=requester_form.phone_number.data.strip(),
            source=requester_form.source.data.strip() if requester_form.source.data else None,
            regular_services=requester_form.regular_services.data,
            status='pending'
        )
        db.session.add(requester)
        db.session.commit()

        flash("Compte client créé avec succès. Veuillez vous connecter.", "success")
        return redirect(url_for('auth.login'))

    return render_template('auth/register_requester.html',
                           user_cred_form=user_cred_form,
                           requester_form=requester_form)



# ---------------------
# Register Worker
# ---------------------
@auth_bp.route('/register/worker', methods=['GET', 'POST'])
def register_worker():
    if current_user.is_authenticated:
        flash("Vous êtes déjà connecté.", "info")
        return redirect(url_for('main.home'))

    user_cred_form = UserCredentialsForm(prefix='user')
    worker_form = WorkerForm(prefix='worker')

    job_choices = [(s.id, s.name) for s in ServiceType.query.order_by(ServiceType.name).all()]
    worker_form.job_primary_id.choices = job_choices
    worker_form.job_secondary_id.choices = [(0, '— Aucun —')] + job_choices

    if user_cred_form.validate_on_submit() and worker_form.validate_on_submit():
        email_value = user_cred_form.email.data.strip().lower() if user_cred_form.email.data else None
        username_value = user_cred_form.username.data.strip()
        existing_user = User.query.filter(
            (User.username == username_value) |
            ((User.email != None) & (User.email == email_value))
        ).first()

        if existing_user:
            flash("Nom d'utilisateur ou email déjà utilisé.", "danger")
            return redirect(url_for('auth.register_worker'))

        user = User(
            username=username_value,
            email=email_value,
            dob=user_cred_form.dob.data,
            password_hash=generate_password_hash(user_cred_form.password.data),
            role="travailleur",
            is_active=True
        )
        db.session.add(user)
        db.session.flush()

        worker = Worker(
            user_id=user.id,
            first_name=worker_form.first_name.data.strip(),
            last_name=worker_form.last_name.data.strip(),
            email=worker_form.email.data.strip().lower() if worker_form.email.data else None,
            phone=worker_form.phone.data.strip(),
            zone=worker_form.zone.data.strip(),
            city=worker_form.city.data.strip(),
            job_primary_id=worker_form.job_primary_id.data if worker_form.job_primary_id.data != 0 else None,
            job_secondary_id=worker_form.job_secondary_id.data if worker_form.job_secondary_id.data != 0 else None,
            experience_years=worker_form.experience_years.data,
            salary_per_job=worker_form.salary_per_job.data or None,
            bio=worker_form.bio.data.strip(),
            source=worker_form.source.data or None,
            status='En attente',
            is_active=True
        )
        db.session.add(worker)
        db.session.commit()

        flash("Compte travailleur créé avec succès. Veuillez vous connecter.", "success")
        return redirect(url_for('auth.login'))

    return render_template(
        'auth/register_worker.html',
        user_cred_form=user_cred_form,
        worker_form=worker_form
    )

# ---------------------
# Forgot / Reset Password & Other Routes...
# (Keep the rest of your file unchanged from here)

# ---------------------
# Forgot Password
# ---------------------
@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        identifier = form.email.data.strip().lower()
        user = User.query.filter(
            (User.email == identifier) | (User.username == identifier)
        ).first()

        if user and user.email:
            token = generate_token(user.email)
            reset_link = url_for('auth.reset_password', token=token, _external=True)
            msg = Message("Réinitialisation du mot de passe", recipients=[user.email])
            msg.body = f"Bonjour,\n\nCliquez ici pour réinitialiser votre mot de passe :\n{reset_link}\n\nCe lien expirera dans 1 heure."
            mail.send(msg)

        flash("Si cet identifiant existe, un lien de réinitialisation a été envoyé.", "info")
        return redirect(url_for('auth.login'))

    return render_template("auth/forgot_password.html", form=form)

# ---------------------
# Reset Password
# ---------------------
@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    identifier = verify_token(token)
    user = User.query.filter(
        (User.email == identifier) | (User.username == identifier)
    ).first()

    if not identifier or not user:
        flash("Lien invalide ou expiré.", "danger")
        return redirect(url_for('auth.forgot_password'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password_hash = generate_password_hash(form.password.data)
        db.session.commit()
        flash("Mot de passe réinitialisé avec succès. Connectez-vous.", "success")
        return redirect(url_for('auth.login'))

    return render_template("auth/reset_password.html", form=form)

# ---------------------
# Admin Reset Link (manual)
# ---------------------
@auth_bp.route('/reset-link/<username>')
@login_required
def admin_reset_link(username):
    if not current_user.is_admin:
        flash("Accès refusé", "danger")
        return redirect(url_for('main.home'))

    user = User.query.filter_by(username=username).first()
    if not user:
        flash("Utilisateur introuvable", "danger")
        return redirect(url_for('admin.admin_dashboard'))

    token = generate_token(user.username)
    reset_link = url_for('auth.reset_password', token=token, _external=True)
    flash(f"Lien de réinitialisation : {reset_link}", "info")
    return redirect(url_for('admin.admin_dashboard'))
