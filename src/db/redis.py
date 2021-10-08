import redis

from context import get_settings


class RedisDB:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if self.__class__._instance is not None:
            raise RuntimeError("Singleton all ready initialized ( use RedisDB.get_connection() )")

        self.host = get_settings().redis_host
        self.port = get_settings().redis_port
        self.connection = redis.Redis(host=self.host, port=self.port)

    def get_item(self, key):
        return self.connection.get(key)

    def set_item(self, key, value):
        self.connection.set(key, value)
