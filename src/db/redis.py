import redis

from .interface import DBInterface


class RedisDB(DBInterface):
    _instance = None

    @classmethod
    def get_connection(cls):
        if cls._instance is None:
            raise RuntimeError("Initiate class first (use __init__)")
        return cls._instance

    def __init__(self, host: str, port: int = 6379):
        if self.__class__._instance is not None:
            raise RuntimeError("Singleton all ready initialized ( use RedisDB.get_connection() )")
        self.host = host
        self.port = port
        self.connection = redis.Redis(host=host, port=port)

        self.__class__._instance = self

    def get_item(self, key):
        return self.connection.get(key)

    def set_item(self, key, value):
        self.connection.set(key, value)
