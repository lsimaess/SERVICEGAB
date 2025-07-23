from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class ServiceTypeForm(FlaskForm):
    name = StringField("Nom du type de service", validators=[DataRequired(), Length(max=100)])
    submit = SubmitField("Ajouter")
