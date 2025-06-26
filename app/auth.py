from flask import Blueprint, redirect, url_for, session, flash, current_app, request
from .extensions import oauth, db
from .models import Gebruiker
from flask_login import login_user, logout_user

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/')
def auth_index():
    return redirect(url_for('auth.login'))

@auth_bp.route('/login')
def login():
    next_url = request.args.get('next')
    if next_url:
        session['next_url'] = next_url
    return oauth.auth0.authorize_redirect(redirect_uri=current_app.config['AUTH0_CALLBACK_URL'])

@auth_bp.route('/callback')
def callback():
    try:
        token = oauth.auth0.authorize_access_token()
        print(token)
        userinfo = oauth.auth0.userinfo()

        auth0_id = userinfo.get('sub')
        email = userinfo.get('email')

        if not auth0_id or not email:
            flash("Login mislukt: geen geldige gebruikersinformatie ontvangen.", "danger")
            return redirect(url_for('main.home'))

        user = Gebruiker.query.filter(
            (Gebruiker.auth0_user_id == auth0_id) | (Gebruiker.email == email)
        ).first()

        if not user:
            base_username = userinfo.get('nickname') or userinfo.get('name') or email.split('@')[0]
            username = base_username
            counter = 1
            while Gebruiker.query.filter_by(username=username).first():
                username = f"{base_username}{counter}"
                counter += 1

            user = Gebruiker(
                username=username,
                email=email,
                profile_picture_url=userinfo.get('picture'),
                auth0_user_id=auth0_id,
                full_name=userinfo.get('name'),
                bio="Welkom bij NOXCO!"
            )
            db.session.add(user)
            db.session.commit()
            flash("Welkom bij NOXCO! Je account is aangemaakt.", "success")
        else:
            # Если auth0_user_id ещё не был сохранён, обновим его
            if not user.auth0_user_id:
                user.auth0_user_id = auth0_id
                db.session.commit()
            flash(f"Welkom terug, {user.username}!", "info")

        login_user(user)
        session['user'] = userinfo

        next_url = session.pop('next_url', None) or url_for('main.home')
        return redirect(next_url)

    except Exception as e:
        flash(f"Login fout: {type(e).__name__}: {e}", "danger")
        current_app.logger.error(f"Auth0 callback error: {e}", exc_info=True)
        return redirect(url_for('main.home'))

@auth_bp.route('/logout')
def logout():
    logout_user()
    session.clear()
    params = {
        'returnTo': current_app.config['AUTH0_LOGOUT_URL'],
        'client_id': current_app.config['AUTH0_CLIENT_ID']
    }
    logout_url = f"https://{current_app.config['AUTH0_DOMAIN']}/v2/logout?" + '&'.join([f'{k}={v}' for k, v in params.items()])
    return redirect(logout_url)
