from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import (
    StringField, TextAreaField, IntegerField, SelectField, SubmitField,
    BooleanField, FileField, PasswordField, HiddenField, SelectMultipleField
)
from wtforms.validators import (
    DataRequired, Email, Optional, NumberRange, EqualTo,
    ValidationError, Regexp
)
from wtforms.widgets import ListWidget, CheckboxInput
from app.models import ServiceType, User

# Helper to load service choices
def get_service_choices():
    return [(str(s.id), s.name) for s in ServiceType.query.order_by(ServiceType.name).all()]

# MultiCheckbox for JSON fields
class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

# -----------------------
# User Credentials Form
# -----------------------
class UserCredentialsForm(FlaskForm):
    username = StringField("Nom d'utilisateur", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Mot de passe", validators=[DataRequired()])
    confirm_password = PasswordField("Confirmer le mot de passe", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("S'inscrire")

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError("Ce nom d'utilisateur est déjà pris. Veuillez en choisir un autre.")

# -----------------------
# Worker Registration Form
# -----------------------
class WorkerForm(FlaskForm):
    first_name = StringField("Prénom", validators=[DataRequired()])
    last_name = StringField("Nom", validators=[DataRequired()])
    
    phone = StringField("Téléphone", validators=[
        DataRequired(),
        Regexp(r'^(?:\+241)?\s?\d{8}$', message="Numéro Gabonais invalide")
    ], render_kw={"placeholder": "+241 0X XX XX XX"})

    quartier = SelectField("Quartier", choices=[
        ("akebe", "Akébé"),
        ("lalala", "Lalala"),
        ("owendo", "Owendo"),
        ("glass", "Glass"),
        ("nzeng_ayong", "Nzeng-Ayong"),
        ("alibandeng", "Alibandeng"),
        ("charbonnages", "Charbonnages"),
        ("bel_air", "Bel-Air"),
        ("mtb", "Montagne Sainte"),
        ("pk5", "PK5"),
    ], validators=[DataRequired()])

    city = StringField("Ville", default="Libreville", validators=[DataRequired()])

    job_primary_id = SelectField("Travail principal", coerce=int, validators=[DataRequired()])
    job_secondary_id = SelectField("Travail secondaire (optionnel)", coerce=int, validators=[Optional()])

    experience_years = IntegerField("Années d'expérience", validators=[DataRequired()])
    salary_per_job = IntegerField("Salaire par tâche (FCFA)", validators=[
        Optional(), NumberRange(min=0)
    ], render_kw={"placeholder": "ex: 10 000"})

    bio = TextAreaField("Bio", validators=[DataRequired()])

    profile_picture = FileField("Photo de profil", validators=[
        Optional(), FileAllowed(['jpg', 'png', 'jpeg'], 'Formats autorisés: .jpg, .png, .jpeg')
    ])
    id_document = FileField("Document d'identité", validators=[
        Optional(), FileAllowed(['pdf', 'jpg', 'png'], 'Formats autorisés: .pdf, .jpg, .png')
    ])

    source = SelectField("Comment avez-vous connu ServiceHub ?", choices=[
        ("facebook", "Facebook"),
        ("tiktok", "TikTok"),
        ("instagram", "Instagram"),
        ("word_of_mouth", "Bouche à oreille"),
        ("autre", "Autre"),
    ], validators=[Optional()])

    submit = SubmitField("S'inscrire")

# -----------------------
# Requester Registration Form
# -----------------------
class RequesterForm(FlaskForm):
    first_name = StringField("Prénom", validators=[DataRequired()])
    last_name = StringField("Nom", validators=[DataRequired()])

    phone = StringField("Téléphone", validators=[
        DataRequired(),
        Regexp(r'^(?:\+241)?\s?\d{8}$', message="Numéro Gabonais invalide")
    ], render_kw={"placeholder": "+241 0X XX XX XX"})

    source = SelectField("Comment avez-vous connu ServiceHub ?", choices=[
        ("facebook", "Facebook"),
        ("tiktok", "TikTok"),
        ("instagram", "Instagram"),
        ("word_of_mouth", "Bouche à oreille"),
        ("autre", "Autre"),
    ], validators=[DataRequired()])

    regular_services = SelectMultipleField("Services réguliers", choices=[], validators=[Optional()],
                                           option_widget=CheckboxInput(), widget=ListWidget(prefix_label=False))
    
    submit = SubmitField("S'inscrire")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.regular_services.choices = get_service_choices()

# -----------------------
# Service Type (Admin)
# -----------------------
class ServiceTypeForm(FlaskForm):
    name = StringField("Nom du service", validators=[DataRequired()])
    submit = SubmitField("Ajouter")

# -----------------------
# Job Creation / Assignment (Admin)
# -----------------------
class JobForm(FlaskForm):
    requester_id = SelectField("Demandeur", coerce=int, validators=[DataRequired()])
    worker_id = SelectField("Travailleur assigné", coerce=int, validators=[Optional()])
    service_needed_id = SelectField("Service demandé", coerce=int, validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    repeated = BooleanField("Tâche récurrente")
    submit = SubmitField("Créer la tâche")

# -----------------------
# Job Completion (Admin)
# -----------------------
class JobCompletionForm(FlaskForm):
    job_id = HiddenField("ID de la tâche")
    rating = IntegerField("Note (1–5)", validators=[DataRequired(), NumberRange(min=1, max=5)])
    review = TextAreaField("Commentaire", validators=[Optional()])
    submit = SubmitField("Clôturer la tâche")

# -----------------------
# Requester Rating Form (Optional future)
# -----------------------
class RequesterRatingForm(FlaskForm):
    job_id = HiddenField("ID de la tâche")
    rating = IntegerField("Note (1–5)", validators=[DataRequired(), NumberRange(min=1, max=5)])
    review = TextAreaField("Commentaire", validators=[Optional()])
    submit = SubmitField("Envoyer mon avis")

# -----------------------
# Update Forms
# -----------------------
class UpdateWorkerForm(FlaskForm):
    zone = StringField("Zone", validators=[DataRequired()])
    city = StringField("Ville", validators=[Optional()])
    experience_years = IntegerField("Expérience", validators=[Optional()])
    job_primary_id = SelectField("Travail principal", coerce=int, validators=[DataRequired()])
    job_secondary_id = SelectField("Travail secondaire", coerce=int, validators=[Optional()])
    salary_per_job = IntegerField("Salaire", validators=[Optional()])
    bio = TextAreaField("Bio", validators=[Optional()])
    phone = StringField("Téléphone", validators=[Optional()])
    submit = SubmitField("Mettre à jour")

class UpdateRequesterForm(FlaskForm):
    phone = StringField("Téléphone", validators=[Optional()])
    regular_services = MultiCheckboxField("Services réguliers", choices=[], validators=[Optional()])
    submit = SubmitField("Mettre à jour")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.regular_services.choices = get_service_choices()

class UpdateJobForm(FlaskForm):
    description = TextAreaField("Description", validators=[DataRequired()])
    repeated = BooleanField("Tâche récurrente")
    submit = SubmitField("Mettre à jour")

# -----------------------
# Login Form (NEW)
# -----------------------
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Mot de passe", validators=[DataRequired()])
    submit = SubmitField("Connexion")

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField("Envoyer le lien de réinitialisation")

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Nouveau mot de passe', validators=[DataRequired()])
    confirm = PasswordField('Confirmer le mot de passe', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Réinitialiser le mot de passe")

from wtforms import PasswordField
from wtforms.validators import Length, EqualTo

class UserCredentialForm(FlaskForm):
    username = StringField("Nom d'utilisateur", validators=[DataRequired()])
    password = PasswordField("Mot de passe", validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField("Confirmer le mot de passe", validators=[DataRequired(), EqualTo('password', message='Les mots de passe doivent correspondre.')])
    submit = SubmitField("Continuer")
