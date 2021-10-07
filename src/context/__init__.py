from .db import get_db
from .services import get_services


__all__ = ["get_db", "get_services", "initiate", "cleanup"]


def initiate():
    """
    Initiate global context
    connect to db
    and load services
    """
    get_db()
    get_services()


def cleanup():
    get_db().close()
