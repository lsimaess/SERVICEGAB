from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, FileField
from wtforms.validators import DataRequired, Email, Length
from flask_wtf.file import FileAllowed

class WorkerForm(FlaskForm):
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
    profile_picture = FileField("Photo de profil", validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    bio = TextAreaField("À propos", validators=[Length(max=300)])
    submit = SubmitField("S'inscrire")
