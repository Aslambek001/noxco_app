from flask import Blueprint, redirect, url_for, session, flash, current_app, request
from .extensions import oauth, db
from .models import Gebruiker
from flask_login import login_user, logout_user, current_user

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/')
def auth_index():
    return redirect(url_for('auth.login'))

@auth_bp.route('/login')
def login():
    # Sla de 'next' URL op als die bestaat, zodat Flask-Login correct kan doorsturen na login
    next_url = request.args.get('next')
    if next_url:
        session['next_url'] = next_url
    return oauth.auth0.authorize_redirect(redirect_uri=current_app.config['AUTH0_CALLBACK_URL'])

@auth_bp.route('/callback')
def callback():
    try:
        # Haal het toegangstoken op uit Auth0's antwoord
        token = oauth.auth0.authorize_access_token()
        # Haal de gebruikersinformatie op met het token
        userinfo = oauth.auth0.userinfo()

        auth0_id = userinfo['sub']
        user = Gebruiker.query.filter_by(auth0_user_id=auth0_id).first()

        # Als de gebruiker nog niet bestaat in onze database, creëer dan een nieuw Gebruiker-object
        if not user:
            base_username = userinfo.get('nickname') or userinfo.get('name') or userinfo.get('email', 'gebruiker').split('@')[0]
            username = base_username
            counter = 1
            # Zorg voor een unieke gebruikersnaam
            while Gebruiker.query.filter_by(username=username).first():
                username = f"{base_username}{counter}"
                counter += 1

            user = Gebruiker(
                username=username,
                email=userinfo.get('email'),
                profile_picture_url=userinfo.get('picture'),
                auth0_user_id=auth0_id,
                full_name=userinfo.get('name'), # Voeg full_name toe als beschikbaar
                bio="Welkom bij NOXCO!" # Standaard bio
            )
            db.session.add(user)
            db.session.commit()
            flash('Welkom bij NOXCO! Je account is aangemaakt.', 'success')
        else:
            flash(f'Welkom terug, {user.username}!', 'info')

        # Deze regel is cruciaal voor Flask-Login.
        # Roep login_user aan met het Gebruiker-object.
        # Dit markeert de gebruiker als ingelogd bij Flask-Login.
        login_user(user)

        # Opslaan van Auth0 userinfo in de sessie (optioneel, maar kan nuttig zijn voor specifieke Auth0 data)
        session['user'] = userinfo

        # Redirect naar de 'next' URL als die bestaat, anders naar home
        next_url = session.pop('next_url', None) or url_for('main.home')
        return redirect(next_url)

    except Exception as e:
        flash(f'Fout bij login: {type(e).__name__}: {e}', 'danger')
        current_app.logger.error(f"Auth0 callback error: {e}", exc_info=True)
        return redirect(url_for('main.home'))

@auth_bp.route('/logout')
def logout():
    logout_user() # Roep Flask-Login's logout_user aan om de gebruiker uit te loggen
    session.clear() # Ruim de hele sessie op, inclusief Auth0 data

    # Vorm de Auth0 logout URL
    params = {
        'returnTo': current_app.config['AUTH0_LOGOUT_URL'],
        'client_id': current_app.config['AUTH0_CLIENT_ID']
    }

    logout_url = f"https://{current_app.config['AUTH0_DOMAIN']}/v2/logout?" + '&'.join([f'{k}={v}' for k, v in params.items()])
    return redirect(logout_url)