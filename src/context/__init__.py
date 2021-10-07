from .db import get_db
from .services import get_services
from .cache import get_cache


__all__ = ["get_db", "get_services", "get_cache", "initiate", "cleanup"]


def initiate():
    """
    Initiate global context
    connect to db
    and load services
    """
    get_db()
    get_services()
    get_cache()


def cleanup():
    get_db().close()
