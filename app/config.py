import os

# 📁 Uploadpaden voor bestanden
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
REDIS_URL = os.getenv('REDIS_URL')
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

class Config:
    # 🔐 Geheime sleutel voor applicatiebeveiliging (sessies, formulieren, etc.)
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-insecure-secret-key')  # ← bij voorkeur overschrijven in .env

    # ✅ CSRF-beveiliging
    WTF_CSRF_ENABLED = True

    # 📦 SQLAlchemy-instellingen
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True  # Toon SQL-query's in de console (handig voor debugging)

    # 🔑 Auth0-instellingen
    AUTH0_CLIENT_ID = os.getenv('AUTH0_CLIENT_ID')
    AUTH0_CLIENT_SECRET = os.getenv('AUTH0_CLIENT_SECRET')
    AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
    AUTH0_CALLBACK_URL = os.getenv('AUTH0_CALLBACK_URL', 'http://127.0.0.1:5001/auth/callback')
    AUTH0_LOGOUT_URL = os.getenv('AUTH0_LOGOUT_URL', 'http://127.0.0.1:5001/')

    # 📁 Uploadfolders
    UPLOAD_FOLDER_PROFILE_PICS = os.path.join(BASE_DIR, 'static', 'images', 'profile_pics')
    UPLOAD_FOLDER_STL_MODELS = os.path.join(BASE_DIR, 'uploads', 'stl_models')
