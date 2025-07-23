from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, Length

class RequesterForm(FlaskForm):
    full_name = StringField("Nom Complet", validators=[DataRequired(), Length(max=100)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone = StringField("Téléphone", validators=[DataRequired(), Length(max=20)])
    zone = SelectField("Zone", choices=[
        ('Akanda', 'Akanda'), 
        ('Owendo', 'Owendo'), 
        ('Libreville-Nord', 'Libreville-Nord'),
        ('Libreville-Centre', 'Libreville-Centre'), 
        ('Libreville-Sud', 'Libreville-Sud')
    ], validators=[DataRequired()])
    description = TextAreaField("Description du besoin", validators=[Length(max=300)])
    submit = SubmitField("S'inscrire")
