import redis


class RedisDB:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self, host: str = "127.0.0.1", port: int = 6379):
        if self.__class__._instance is not None:
            raise RuntimeError("Singleton all ready initialized ( use RedisDB.get_connection() )")
        self.host = host
        self.port = port
        self.connection = redis.Redis(host=host, port=port)

    def get_item(self, key):
        return self.connection.get(key)

    def set_item(self, key, value):
        self.connection.set(key, value)
