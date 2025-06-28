from app.extensions import db
from flask_login import UserMixin
from datetime import datetime
import json

# --- Таблица для подписок (follow) ---
class Follow(db.Model):
    __tablename__ = 'follow'
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('gebruiker.id'))
    followed_id = db.Column(db.Integer, db.ForeignKey('gebruiker.id'))
    timestamp = db.Column(db.DateTime, default=db.func.now())

# --- Главная таблица пользователя ---
class Gebruiker(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    profile_picture_url = db.Column(db.String(200), nullable=True)
    auth0_user_id = db.Column(db.String(100), unique=True, nullable=False)

    full_name = db.Column(db.String(100), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    is_private = db.Column(db.Boolean, default=False, nullable=False, server_default=db.text('FALSE'))

    # Кто на меня подписан
    followers = db.relationship(
        'Follow',
        foreign_keys='Follow.followed_id',
        backref='followed_user',   # backref для Follow.followed
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    # На кого я подписан
    following = db.relationship(
        'Follow',
        foreign_keys='Follow.follower_id',
        backref='follower_user',   # backref для Follow.follower
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    def is_following(self, user):
        if user.id is None:
            return False
        return self.following.filter_by(followed_id=user.id).first() is not None
    comments_made = db.relationship('Comment', backref='author', lazy='dynamic')
    likes_given = db.relationship('Like', backref='user', lazy='dynamic')

    # --- Свойство для получения объектов пользователей, на которых я подписан ---
    @property
    def followed(self):
        # Возвращает список объектов Gebruiker, на которых я подписан
        return [f.followed_user for f in self.following]

    # --- Методы для управления подписками ---
    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower_id=self.id, followed_id=user.id)
            db.session.add(f)
            return True
        return False

    def unfollow(self, user):
        f = self.following.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)
            return True
        return False



    def has_liked_model(self, stl_model):
        if stl_model.id is None:
            return False
        return self.likes_given.filter_by(model_id=stl_model.id).first() is not None

    # --- REDIS CACHE МЕТОДЫ ---
    def cache_key(self):
        return f"gebruiker:{self.id}"

    def cache_to_redis(self, expire_seconds=3600):
        from app.extensions import redis_client
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'profile_picture_url': self.profile_picture_url,
            'full_name': self.full_name,
            'bio': self.bio,
            'is_private': self.is_private,
        }
        redis_client.setex(self.cache_key(), expire_seconds, json.dumps(data))

    @classmethod
    def get_from_cache(cls, user_id):
        from app.extensions import redis_client
        key = f"gebruiker:{user_id}"
        cached = redis_client.get(key)
        if cached:
            return json.loads(cached)
        user = cls.query.get(user_id)
        if user:
            user.cache_to_redis()
            return {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'profile_picture_url': user.profile_picture_url,
                'full_name': user.full_name,
                'bio': user.bio,
                'is_private': user.is_private,
            }
        return None

    def __repr__(self):
        return f"Gebruiker('{self.username}', '{self.email}', 'Privé: {self.is_private}')"

# --- Модель для STL файлов ---


class STLModel(db.Model):
    __tablename__ = 'stlmodel'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.String(120), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    location = db.Column(db.String(100), nullable=True)
    tags = db.Column(db.String(200), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('gebruiker.id'), nullable=False)

    gebruiker = db.relationship('Gebruiker', backref='stl_models', lazy=True)  # user → gebruiker (чтобы было как в других местах)

    likes = db.relationship('Like', backref='model', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='model', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f"STLModel('{self.title}', '{self.date_posted}')"

# --- Модель лайков ---
class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('gebruiker.id'), nullable=False)
    model_id = db.Column(db.Integer, db.ForeignKey('stlmodel.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'model_id', name='_user_model_like_uc'),)

    def __repr__(self):
        return f'<Like Gebruiker {self.user_id} op Model {self.model_id}>'

# --- Модель комментариев ---
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('gebruiker.id'), nullable=False)
    model_id = db.Column(db.Integer, db.ForeignKey('stlmodel.id'), nullable=False)

    def __repr__(self):
        return f'<Commentaar {self.id} door Gebruiker {self.user_id} op Model {self.model_id}>'
