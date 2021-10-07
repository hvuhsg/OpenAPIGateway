from models.services import Services


__all__ = ["get_services"]


def get_services() -> Services:
    return Services.get_instance()
