import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_login import LoginManager
from dotenv import load_dotenv

load_dotenv()  # ✅ Load env vars

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
login_manager = LoginManager()  # ✅ Add this line

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    Bootstrap(app)
    mail.init_app(app)
    login_manager.init_app(app)  # ✅ Set up login manager
    login_manager.login_view = 'auth.login'  # Redirect to login if @login_required

    # Import models and register user loader
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Import blueprints
    from app.admin.routes import admin_bp
    from app.worker.routes import worker_bp
    from app.requester.routes import requester_bp
    from app.main.routes import main_bp
    from app.auth.routes import auth_bp

    # Register blueprints
    app.register_blueprint(admin_bp)
    app.register_blueprint(worker_bp)
    app.register_blueprint(requester_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    return app
