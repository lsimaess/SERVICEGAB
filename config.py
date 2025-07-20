import os
SQLALCHEMY_DATABASE_URI = 'postgresql://lsimaess:Essamvous66@servicehub-db.c5m0u8ug4rvu.us-east-2.rds.amazonaws.com:5432/servicehub' 
SQLALCHEMY_TRACK_MODIFICATIONS = False
# ---------------------
# Secret Key
# ---------------------
SECRET_KEY = os.environ.get("SECRET_KEY", "test-secret-key-change-this")
