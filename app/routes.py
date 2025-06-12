# app/routes.py
from flask import Blueprint, render_template, session, redirect, url_for, flash, request, current_app, \
    send_from_directory, jsonify
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.utils import secure_filename
import os
from datetime import datetime

from .models import STLModel, Gebruiker, Follow, Like, Comment
from .extensions import db

main_bp = Blueprint('main', __name__)

# --- GLOBALE PADDEFINITIES VERWIJDERD (Nu in app.config in __init__.py) ---
# PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
# UPLOAD_FOLDER_PATH = os.path.join(PROJECT_ROOT, 'uploads', 'stl_models')
# if not os.path.exists(UPLOAD_FOLDER_PATH):


#    os.makedirs(UPLOAD_FOLDER_PATH)
#    print(f"DEBUG: Map voor STL-modellen aangemaakt: {UPLOAD_FOLDER_PATH}")

# --- GLOBALE SETS VOOR TOEGESTAANE EXTENSIES BEHOUDEN ---
ALLOWED_STL_EXTENSIONS = {'stl'}
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename, allowed_extensions_set):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions_set


@main_bp.route('/')
def home():
    """
    Rendert de homepagina met de 3 meest recente STL-modellen, inclusief likes en comments tellingen.
    """
    if current_user.is_authenticated:
        followed_users_ids = [f.followed_id for f in current_user.following.all()]
        if current_user.id not in followed_users_ids:
            followed_users_ids.append(current_user.id)

        stl_models_query = STLModel.query.join(Gebruiker). \
            filter(
            (Gebruiker.is_private == False) |
            (Gebruiker.id.in_(followed_users_ids))
        ). \
            order_by(STLModel.date_posted.desc()).limit(20)
    else:
        stl_models_query = STLModel.query.join(Gebruiker). \
            filter(Gebruiker.is_private == False). \
            order_by(STLModel.date_posted.desc()).limit(20)

    models_data_for_template = []
    for model in stl_models_query.all():
        model_info = {
            'id': model.id,
            'title': model.title,
            'filename': model.filename,
            'date_posted': model.date_posted.strftime('%Y-%m-%d %H:%M'),
            'location': model.location,
            'tags': model.tags,
            'user_id': model.user_id,
            'author_username': model.user.username,
            'profile_picture_url': model.user.profile_picture_url,
            'likes_count': model.likes_received.count(),
            'comments_count': model.comments.count()
        }
        models_data_for_template.append(model_info)

    return render_template('home.html', stl_models=models_data_for_template)


@main_bp.route('/profile', defaults={'user_id': None})
@main_bp.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
    if user_id:
        user_to_view = Gebruiker.query.get_or_404(user_id)
    else:
        user_to_view = current_user

    user_models_query = STLModel.query.filter_by(user_id=user_to_view.id).order_by(STLModel.date_posted.desc())

    if user_to_view.is_private:
        if current_user.id == user_to_view.id:
            pass
        elif current_user.is_following(user_to_view):
            pass
        else:
            flash(f'Dit is een privéaccount. U moet volgen om de berichten te zien.', 'info')
            user_models_query = user_models_query.filter(False)
    else:
        pass

    user_models_data_for_template = []
    for model in user_models_query.all():
        model_info = {
            'id': model.id,
            'title': model.title,
            'filename': model.filename,
            'date_posted': model.date_posted.strftime('%Y-%m-%d %H:%M'),
            'location': model.location,
            'tags': model.tags,
            'user_id': model.user_id,
            'author_username': model.user.username,
            'profile_picture_url': model.user.profile_picture_url,
            'likes_count': model.likes_received.count(),
            'comments_count': model.comments.count()
        }
        user_models_data_for_template.append(model_info)

    is_following = False
    if current_user.is_authenticated and current_user.id != user_to_view.id:
        is_following = current_user.is_following(user_to_view)

    follower_count = user_to_view.followers.count()
    following_count = user_to_view.following.count()

    followers_list = []
    following_list = []
    if not user_to_view.is_private or \
            (current_user.is_authenticated and current_user.id == user_to_view.id) or \
            (current_user.is_authenticated and current_user.is_following(user_to_view)):
        followers_list = [f.follower for f in user_to_view.followers.all()]
        following_list = [f.followed for f in user_to_view.following.all()]

    return render_template('profile.html',
                           user=user_to_view,
                           user_models=user_models_data_for_template,
                           is_following=is_following,
                           follower_count=follower_count,
                           following_count=following_count,
                           followers_list=followers_list,
                           following_list=following_list
                           )


