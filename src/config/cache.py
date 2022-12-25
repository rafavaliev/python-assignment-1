import os

import redis


def get_cache():
    # TODO: Set up redis connection pool
    cache = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=os.getenv("REDIS_PORT", 6379),
        db=os.getenv("REDIS_DB", 0),
        password=os.getenv("REDIS_PASSWORD", None),
    )
    try:
        yield cache
    finally:
        cache.close()
