import os
import redis
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth

db = SQLAlchemy()
redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)
oauth = OAuth()


def init_redis(app):
    global redis_client
    redis_client = redis.Redis(
        host=app.config.get("REDIS_HOST", "redis"),
        port=app.config.get("REDIS_PORT", 6379),
        db=0
    )