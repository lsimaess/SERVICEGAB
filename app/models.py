from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from sqlalchemy.dialects.postgresql import JSON

# ---------------------
# Status Constants
# ---------------------
class Status:
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    ASSIGNED = 'assigned'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

# ---------------------
# Association Table for Job Services
# ---------------------
job_service_used = db.Table(
    'job_service_used',
    db.Column('job_id', db.Integer, db.ForeignKey('job.id')),
    db.Column('service_type_id', db.Integer, db.ForeignKey('service_type.id'))
)

# ---------------------
# Service Type Model
# ---------------------
class ServiceType(db.Model):
    __tablename__ = 'service_type'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f"<ServiceType {self.name}>"

# ---------------------
# User Model
# ---------------------
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(400), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"

# ---------------------
# Worker Model
# ---------------------
class Worker(db.Model):
    __tablename__ = 'worker'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('worker', uselist=False))

    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    job_primary_id = db.Column(db.Integer, db.ForeignKey('service_type.id'), nullable=False)
    job_secondary_id = db.Column(db.Integer, db.ForeignKey('service_type.id'))

    job_primary = db.relationship('ServiceType', foreign_keys=[job_primary_id], backref='primary_workers')
    job_secondary = db.relationship('ServiceType', foreign_keys=[job_secondary_id], backref='secondary_workers')

    zone = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), default='Libreville')
    experience_years = db.Column(db.Integer, nullable=False)
    bio = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    profile_picture = db.Column(db.String(200), nullable=False)
    id_document = db.Column(db.String(200), nullable=False)
    salary_per_job = db.Column(db.Integer)

    status = db.Column(db.String(50), default=Status.PENDING)
    notes = db.Column(db.Text)
    source = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    avg_rating = db.Column(db.Float, default=0.0)
    rating_count = db.Column(db.Integer, default=0)

    jobs = db.relationship('Job', backref='worker', lazy=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

# ---------------------
# Requester Model
# ---------------------
class Requester(db.Model):
    __tablename__ = 'requester'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('requester', uselist=False))

    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    source = db.Column(db.String(100))
    status = db.Column(db.String(50), default=Status.PENDING)
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    regular_services = db.Column(JSON)

    jobs = db.relationship('Job', backref='requester', lazy=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

# ---------------------
# Job Model
# ---------------------
class Job(db.Model):
    __tablename__ = 'job'
    id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(db.Integer, db.ForeignKey('requester.id'), nullable=False)
    worker_id = db.Column(db.Integer, db.ForeignKey('worker.id'))

    service_needed_id = db.Column(db.Integer, db.ForeignKey('service_type.id'), nullable=False)
    service_needed = db.relationship('ServiceType', foreign_keys=[service_needed_id], backref='jobs_requested')

    services_used = db.relationship('ServiceType', secondary=job_service_used, backref='jobs_fulfilled')

    description = db.Column(db.Text, nullable=False)
    scheduled_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), default=Status.PENDING)

    assigned_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)

    rating = db.Column(db.Integer)
    review = db.Column(db.Text)
    notes = db.Column(db.Text)

    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    repeated = db.Column(db.Boolean, default=False)

    def assign(self, worker):
        self.worker_id = worker.id
        self.status = Status.ASSIGNED
        self.assigned_at = datetime.utcnow()

    def complete(self, rating=None, review=None):
        self.status = Status.COMPLETED
        self.completed_at = datetime.utcnow()
        self.rating = rating
        self.review = review
