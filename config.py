import os

# ---------------------
# Database Configuration
# ---------------------
SQLALCHEMY_DATABASE_URI = 'postgresql://lsimaess:Essamvous66@servicehub-db.c5m0u8ug4rvu.us-east-2.rds.amazonaws.com:5432/servicehub'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# ---------------------
# Secret Key
# ---------------------
SECRET_KEY = os.environ.get("SECRET_KEY", "test-secret-key-change-this")

# ---------------------
# Flask-Mail Configuration
# ---------------------
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')
