# ---------------------
# 🔧 Imports & Constants
# ---------------------

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import (
    StringField, TextAreaField, IntegerField, SelectField, SubmitField,
    BooleanField, FileField, PasswordField, HiddenField, SelectMultipleField, DateField
)
from wtforms.validators import (
    DataRequired, Email, Optional, NumberRange, EqualTo,
    ValidationError, Regexp
)
from wtforms.widgets import ListWidget, CheckboxInput, Select
from app.models import ServiceType, User
from wtforms.fields import DateTimeLocalField


ZONES = [
    ("akebe", "Akébé"), ("lalala", "Lalala"), ("owendo", "Owendo"),
    ("glass", "Glass"), ("nzeng_ayong", "Nzeng-Ayong"), ("alibandeng", "Alibandeng"),
    ("charbonnages", "Charbonnages"), ("bel_air", "Bel-Air"),
    ("mtb", "Montagne Sainte"), ("pk5", "PK5")
]

COUNTRY_CODES = [
    ("+241", "+241 (Gabon)"),
    ("+33", "+33 (France)"),
    ("+225", "+225 (Côte d'Ivoire)"),
    ("+237", "+237 (Cameroun)"),
    ("+1", "+1 (USA/Canada)"),
]

def get_service_choices():
    return [(s.id, s.name) for s in ServiceType.query.order_by(ServiceType.name).all()]

class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

# ---------------------
# 👤 User Credentials
# ---------------------

class UserCredentialsForm(FlaskForm):
    username = StringField("Nom d'utilisateur", validators=[DataRequired()])
    email = StringField("Email (facultatif)", validators=[Optional(), Email()])
    dob = DateField("Date de naissance", format='%Y-%m-%d', validators=[DataRequired()])
    password = PasswordField("Mot de passe", validators=[DataRequired()])
    confirm_password = PasswordField("Confirmer le mot de passe", validators=[
        DataRequired(), EqualTo('password')
    ])
    submit = SubmitField("S'inscrire")

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError("Ce nom d'utilisateur est déjà pris.")

# ---------------------
# 🙋 Requester Forms
# ---------------------

