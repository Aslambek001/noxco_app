from flask import Blueprint
from app.extensions import redis_client  # Redis-client wordt hier geïmporteerd

redis_test = Blueprint('redis_test', __name__)  # Nieuwe Blueprint voor Redis-routes

@redis_test.route("/test-redis")
def test_redis():
    # Zet een tijdelijke sleutel in Redis, die 60 seconden geldig is
    redis_client.set("testkey", "Hallo van Redis!", ex=60)

    # Haal de waarde op uit Redis
    value = redis_client.get("testkey")

    # Controleer of de waarde bestaat
    if value:
        return f"Waarde uit Redis: {value.decode()}"
    else:
        return "Geen waarde gevonden in Redis."
