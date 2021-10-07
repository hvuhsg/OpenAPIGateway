from db.mongo import MongoDB


def get_db() -> MongoDB:
    return MongoDB.get_instance()