class RequesterForm(FlaskForm):
    first_name = StringField("Prénom", validators=[DataRequired()])
    last_name = StringField("Nom", validators=[DataRequired()])
    email = StringField("Email (facultatif)", validators=[Optional(), Email()])

    country_code = SelectField("Indicatif", choices=COUNTRY_CODES, validators=[DataRequired()])
    phone_number = StringField("Téléphone", validators=[
        DataRequired(),
        Regexp(r'^\d{8}$', message="Entrez un numéro à 8 chiffres.")
    ], render_kw={"placeholder": "0X XX XX XX"})

    source = SelectField("Comment avez-vous connu ServiceHub ?", choices=[
        ("facebook", "Facebook"), ("tiktok", "TikTok"), ("instagram", "Instagram"),
        ("word_of_mouth", "Bouche à oreille"), ("autre", "Autre")
    ], validators=[DataRequired()])

    regular_services = MultiCheckboxField("Services réguliers", coerce=int, choices=[], validators=[Optional()])
    submit = SubmitField("Enregistrer")

    def __init__(self, *args, is_admin=False, is_update=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.regular_services.choices = get_service_choices()

class RequesterProfileUpdateForm(FlaskForm):
    first_name = StringField("Prénom", validators=[DataRequired()])
    last_name = StringField("Nom", validators=[DataRequired()])
    email = StringField("Email (facultatif)", validators=[Optional(), Email()])

    country_code = SelectField("Indicatif", choices=COUNTRY_CODES, validators=[DataRequired()])
    phone_number = StringField("Téléphone", validators=[
        DataRequired(),
        Regexp(r'^\d{8}$', message="Entrez un numéro à 8 chiffres.")
    ], render_kw={"placeholder": "0X XX XX XX"})

    source = SelectField("Comment avez-vous connu ServiceHub ?", choices=[
        ("facebook", "Facebook"), ("tiktok", "TikTok"), ("instagram", "Instagram"),
        ("word_of_mouth", "Bouche à oreille"), ("autre", "Autre")
    ], validators=[Optional()])

    regular_services = MultiCheckboxField("Services réguliers", choices=[], validators=[Optional()])
    submit = SubmitField("Mettre à jour")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.regular_services.choices = get_service_choices()

# ---------------------
# 🛠️ Worker Forms
# ---------------------

class WorkerForm(FlaskForm):
    first_name = StringField("Prénom", validators=[DataRequired()])
    last_name = StringField("Nom", validators=[DataRequired()])
    email = StringField("Email (facultatif)", validators=[Optional(), Email()])

    country_code = SelectField("Indicatif", choices=COUNTRY_CODES, validators=[DataRequired()])
    phone_number = StringField("Téléphone", validators=[
        DataRequired(),
        Regexp(r'^\d{8}$', message="Entrez un numéro à 8 chiffres.")
    ], render_kw={"placeholder": "0X XX XX XX"})

    zone = SelectField("Quartier", choices=ZONES, validators=[DataRequired()])
    city = StringField("Ville", default="Libreville", validators=[DataRequired()])

    job_primary_id = SelectField("Travail principal", coerce=int, validators=[DataRequired()])
    job_secondary_id = SelectField("Travail secondaire (optionnel)", coerce=int, validators=[Optional()])
    experience_years = IntegerField("Années d'expérience", validators=[DataRequired()])
    salary_per_job = IntegerField("Salaire par tâche (FCFA)", validators=[
        Optional(), NumberRange(min=0)
    ], render_kw={"placeholder": "ex: 10 000"})

    bio = TextAreaField("Bio", validators=[DataRequired()])
    profile_picture = FileField("Photo de profil", validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'])])
    id_document = FileField("Document d'identité", validators=[Optional(), FileAllowed(['pdf', 'jpg', 'png'])])

    source = SelectField("Comment avez-vous connu ServiceHub ?", choices=[
        ("facebook", "Facebook"), ("tiktok", "TikTok"), ("instagram", "Instagram"),
        ("word_of_mouth", "Bouche à oreille"), ("autre", "Autre")
    ], validators=[Optional()])

    submit = SubmitField("Enregistrer")

    def __init__(self, *args, is_admin=False, is_update=False, **kwargs):
        super().__init__(*args, **kwargs)
        if is_admin or is_update:
            self.profile_picture.validators = [Optional()]
            self.id_document.validators = [Optional()]

class WorkerProfileUpdateForm(FlaskForm):
    first_name = StringField("Prénom", validators=[DataRequired()])
    last_name = StringField("Nom", validators=[DataRequired()])
    email = StringField("Email (facultatif)", validators=[Optional(), Email()])

    country_code = SelectField("Indicatif", choices=COUNTRY_CODES, validators=[DataRequired()])
    phone_number = StringField("Téléphone", validators=[
        DataRequired(),
        Regexp(r'^\d{8}$', message="Entrez un numéro à 8 chiffres.")
    ], render_kw={"placeholder": "0X XX XX XX"})

    zone = SelectField("Quartier", choices=ZONES, validators=[DataRequired()])
    city = StringField("Ville", default="Libreville", validators=[DataRequired()])

    job_primary_id = SelectField("Travail principal", coerce=int, validators=[DataRequired()])
    job_secondary_id = SelectField("Travail secondaire (optionnel)", coerce=int, validators=[Optional()])
    experience_years = IntegerField("Années d'expérience", validators=[DataRequired()])
    salary_per_job = IntegerField("Salaire par tâche (FCFA)", validators=[Optional()])
    bio = TextAreaField("Bio", validators=[DataRequired()])

    submit = SubmitField("Mettre à jour")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

# ---------------------
# 📋 Job & Completion Forms
# ---------------------

class JobForm(FlaskForm):
    requester_id = SelectField("Demandeur", coerce=int, validators=[DataRequired()])
    worker_id = SelectField("Travailleur assigné", coerce=int, validators=[Optional()])
    service_needed_id = SelectField("Service demandé", coerce=int, validators=[DataRequired()])
    zone = SelectField("Zone (optionnelle pour filtrage)", choices=[("", "— Indifférent —")] + ZONES, validators=[Optional()])
    date_needed = DateTimeLocalField("Date et heure", format="%Y-%m-%dT%H:%M", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    payment_amount = IntegerField(
        "Montant à payer (en FCFA)",
        validators=[DataRequired(message="Le montant est requis."), NumberRange(min=1)],
        render_kw={"placeholder": "ex: 10 000"}
    )

    repeated = BooleanField("Tâche récurrente")
    recurrence_pattern = SelectField("Fréquence", choices=[
        ("daily", "Quotidien"),
        ("weekly", "Hebdomadaire"),
        ("monthly", "Mensuel")
    ], validators=[Optional()])

    # ✅ Add this here
    parent_job_id = HiddenField()


    submit = SubmitField("Enregistrer la tâche")

    # ✅ Custom validator
    def validate_recurrence_pattern(self, field):
        if self.repeated.data and not field.data:
            raise ValidationError("La fréquence est requise pour une tâche récurrente.")


class JobCompletionForm(FlaskForm):
    job_id = HiddenField("ID de la tâche")
    rating = IntegerField("Note (1–5)", validators=[DataRequired(), NumberRange(min=1, max=5)])
    review = TextAreaField("Commentaire", validators=[Optional()])
    submit = SubmitField("Clôturer la tâche")

class RequesterRatingForm(FlaskForm):
    job_id = HiddenField("ID de la tâche")
    rating = IntegerField("Note (1–5)", validators=[DataRequired(), NumberRange(min=1, max=5)])
    review = TextAreaField("Commentaire", validators=[Optional()])
    submit = SubmitField("Envoyer mon avis")

# ---------------------
# 🔐 Auth & Password Reset
# ---------------------

class LoginForm(FlaskForm):
    identifier = StringField("Nom d'utilisateur ou Email", validators=[DataRequired()])
    password = PasswordField("Mot de passe", validators=[DataRequired()])
    submit = SubmitField("Connexion")

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField("Envoyer le lien de réinitialisation")

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Nouveau mot de passe', validators=[DataRequired()])
    confirm = PasswordField('Confirmer le mot de passe', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Réinitialiser le mot de passe")

# ---------------------
# 🧰 Admin – Service Type Management
# ---------------------

class ServiceTypeForm(FlaskForm):
    name = StringField("Nom du service", validators=[DataRequired()])
    submit = SubmitField("Ajouter")

