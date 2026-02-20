import redis
import json
from config import Config
from flask_jwt_extended import get_jwt_identity
from models.patient import Patient   


# Redis Connection
redis_client = redis.Redis.from_url(
    Config.REDIS_URL,
    decode_responses=True
)


# Get value from cache means it wil check in check ki data is avilable or not if not return none
def get_cache(key):
    data = redis_client.get(key)
    if data:
        return json.loads(data)
    return None


# Set value in cache    after 5min cache will delete automaticlly
def set_cache(key, value, ttl=300):
    redis_client.setex(
        key,
        ttl,
        json.dumps(value)
    )


#Delete key from cache  whenevr data will update n then we need to delte the cache
def delete_cache(key):
    redis_client.delete(key)


# Get logged-in patient using JWT
def get_patient_by_token():
    user_id = get_jwt_identity()
    return Patient.query.filter_by(user_id=user_id).first()
