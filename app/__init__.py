import os
import logging
from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect

from .config import Config
from .extensions import db, oauth
from .auth import auth_bp
from .routes import main_bp
from app.models import Gebruiker

# Initialiseer CSRFProtect globaal
csrf = CSRFProtect()

# Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return Gebruiker.query.get(int(user_id))

def inject_user():
    return dict(current_user=current_user)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    print(f"DEBUG (__init__.py): app.config['SQLALCHEMY_DATABASE_URI']: {app.config.get('SQLALCHEMY_DATABASE_URI')}")

    db.init_app(app)
    oauth.init_app(app)
    Migrate(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    app.context_processor(inject_user)

    oauth.register(
        name='auth0',
        client_id=app.config['AUTH0_CLIENT_ID'],
        client_secret=app.config['AUTH0_CLIENT_SECRET'],
        server_metadata_url=f"https://{app.config['AUTH0_DOMAIN']}/.well-known/openid-configuration",
        client_kwargs={
            'scope': 'openid profile email',
            'token_endpoint_auth_method': 'client_secret_post'
        }
    )

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    from . import models  # noqa: F401

    logging.basicConfig()
    logging.getLogger('authlib').setLevel(logging.DEBUG)
    logging.getLogger('urllib3').setLevel(logging.DEBUG)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    return app