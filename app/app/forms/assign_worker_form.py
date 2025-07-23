from flask_wtf import FlaskForm
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms import SubmitField
from app.models import Worker

def approved_workers():
    return Worker.query.filter_by(status='approved', is_deleted=False).order_by(Worker.full_name)

class AssignWorkerForm(FlaskForm):
    worker = QuerySelectField(
        "Attribuer un prestataire",
        query_factory=approved_workers,
        get_label=lambda w: f"{w.full_name} ({w.zone})",
        allow_blank=False
    )
    submit = SubmitField("Attribuer")
