from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Worker, Job, ServiceType
from app.forms import WorkerProfileUpdateForm
from sqlalchemy import func
from werkzeug.datastructures import FileStorage
from app.utils import save_file

worker_bp = Blueprint('worker', __name__, url_prefix='/worker')


@worker_bp.route('/dashboard')
@login_required
def dashboard():
    if not hasattr(current_user, 'worker'):
        flash("Seuls les prestataires peuvent accéder à ce tableau de bord.", "warning")
        return redirect(url_for('main.home'))

    worker = current_user.worker
    assigned_jobs = Job.query.filter_by(worker_id=worker.id).order_by(Job.date_needed.desc()).all()
    total_completed = Job.query.filter_by(worker_id=worker.id, status='COMPLETED').count()
    avg_rating = db.session.query(func.avg(Job.rating)).filter(
        Job.worker_id == worker.id, Job.rating.isnot(None)
    ).scalar()
    avg_rating = round(avg_rating, 2) if avg_rating else None

    return render_template('worker/dashboard.html',
                           worker=worker,
                           total_completed=total_completed,
                           avg_rating=avg_rating,
                           jobs=assigned_jobs)


@worker_bp.route('/jobs', endpoint='worker_job_list')
@login_required
def job_list():
    if not hasattr(current_user, 'worker'):
        flash("Seuls les prestataires peuvent accéder à cette page.", "warning")
        return redirect(url_for('main.home'))

    worker = current_user.worker
    jobs = Job.query.filter_by(worker_id=worker.id).order_by(Job.date_needed.desc()).all()
    return render_template('worker/job_list.html', jobs=jobs)


@worker_bp.route('/job/<int:id>', endpoint='worker_job_detail')
@login_required
def view_job(id):
    job = Job.query.get_or_404(id)
    if not hasattr(current_user, 'worker') or job.worker_id != current_user.worker.id:
        flash("Accès non autorisé à cette tâche.", "danger")
        return redirect(url_for('worker.dashboard'))
    return render_template('worker/worker_job_detail.html', job=job)


@worker_bp.route('/job/<int:id>/complete', methods=['POST'], endpoint='worker_complete_job')
@login_required
def complete_job(id):
    job = Job.query.get_or_404(id)
    if not hasattr(current_user, 'worker') or job.worker_id != current_user.worker.id:
        flash("Action non autorisée.", "danger")
        return redirect(url_for('worker.dashboard'))

    job.status = 'COMPLETED'
    db.session.commit()
    flash("Tâche marquée comme complétée.", "success")
    return redirect(url_for('worker.dashboard'))


@worker_bp.route('/profile', endpoint='worker_profile')
@login_required
def profile():
    if not hasattr(current_user, 'worker'):
        flash("Seuls les prestataires peuvent accéder à cette page.", "warning")
        return redirect(url_for('main.home'))

    worker = current_user.worker
    return render_template('worker/profile.html', worker=worker)


@worker_bp.route('/edit-profile', methods=['GET', 'POST'], endpoint='worker_edit_profile')
@login_required
def edit_profile():
    if not hasattr(current_user, 'worker'):
        flash("Seuls les prestataires peuvent modifier leur profil.", "warning")
        return redirect(url_for('main.home'))

    worker = current_user.worker
    form = WorkerProfileUpdateForm(obj=worker)

    # Populate job choices
    services = ServiceType.query.order_by(ServiceType.name).all()
    form.job_primary_id.choices = [(s.id, s.name) for s in services]
    form.job_secondary_id.choices = [(0, '— Aucun —')] + [(s.id, s.name) for s in services]

    # Set secondary job default on GET only
    if request.method == 'GET':
        form.job_secondary_id.data = worker.job_secondary_id or 0

    if form.validate_on_submit():
        worker.first_name = form.first_name.data
        worker.last_name = form.last_name.data
        worker.phone = form.phone.data
        worker.zone = form.zone.data
        worker.city = form.city.data
        worker.job_primary_id = form.job_primary_id.data
        worker.bio = form.bio.data
        worker.source = form.source.data

        # Safely handle secondary job ID
        try:
            sec_id = int(form.job_secondary_id.data)
            worker.job_secondary_id = None if sec_id == 0 else sec_id
        except (ValueError, TypeError):
            worker.job_secondary_id = None

        # Handle profile picture upload
        if isinstance(form.profile_picture.data, FileStorage) and form.profile_picture.data.filename:
            worker.profile_picture_path = save_file(form.profile_picture.data)

        # Handle ID document upload
        if isinstance(form.id_document.data, FileStorage) and form.id_document.data.filename:
            worker.id_document_path = save_file(form.id_document.data)

        db.session.commit()
        flash("Profil mis à jour avec succès.", "success")
        return redirect(url_for('worker.worker_profile'))

    return render_template('worker/edit_profile.html', form=form)