@main_bp.route('/upload_model', methods=['POST'])
@login_required
def upload_model():
    if request.method == 'POST':
        if 'stl_file' not in request.files:
            flash('Geen bestand geselecteerd.', 'danger')
            return redirect(url_for('main.home'))

        file = request.files['stl_file']
        title = request.form.get('title')
        location = request.form.get('location')
        tags = request.form.get('tags')

        if file.filename == '':
            flash('Geen bestand geselecteerd.', 'danger')
            return redirect(url_for('main.home'))

        if file and allowed_file(file.filename, ALLOWED_STL_EXTENSIONS):
            filename = secure_filename(file.filename)
            # GEBRUIK HET PAD VAN current_app.config
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER_STL_MODELS'], filename)

            try:
                file.save(file_path)

                new_model = STLModel(
                    title=title,
                    filename=filename,
                    date_posted=datetime.utcnow(),
                    user_id=current_user.id,
                    location=location,
                    tags=tags
                )
                db.session.add(new_model)
                db.session.commit()

                flash('Model succesvol geüpload!', 'success')
                return redirect(url_for('main.profile'))

            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Fout bij uploaden of opslaan model: {e}", exc_info=True)
                flash(f'Er is een fout opgetreden bij het uploaden: {e}', 'danger')
                return redirect(url_for('main.home'))

        else:
            flash('Alleen STL-bestanden zijn toegestaan (.stl).', 'danger')
            return redirect(url_for('main.home'))

    flash('Onjuiste aanvraagmethode voor upload.', 'danger')
    return redirect(url_for('main.home'))


