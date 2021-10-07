from db.redis import RedisDB


def get_cache():
    return RedisDB.get_instance()
