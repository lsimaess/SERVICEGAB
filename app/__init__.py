from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')

    db.init_app(app)

    # Import all models so Flask-Migrate or db.create_all can see them
    from app import models  # <-- this makes sure all models are registered

    # Register blueprints
    from app.admin.routes import admin_bp
    from app.worker.routes import worker_bp
    from app.requester.routes import requester_bp
    from app.main.routes import main_bp

    app.register_blueprint(admin_bp)
    app.register_blueprint(worker_bp)
    app.register_blueprint(requester_bp)
    app.register_blueprint(main_bp)

    return app
