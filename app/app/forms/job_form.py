from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, DecimalField, DateTimeField
from wtforms.validators import DataRequired, NumberRange, Length
from wtforms_sqlalchemy.fields import QuerySelectMultipleField
from app.models import ServiceType

def service_type_choices():
    return ServiceType.query

class JobForm(FlaskForm):
    title = StringField("Titre du Service", validators=[DataRequired(), Length(max=100)])
    description = TextAreaField("Description", validators=[DataRequired(), Length(max=500)])
    zone = SelectField("Zone", choices=[
        ('Akanda', 'Akanda'), 
        ('Owendo', 'Owendo'), 
        ('Libreville-Nord', 'Libreville-Nord'),
        ('Libreville-Centre', 'Libreville-Centre'), 
        ('Libreville-Sud', 'Libreville-Sud')
    ], validators=[DataRequired()])
    service_types = QuerySelectMultipleField("Types de service", query_factory=service_type_choices, get_label="name")
    offer_price = DecimalField("Prix proposé (FCFA)", validators=[DataRequired(), NumberRange(min=0)])
    frequency = SelectField("Fréquence", choices=[
        ('ponctuel', 'Ponctuel'), 
        ('hebdomadaire', 'Hebdomadaire'), 
        ('mensuel', 'Mensuel')
    ], validators=[DataRequired()])
    preferred_time = DateTimeField("Date et heure préférées", format='%Y-%m-%d %H:%M', validators=[DataRequired()])
    submit = SubmitField("Créer le job")
