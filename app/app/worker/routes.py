from flask import Blueprint, render_template, redirect, url_for, flash, request
from app import db
from app.models import Worker
from app.forms.worker_form import WorkerForm
from werkzeug.utils import secure_filename
import os

worker_bp = Blueprint('worker', __name__, url_prefix='/worker')

@worker_bp.route('/register', methods=['GET', 'POST'])
def register_worker():
    form = WorkerForm()
    if form.validate_on_submit():
        filename = None
        if form.profile_picture.data:
            filename = secure_filename(form.profile_picture.data.filename)
            folder = os.path.join('static', 'uploads', 'workers')
            os.makedirs(folder, exist_ok=True)
            filepath = os.path.join(folder, filename)
            form.profile_picture.data.save(filepath)

        new_worker = Worker(
            full_name=form.full_name.data,
            email=form.email.data,
            phone=form.phone.data,
            zone=form.zone.data,
            bio=form.bio.data,
            profile_picture=f"uploads/workers/{filename}" if filename else None,
            status="pending"
        )
        db.session.add(new_worker)
        db.session.commit()
        flash("Inscription réussie ! En attente d’approbation par l’administrateur.", "success")
        return redirect(url_for('main.home'))

    return render_template('worker/register_worker.html', form=form)