@main_bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = current_user

    if request.method == 'POST':
        user.username = request.form.get('username', user.username)
        user.full_name = request.form.get('full_name', user.full_name)
        user.bio = request.form.get('bio', user.bio)
        user.email = request.form.get('email', user.email)

        if 'profile_picture' in request.files:
            profile_pic = request.files['profile_picture']
            if profile_pic.filename != '' and allowed_file(profile_pic.filename, ALLOWED_IMAGE_EXTENSIONS):
                filename_base, file_extension = os.path.splitext(secure_filename(profile_pic.filename))
                unique_filename = f"user_{user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}{file_extension}"

                # GEBRUIK HET PAD VAN current_app.config
                pic_path = os.path.join(current_app.config['UPLOAD_FOLDER_PROFILE_PICS'], unique_filename)

                try:
                    profile_pic.save(pic_path)
                    user.profile_picture_url = url_for('static', filename=f'images/profile_pics/{unique_filename}')
                    flash('Profielfoto succesvol geüpload!', 'success')
                except Exception as e:
                    current_app.logger.error(f"Fout bij opslaan profielfoto: {e}", exc_info=True)
                    flash('Fout bij het uploaden van de profielfoto.', 'danger')
            elif profile_pic.filename != '':
                flash('Ongeldig bestandstype voor profielfoto. Alleen PNG, JPG, JPEG, GIF.', 'danger')

        user.is_private = 'is_private' in request.form

        try:
            db.session.commit()
            flash('Profiel succesvol bijgewerkt!', 'success')
            return redirect(url_for('main.profile'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Fout bij bijwerken profiel: {e}", exc_info=True)
            flash(f'Fout bij bijwerken profiel: {e}', 'danger')
            return redirect(url_for('main.edit_profile'))

    return render_template('edit_profile.html', user=user)


@main_bp.route('/follow/<int:user_id>')
@login_required
def follow_user(user_id):
    user_to_follow = Gebruiker.query.get_or_404(user_id)
    if user_to_follow == current_user:
        flash('U kunt uzelf niet volgen.', 'danger')
        return redirect(url_for('main.profile', user_id=user_id))

    if current_user.is_following(user_to_follow):
        flash(f'U volgt {user_to_follow.username} al.', 'info')
        return redirect(url_for('main.profile', user_id=user_id))

    current_user.follow(user_to_follow)
    db.session.commit()
    flash(f'U volgt nu {user_to_follow.username}.', 'success')

    return redirect(url_for('main.profile', user_id=user_id))


@main_bp.route('/unfollow/<int:user_id>')
@login_required
def unfollow_user(user_id):
    user_to_unfollow = Gebruiker.query.get_or_404(user_id)
    if user_to_unfollow == current_user:
        flash('U kunt uzelf niet ontvolgen.', 'danger')
        return redirect(url_for('main.profile', user_id=user_id))

    if not current_user.is_following(user_to_unfollow):
        flash(f'U volgt {user_to_unfollow.username} niet.', 'info')
        return redirect(url_for('main.profile', user_id=user_id))

    current_user.unfollow(user_to_unfollow)
    db.session.commit()
    flash(f'U bent {user_to_unfollow.username} ontvolgd.', 'success')

    return redirect(url_for('main.profile', user_id=user_id))


# --- API ROUTES ---

@main_bp.route('/api/models/<int:model_id>/likes', methods=['GET'])
def get_likes_count_api(model_id):
    model = STLModel.query.get(model_id)
    if not model:
        return jsonify(error="Model niet gevonden"), 404

    likes_count = model.likes_received.count()

    return jsonify(likes_count=likes_count)


@main_bp.route('/api/models/<int:model_id>/like', methods=['POST'])
@login_required
def toggle_like_api(model_id):
    model = STLModel.query.get(model_id)
    if not model:
        return jsonify(error="Model niet gevonden"), 404

    existing_like = Like.query.filter_by(user_id=current_user.id, model_id=model.id).first()

    if existing_like:
        db.session.delete(existing_like)
        action = "unliked"
    else:
        new_like = Like(user_id=current_user.id, model_id=model.id)
        db.session.add(new_like)
        action = "liked"

    db.session.commit()

    likes_count = model.likes_received.count()
    return jsonify(likes_count=likes_count, action=action)


@main_bp.route('/api/models/<int:model_id>/comments', methods=['GET'])
def get_comments_api(model_id):
    model = STLModel.query.get(model_id)
    if not model:
        return jsonify(error="Model niet gevonden"), 404

    comments = Comment.query.filter_by(model_id=model.id).order_by(Comment.date_posted.asc()).all()

    comments_data = []
    for comment in comments:
        comments_data.append({
            'id': comment.id,
            'author_username': comment.author.username,
            'text': comment.text,
            'date_posted': comment.date_posted.isoformat()
        })

    return jsonify(comments=comments_data)


@main_bp.route('/api/models/<int:model_id>/comments', methods=['POST'])
@login_required
def add_comment_api(model_id):
    model = STLModel.query.get(model_id)
    if not model:
        return jsonify(error="Model niet gevonden"), 404

    data = request.get_json()
    comment_text = data.get('text')

    if not comment_text:
        return jsonify(error="Commentaartekst is vereist"), 400

    new_comment = Comment(
        text=comment_text,
        date_posted=datetime.utcnow(),
        user_id=current_user.id,
        model_id=model.id
    )

    db.session.add(new_comment)
    db.session.commit()

    return jsonify({
        'id': new_comment.id,
        'author_username': current_user.username,
        'text': new_comment.text,
        'date_posted': new_comment.date_posted.isoformat()
    }), 201


from flask_wtf.csrf import generate_csrf


@main_bp.route('/get-csrf-token', methods=['GET'])
def get_csrf_token_api():
    return jsonify({'csrf_token': generate_csrf()})


@main_bp.route('/uploads/stl_models/<path:filename>')
def serve_stl_models(filename):
    """
    Dient bestanden uit de UPLOAD_FOLDER (uploads/stl_models).
    """
    # Gebruik het pad uit current_app.config, niet een lokale variabele
    # Deze variabele moet geconfigureerd zijn in __init__.py
    full_upload_path = current_app.config['UPLOAD_FOLDER_STL_MODELS']

    print(f"DEBUG: Poging om STL-bestand te serveren: {filename} vanuit map: {full_upload_path}")

    try:
        return send_from_directory(full_upload_path, filename)
    except FileNotFoundError:
        print(f"ERROR: STL-bestand niet gevonden: {os.path.join(full_upload_path, filename)}")
        return "Bestand niet gevonden", 404
    except Exception as e:
        print(f"ERROR: Fout bij het serveren van STL-bestand: {e}")
        return "Interne serverfout", 500

@main_bp.route('/uploads/stl_models/<filename>')
def serve_stl_file(filename):
    base_path = os.path.abspath(os.path.join(current_app.root_path, '..', 'uploads', 'stl_models'))
    return send_from_directory(base_path, filename)


@main_bp.route('/search', methods=['GET'])
def search_users():
    query = request.args.get('query', '').strip()  # Haal de zoekterm uit de URL
    users = []
    if query:
        # Zoek gebruikers op gebruikersnaam of volledige naam, gebruik LIKE voor gedeeltelijke overeenkomst
        # %{query}% betekent dat de query overal in de string kan staan
        search_pattern = f"%{query}%"
        users = Gebruiker.query.filter(
            (Gebruiker.username.ilike(search_pattern)) |  # ilike voor hoofdletterongevoelige zoekopdracht
            (Gebruiker.full_name.ilike(search_pattern))
        ).all()

        # Optioneel: filter privéaccounts voor niet-geauthenticeerde gebruikers
        if not current_user.is_authenticated:
            users = [user for user in users if not user.is_private]
        # Indien nodig, voeg logica toe om privéaccounts te zien die gevolgd worden
        elif current_user.is_authenticated:
            visible_users = []
            for user_found in users:
                if not user_found.is_private or \
                        user_found.id == current_user.id or \
                        current_user.is_following(user_found):
                    visible_users.append(user_found)
            users = visible_users

    return render_template('search_results.html', query=query, users=users)