from context import get_cache, get_db


class MiddlewareContext:
    def __init__(self):
        self.cache = get_cache()
        self.db = get_db()
