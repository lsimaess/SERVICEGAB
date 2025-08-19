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
    username = db.Column(db.String(100), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    dob = db.Column(db.Date, nullable=False)
    password_hash = db.Column(db.String(400), nullable=False)

    is_admin = db.Column(db.Boolean, default=False)
    role_worker = db.Column(db.Boolean, default=False)
    role_requester = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    worker = db.relationship("Worker", uselist=False, backref="user")
    requester = db.relationship("Requester", uselist=False, backref="user")

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
    country_code = db.Column(db.String(6), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=True)
    id_document = db.Column(db.String(200), nullable=True)
    salary_per_job = db.Column(db.Integer)

    status = db.Column(db.String(50), default=Status.PENDING)
    notes = db.Column(db.Text)
    source = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    avg_rating = db.Column(db.Float, default=0.0)
    rating_count = db.Column(db.Integer, default=0)

    jobs = db.relationship('Job', backref='worker', lazy=True)

    def get_average_rating(self):
        return self.avg_rating if self.rating_count > 0 else None

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

    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    country_code = db.Column(db.String(6), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
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
    date_needed = db.Column(db.DateTime, nullable=False)

    status = db.Column(db.String(50), default=Status.PENDING)

    assigned_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    rating = db.Column(db.Integer)
    review = db.Column(db.Text)
    notes = db.Column(db.Text)
    cancel_reason = db.Column(db.Text)

    is_active = db.Column(db.Boolean, default=True)

    repeated = db.Column(db.Boolean, default=False)
    recurrence_pattern = db.Column(db.String(50))
    parent_job_id = db.Column(db.Integer, db.ForeignKey('job.id'))
    parent_job = db.relationship('Job', remote_side=[id], backref='child_jobs')

    zone = db.Column(db.String(64), nullable=False)
    created_by_admin = db.Column(db.Boolean, default=False)
    payment_amount = db.Column(db.Integer, nullable=True)


    def assign(self, worker):
        self.worker_id = worker.id
        self.status = Status.ASSIGNED
        self.assigned_at = datetime.utcnow()

    def complete(self, rating=None, review=None):
        self.status = Status.COMPLETED
        self.completed_at = datetime.utcnow()
        self.rating = rating
        self.review = review

# ---------------------
# Job Recurrence Change Log
# ---------------------
class JobRecurrenceChangeLog(db.Model):
    __tablename__ = 'job_recurrence_change_log'
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    changed_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    fields_changed = db.Column(db.Text)
    affected_jobs = db.Column(db.Integer)

    job = db.relationship('Job', backref='recurrence_logs')
    user = db.relationship('User', backref='recurrence_logs')
