from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Job, Requester, ServiceType
from datetime import datetime

requester_bp = Blueprint('requester', __name__, url_prefix='/requester')


@requester_bp.route('/dashboard', endpoint='dashboard')
@login_required
def dashboard():
    if not hasattr(current_user, 'requester'):
        flash("Seuls les demandeurs peuvent accéder à ce tableau de bord.", "warning")
        return redirect(url_for('main.home'))

    jobs = Job.query.filter_by(requester_id=current_user.id).order_by(Job.created_at.desc()).all()
    return render_template('requester/dashboard.html', jobs=jobs)


@requester_bp.route('/create', methods=['GET', 'POST'], endpoint='create_job')
@login_required
def create_job():
    if not hasattr(current_user, 'requester'):
        flash("Seuls les demandeurs peuvent créer une demande.", "warning")
        return redirect(url_for('main.home'))

    service_types = ServiceType.query.order_by(ServiceType.name).all()

    if request.method == 'POST':
        service_id = request.form.get('service_id')
        description = request.form.get('description')
        date_needed = request.form.get('date_needed')
        location = request.form.get('location')

        if not all([service_id, description, date_needed, location]):
            flash("Veuillez remplir tous les champs.", "danger")
        else:
            new_job = Job(
                requester_id=current_user.id,
                service_id=service_id,
                description=description.strip(),
                date_needed=datetime.strptime(date_needed, '%Y-%m-%d'),
                location=location.strip(),
                status='PENDING'
            )
            db.session.add(new_job)
            db.session.commit()
            flash("Demande créée avec succès.", "success")
            return redirect(url_for('requester.dashboard'))

    return render_template('requester/create_job.html', service_types=service_types)


@requester_bp.route('/job/<int:id>', endpoint='view_job')
@login_required
def view_job(id):
    job = Job.query.get_or_404(id)
    if job.requester_id != current_user.id:
        flash("Accès non autorisé à cette demande.", "danger")
        return redirect(url_for('requester.dashboard'))

    return render_template('requester/job_detail.html', job=job)
