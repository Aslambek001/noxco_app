import os
import redis
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth

db = SQLAlchemy()
oauth = OAuth()


# app/extensions.py


# Initieer een Redis-client via de variabelen in .env
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    # decode_responses=True  # zorgt voor str i.p.v. bytes
)
