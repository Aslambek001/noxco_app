# app/models.py
from app.extensions import db
from flask_login import UserMixin
from datetime import datetime


class Gebruiker(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    profile_picture_url = db.Column(db.String(200), nullable=True)
    auth0_user_id = db.Column(db.String(100), unique=True, nullable=False)

    # Optionele velden die je in profile.html gebruikt
    full_name = db.Column(db.String(100), nullable=True)
    bio = db.Column(db.Text, nullable=True)

    # --- NIEUW VELD: Is het account privé? ---
    # Gewijzigd: server_default toegevoegd voor correcte migratie op een bestaande tabel
    is_private = db.Column(db.Boolean, default=False, nullable=False, server_default=db.text('FALSE'))

    # --- RELATIES VOOR VOLGSYSTEEM ---
    followers = db.relationship(
        'Follow', foreign_keys='Follow.followed_id',
        backref='followed', lazy='dynamic', cascade='all, delete-orphan'
    )
    following = db.relationship(
        'Follow', foreign_keys='Follow.follower_id',
        backref='follower', lazy='dynamic', cascade='all, delete-orphan'
    )

    # --- NIEUWE RELATIES VOOR LIKES EN COMMENTAREN (voor Gebruiker) ---
    comments_made = db.relationship('Comment', backref='author', lazy='dynamic') # Gebruiker is auteur van commentaar
    likes_given = db.relationship('Like', backref='user', lazy='dynamic') # Gebruiker is auteur van like

    def __repr__(self):
        return f"Gebruiker('{self.username}', '{self.email}', 'Privé: {self.is_private}')"

    # --- METHODEN VOOR HET BEHEER VAN VOLGERS ---
    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)
            return True
        return False

    def unfollow(self, user):
        f = self.following.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)
            return True
        return False

    def is_following(self, user):
        if user.id is None: # Bescherming tegen pogingen om een niet-bestaande gebruiker te volgen
            return False
        return self.following.filter_by(followed_id=user.id).first() is not None

    # Extra methoden voor gemak met likes
    def has_liked_model(self, stl_model):
        if stl_model.id is None: # Bescherming tegen pogingen om een niet-bestaand model te liken
            return False
        return self.likes_given.filter_by(model_id=stl_model.id).first() is not None


# --- MODEL: Voor het opslaan van volgrelaties ---
class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('gebruiker.id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('gebruiker.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Zorgt ervoor dat een gebruiker niet dezelfde persoon meer dan één keer kan volgen
    __table_args__ = (db.UniqueConstraint('follower_id', 'followed_id', name='_follower_followed_uc'),)

    def __repr__(self):
        return f'<Volgen {self.follower_id} volgt {self.followed_id}>'


class STLModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.String(120), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    location = db.Column(db.String(100), nullable=True)
    tags = db.Column(db.String(200), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('gebruiker.id'), nullable=False)

    # Relatie naar Gebruiker: elke STLModel behoort tot één Gebruiker
    user = db.relationship('Gebruiker', backref='posts', lazy=True) # backref 'posts' voor gemak

    # --- NIEUWE RELATIES VOOR LIKES EN COMMENTAREN (voor STLModel) ---
    likes_received = db.relationship('Like', backref='model', lazy='dynamic', cascade='all, delete-orphan') # Likes die de model heeft ontvangen
    comments = db.relationship('Comment', backref='model', lazy='dynamic', cascade='all, delete-orphan') # Commentaren op de model

    def __repr__(self):
        return f"STLModel('{self.title}', '{self.date_posted}')"

# --- NIEUWE MODELLEN: Like en Commentaar ---
class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('gebruiker.id'), nullable=False)
    model_id = db.Column(db.Integer, db.ForeignKey('stl_model.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Uniciteit: één gebruiker kan één model slechts één keer liken
    __table_args__ = (db.UniqueConstraint('user_id', 'model_id', name='_user_model_like_uc'),)

    def __repr__(self):
        return f'<Like Gebruiker {self.user_id} op Model {self.model_id}>'

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('gebruiker.id'), nullable=False)
    model_id = db.Column(db.Integer, db.ForeignKey('stl_model.id'), nullable=False)

    def __repr__(self):
        return f'<Commentaar {self.id} door Gebruiker {self.user_id} op Model {self.model_id}>'