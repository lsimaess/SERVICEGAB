from flask import Blueprint, render_template, redirect, url_for, flash
from app import db
from app.models import Requester
from app.forms.requester_form import RequesterForm

requester_bp = Blueprint('requester', __name__, url_prefix='/requester')

@requester_bp.route('/register', methods=['GET', 'POST'])
def register_requester():
    form = RequesterForm()
    if form.validate_on_submit():
        new_requester = Requester(
            full_name=form.full_name.data,
            email=form.email.data,
            phone=form.phone.data,
            zone=form.zone.data,
            description=form.description.data,
            status="pending"
        )
        db.session.add(new_requester)
        db.session.commit()
        flash("Inscription réussie ! En attente de validation.", "success")
        return redirect(url_for('main.home'))

    return render_template('requester/register_requester.html', form=form)
