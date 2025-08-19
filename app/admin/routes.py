# app/admin/routes.py

from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models import Worker, Requester, Job, ServiceType, Status, JobRecurrenceChangeLog
from app.forms import WorkerForm, RequesterForm, JobForm, JobCompletionForm, ServiceTypeForm

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# -----------------------------
# Helpers
# -----------------------------
def admin_only(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not getattr(current_user, "is_admin", False):
            abort(403)
        return view(*args, **kwargs)
    return wrapper

STATUS_MAP = {
    'pending': 'En attente',
    'approved': 'Approuvé',
    'rejected': 'Rejeté'
}

# -----------------------------
# Admin Dashboard
# -----------------------------
@admin_bp.route('/')
@login_required
@admin_only
def admin_dashboard():
    worker_count = Worker.query.filter_by(is_active=True).count()
    pending_worker_count = Worker.query.filter_by(status='En attente', is_active=True).count()
    requester_count = Requester.query.filter_by(is_active=True).count()
    pending_requester_count = Requester.query.filter_by(status='En attente', is_active=True).count()
    job_count = Job.query.filter_by(is_active=True).count()
    pending_job_count = Job.query.filter_by(status=Status.PENDING, is_active=True).count()
    assigned_job_count = Job.query.filter_by(status=Status.ASSIGNED, is_active=True).count()

    return render_template(
        'admin/dashboard.html',
        worker_count=worker_count,
        pending_worker_count=pending_worker_count,
        requester_count=requester_count,
        pending_requester_count=pending_requester_count,
        job_count=job_count,
        pending_job_count=pending_job_count,
        assigned_job_count=assigned_job_count
    )

# -----------------------------
# Workers
# -----------------------------
@admin_bp.route('/travailleurs')
@login_required
@admin_only
def admin_worker_list():
    query = Worker.query.filter_by(is_active=True)
    status_param = request.args.get('status', '').strip().lower()
    if status_param in STATUS_MAP:
        query = query.filter(Worker.status == STATUS_MAP[status_param])
    workers = query.order_by(Worker.created_at.desc()).all()
    return render_template('admin/worker_list.html', workers=workers)


@admin_bp.route('/travailleurs/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_only
def admin_worker_detail(id):
    worker = Worker.query.get_or_404(id)
    service_types = ServiceType.query.order_by(ServiceType.name).all()
    choices = [(s.id, s.name) for s in service_types]

    form = WorkerForm(obj=worker, is_admin=True, is_update=True)
    form.job_primary_id.choices = choices
    form.job_secondary_id.choices = [(0, '— Aucun —')] + choices

    if request.method == "GET":
        form.job_secondary_id.data = worker.job_secondary_id or 0

        # ✅ Pre-fill separate phone fields directly if present
        form.country_code.data = getattr(worker, "country_code", "")
        form.phone_number.data = getattr(worker, "phone_number", "")

    if form.validate_on_submit():
        worker.first_name = form.first_name.data
        worker.last_name = form.last_name.data
        worker.email = form.email.data or None

        # ✅ Save phone components separately
        worker.country_code = form.country_code.data
        worker.phone_number = form.phone_number.data

        worker.zone = form.zone.data
        worker.city = form.city.data
        worker.job_primary_id = form.job_primary_id.data
        worker.job_secondary_id = None if form.job_secondary_id.data == 0 else form.job_secondary_id.data
        worker.experience_years = form.experience_years.data
        worker.salary_per_job = form.salary_per_job.data or None
        worker.bio = form.bio.data
        worker.source = form.source.data or None

        db.session.commit()
        flash("Travailleur mis à jour.", "success")
        return redirect(url_for('admin.admin_worker_list'))

    return render_template('admin/worker_detail.html', form=form, worker=worker)


@admin_bp.route('/travailleurs/<int:id>/delete', methods=['POST'])
@login_required
@admin_only
def admin_worker_delete(id):
    worker = Worker.query.get_or_404(id)
    worker.is_active = False
    db.session.commit()
    flash("Travailleur supprimé (soft delete).", "warning")
    return redirect(url_for('admin.admin_worker_list'))


@admin_bp.route('/travailleurs/approve_bulk', methods=['POST'])
@login_required
@admin_only
def admin_worker_approve_bulk():
    ids = [int(x) for x in request.form.getlist('selected_ids') if str(x).isdigit()]
    if not ids:
        flash("Aucun élément sélectionné.", "warning")
        return redirect(url_for('admin.admin_worker_list'))

    workers = Worker.query.filter(Worker.id.in_(ids), Worker.is_active.is_(True)).all()
    for w in workers:
        w.status = 'Approuvé'
    db.session.commit()
    flash(f"{len(workers)} travailleurs approuvés.", "success")
    return redirect(url_for('admin.admin_worker_list'))


# -----------------------------
# Clients
# -----------------------------
from app.forms import RequesterProfileUpdateForm  # ✅ Ensure it's imported

@admin_bp.route('/clients')
@login_required
@admin_only
def admin_requester_list():
    query = Requester.query.filter_by(is_active=True)
    status_param = request.args.get('status', '').strip().lower()
    if status_param in STATUS_MAP:
        query = query.filter(Requester.status == STATUS_MAP[status_param])
    requesters = query.order_by(Requester.created_at.desc()).all()
    return render_template('admin/requester_list.html', requesters=requesters)


@admin_bp.route('/clients/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_only
def admin_requester_detail(id):
    requester = Requester.query.get_or_404(id)
    form = RequesterProfileUpdateForm(obj=requester)

    # ✅ Pre-fill for GET
    if request.method == "GET":
        form.country_code.data = requester.country_code
        form.phone_number.data = requester.phone_number
        form.regular_services.data = requester.regular_services or []

    if form.validate_on_submit():
        requester.first_name = form.first_name.data
        requester.last_name = form.last_name.data
        requester.email = form.email.data or None
        requester.country_code = form.country_code.data
        requester.phone_number = form.phone_number.data
        requester.source = form.source.data or None
        requester.regular_services = form.regular_services.data or []

        db.session.commit()
        flash("Client mis à jour.", "success")
        return redirect(url_for('admin.admin_requester_list'))

    return render_template('admin/requester_detail.html', form=form, requester=requester)


@admin_bp.route('/clients/<int:id>/delete', methods=['POST'])
@login_required
@admin_only
def admin_requester_delete(id):
    requester = Requester.query.get_or_404(id)
    requester.is_active = False
    db.session.commit()
    flash("Client supprimé (soft delete).", "warning")
    return redirect(url_for('admin.admin_requester_list'))


@admin_bp.route('/clients/approve_bulk', methods=['POST'])
@login_required
@admin_only
def admin_requester_approve_bulk():
    ids = [int(x) for x in request.form.getlist('selected_ids') if str(x).isdigit()]
    if not ids:
        flash("Aucun élément sélectionné.", "warning")
        return redirect(url_for('admin.admin_requester_list'))

    requesters = Requester.query.filter(Requester.id.in_(ids), Requester.is_active.is_(True)).all()
    for r in requesters:
        r.status = 'Approuvé'
    db.session.commit()
    flash(f"{len(requesters)} clients approuvés.", "success")
    return redirect(url_for('admin.admin_requester_list'))

# -----------------------------
# 📋 Gestion des Emplois (Jobs)
# -----------------------------

from datetime import datetime, timedelta
from flask import (
    render_template, request, redirect, url_for, flash
)
from flask_login import login_required
from app import db
from app.models import Job, Requester, Worker, ServiceType, Status
from app.forms import JobForm
from app.forms import ZONES

@admin_bp.route('/emplois')
@login_required
@admin_only
def admin_job_list():
    """Admin view: list all jobs with filters."""
    query = Job.query.filter_by(is_active=True)

    status_param = request.args.get('status', '').strip().lower()
    if status_param in Status.__dict__:
        query = query.filter(Job.status == getattr(Status, status_param.upper()))

    requester_id = request.args.get('requester_id')
    if requester_id and requester_id.isdigit():
        query = query.filter(Job.requester_id == int(requester_id))

    worker_id = request.args.get('worker_id')
    if worker_id and worker_id.isdigit():
        query = query.filter(Job.worker_id == int(worker_id))

    service_type_id = request.args.get('service_type_id')
    if service_type_id and service_type_id.isdigit():
        query = query.filter(Job.service_needed_id == int(service_type_id))

    date_str = request.args.get('date')
    if date_str:
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            query = query.filter(db.func.date(Job.date_needed) == date_obj)
        except ValueError:
            flash("Format de date invalide. Utilisez AAAA-MM-JJ.", "danger")

    zone_param = request.args.get('zone')
    if zone_param:
        query = query.filter(Job.zone == zone_param)

    repeated_param = request.args.get('repeated')
    if repeated_param == '1':
        query = query.filter(Job.repeated.is_(True))
    elif repeated_param == '0':
        query = query.filter(Job.repeated.is_(False))

    jobs = query.order_by(Job.created_at.desc()).all()
    workers = Worker.query.filter_by(is_active=True).all()
    requesters = Requester.query.filter_by(is_active=True, status="Approuvé").all()
    services = ServiceType.query.order_by(ServiceType.name).all()

    return render_template(
        'admin/job_list.html',
        jobs=jobs,
        workers=workers,
        requesters=requesters,
        services=services,
        zones=ZONES,
        request_args=request.args
    )


@admin_bp.route('/emplois/creer', methods=['GET', 'POST'])
@login_required
@admin_only
def admin_job_create():
    form = JobForm()

    services = ServiceType.query.order_by(ServiceType.name).all()
    requesters = Requester.query.filter_by(is_active=True, status="Approuvé").all()
    form.service_needed_id.choices = [(s.id, s.name) for s in services]
    form.requester_id.choices = [(r.id, r.full_name) for r in requesters]

    workers_query = Worker.query.filter_by(is_active=True)
    filtered_workers = []

    if request.method == "POST":
        if form.service_needed_id.data:
            sid = form.service_needed_id.data
            workers_query = workers_query.filter(
                (Worker.job_primary_id == sid) | (Worker.job_secondary_id == sid)
            )

        if form.zone.data:
            workers_query = workers_query.filter(Worker.zone == form.zone.data)

        if form.date_needed.data:
            target_time = form.date_needed.data
            buffer_start = target_time - timedelta(hours=1)
            buffer_end = target_time + timedelta(hours=1)

            busy_worker_ids = db.session.query(Job.worker_id).filter(
                Job.date_needed >= buffer_start,
                Job.date_needed <= buffer_end,
                Job.status.in_([Status.ASSIGNED, Status.PENDING])
            ).subquery()

            workers_query = workers_query.filter(~Worker.id.in_(busy_worker_ids))

        filtered_workers = workers_query.all()

    def get_worker_label(w):
        rating = w.get_average_rating()
        rating_str = f"{rating:.1f}★" if rating else "— Aucune note —"
        role = "Principal" if w.job_primary_id == form.service_needed_id.data else "Secondaire"
        return f"{w.full_name} — {role} ({rating_str})"

    form.worker_id.choices = [
        (w.id, get_worker_label(w)) for w in filtered_workers
    ] if filtered_workers else []

    if form.validate_on_submit() and "filter_workers" not in request.form:
        job = Job(
            requester_id=form.requester_id.data,
            worker_id=form.worker_id.data,
            service_needed_id=form.service_needed_id.data,
            zone=form.zone.data or "",
            date_needed=form.date_needed.data,
            description=form.description.data,
            payment_amount=form.payment_amount.data,
            repeated=form.repeated.data,
            recurrence_pattern=form.recurrence_pattern.data if form.repeated.data else None,
            parent_job_id=form.parent_job_id.data or None,
            status=Status.ASSIGNED if form.worker_id.data else Status.PENDING,
            is_active=True
        )
        db.session.add(job)
        db.session.commit()
        flash("Nouvelle tâche créée avec succès.", "success")
        return redirect(url_for('admin.admin_job_list'))

    return render_template('admin/job_form.html', form=form)


@admin_bp.route('/emplois/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_only
def admin_job_detail(id):
    job = Job.query.get_or_404(id)

    if job.status in [Status.COMPLETED, Status.CANCELLED]:
        flash("Impossible de modifier une tâche déjà clôturée ou annulée.", "warning")
        return redirect(url_for('admin.admin_job_list'))

    form = JobForm(obj=job)

    requesters = Requester.query.filter_by(is_active=True, status="Approuvé").all()
    services = ServiceType.query.order_by(ServiceType.name).all()
    workers = Worker.query.filter_by(is_active=True).all()

    form.requester_id.choices = [(r.id, r.full_name) for r in requesters]
    form.service_needed_id.choices = [(s.id, s.name) for s in services]

    def get_worker_label(w):
        rating = w.get_average_rating()
        rating_str = f"{rating:.1f}★" if rating else "— Aucune note —"
        role = "Principal" if w.job_primary_id == job.service_needed_id else "Secondaire"
        return f"{w.full_name} — {role} ({rating_str})"

    form.worker_id.choices = [(w.id, get_worker_label(w)) for w in workers]

    if form.validate_on_submit():
        job.requester_id = form.requester_id.data
        job.worker_id = form.worker_id.data
        job.service_needed_id = form.service_needed_id.data
        job.zone = form.zone.data or ""
        job.date_needed = form.date_needed.data
        job.description = form.description.data
        job.payment_amount = form.payment_amount.data
        job.status = Status.ASSIGNED if job.worker_id else Status.PENDING
        job.repeated = form.repeated.data
        job.recurrence_pattern = form.recurrence_pattern.data if form.repeated.data else None
        job.parent_job_id = form.parent_job_id.data or None

        # Optional: handle apply_to_children checkbox for bulk updates here

        db.session.commit()
        flash("Tâche mise à jour.", "success")
        return redirect(url_for('admin.admin_job_list'))

    return render_template('admin/job_form.html', form=form, job=job)

@admin_bp.route('/emplois/<int:id>/delete', methods=['POST'])
@login_required
@admin_only
def admin_job_delete(id):
    job = Job.query.get_or_404(id)
    job.is_active = False  # 🔁 Soft delete
    db.session.commit()
    flash("Tâche supprimée (soft delete).", "warning")
    return redirect(url_for('admin.admin_job_list'))

@admin_bp.route('/emplois/<int:job_id>/dupliquer', methods=['GET', 'POST'])
@login_required
@admin_only
def admin_job_duplicate(job_id):
    original = Job.query.get_or_404(job_id)
    form = JobForm()

    services = ServiceType.query.order_by(ServiceType.name).all()
    requesters = Requester.query.filter_by(is_active=True, status="Approuvé").all()
    workers = Worker.query.filter_by(is_active=True).all()

    form.service_needed_id.choices = [(s.id, s.name) for s in services]
    form.requester_id.choices = [(r.id, r.full_name) for r in requesters]

    def get_worker_label(w):
        rating = w.get_average_rating()
        rating_str = f"{rating:.1f}★" if rating else "— Aucune note —"
        role = "Principal" if w.job_primary_id == original.service_needed_id else "Secondaire"
        return f"{w.full_name} — {role} ({rating_str})"

    form.worker_id.choices = [(w.id, get_worker_label(w)) for w in workers]

    if request.method == "GET":
        form.requester_id.data = original.requester_id
        form.worker_id.data = original.worker_id
        form.service_needed_id.data = original.service_needed_id
        form.zone.data = original.zone
        form.date_needed.data = original.date_needed
        form.description.data = original.description
        form.payment_amount.data = original.payment_amount
        form.repeated.data = original.repeated
        form.recurrence_pattern.data = original.recurrence_pattern
        form.parent_job_id.data = original.id  # ✅ Set current job as parent

    if form.validate_on_submit():
        job = Job(
            requester_id=form.requester_id.data,
            worker_id=form.worker_id.data,
            service_needed_id=form.service_needed_id.data,
            zone=form.zone.data or "",
            date_needed=form.date_needed.data,
            description=form.description.data,
            payment_amount=form.payment_amount.data,
            repeated=form.repeated.data,
            recurrence_pattern=form.recurrence_pattern.data if form.repeated.data else None,
            parent_job_id=form.parent_job_id.data or None,
            status=Status.ASSIGNED if form.worker_id.data else Status.PENDING,
            is_active=True
        )
        db.session.add(job)
        db.session.commit()
        flash("Tâche dupliquée avec succès.", "success")
        return redirect(url_for('admin.admin_job_list'))

    return render_template('admin/job_form.html', form=form)


# -----------------------------
# Types de Service (Service Types)
# -----------------------------

@admin_bp.route('/services')
@login_required
@admin_only
def admin_service_type_list():
    """List all service types."""
    service_types = ServiceType.query.order_by(ServiceType.name).all()
    return render_template('admin/service_type_list.html', service_types=service_types)


@admin_bp.route('/services/ajouter', methods=['GET', 'POST'])
@login_required
@admin_only
def admin_service_type_add():
    """Add a new service type."""
    form = ServiceTypeForm()

    if form.validate_on_submit():
        new_service = ServiceType(name=form.name.data)
        db.session.add(new_service)
        db.session.commit()
        flash("Nouveau service ajouté.", "success")
        return redirect(url_for('admin.admin_service_type_list'))

    return render_template('admin/service_type_form.html', form=form)


@admin_bp.route('/services/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_only
def admin_service_type_edit(id):
    """Edit an existing service type."""
    service_type = ServiceType.query.get_or_404(id)
    form = ServiceTypeForm(obj=service_type)

    if form.validate_on_submit():
        service_type.name = form.name.data
        db.session.commit()
        flash("Type de service mis à jour.", "success")
        return redirect(url_for('admin.admin_service_type_list'))

    return render_template('admin/service_type_form.html', form=form, service_type=service_type)


@admin_bp.route('/services/<int:id>/delete', methods=['POST'])
@login_required
@admin_only
def admin_service_type_delete(id):
    """Delete a service type."""
    service_type = ServiceType.query.get_or_404(id)
    db.session.delete(service_type)  # Use soft delete if desired
    db.session.commit()
    flash("Type de service supprimé.", "warning")
    return redirect(url_for('admin.admin_service_type_list'))
