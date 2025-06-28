import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect
from app.extensions import db, oauth
from app.auth import auth_bp
from app.routes import main_bp
from app.redis_test import redis_test  # Blueprint voor Redis-test
from .config import Config
from flask_session import Session
import redis


csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def inject_user():
    return dict(current_user=current_user)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    # Sessions via Redis
    app.config['SESSION_TYPE'] = 'redis'
    redis_url = os.environ.get('REDIS_URL')
    if not redis_url:
        raise Exception("REDIS_URL not found in environment variables!")

    app.config['SESSION_REDIS'] = redis.from_url(redis_url)
    app.config['SESSION_COOKIE_NAME'] = 'noxco_session'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SECURE'] = False  # HTTPS? → True!
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Of 'None' bij Auth0/HTTPS
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600

    Session(app)

    # Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(redis_test)

    # Database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    db.init_app(app)
    Migrate(app, db)

    # OAuth
    oauth.init_app(app)
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

    # CSRF en login
    login_manager.init_app(app)
    csrf.init_app(app)
    app.context_processor(inject_user)

    # <<<<< Belangrijk: pas hier na de app-setup de modellen importeren! >>>>>
    from app.models import Gebruiker

    # User loader registreer je na de import
    @login_manager.user_loader
    def load_user(user_id):
        return Gebruiker.query.get(int(user_id))

    # Logging instellen
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/flask.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Noxco startup')

    return app
