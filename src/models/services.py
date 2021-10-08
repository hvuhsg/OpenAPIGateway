from typing import Dict, Optional

from context.db import get_db
from models.service import Service

__all__ = ["Services"]


class Services:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if self._instance is not None:
            raise RuntimeError("Services singleton all ready initiated")

        self.db = get_db()
        self.__services: Dict[str, Service] = {}
        self.__services_by_id: Dict[str, Service] = {}
        self._load_services()

    def _load_services(self):
        services = [
            Service.from_dict(service_dict)
            for service_dict in self.db.get_all_services(exclude_fields=["_id", "created_at"])
        ]
        for service in services:
            self.__services[service.prefix_path] = service
            self.__services_by_id[service.id] = service

    def _load_service(self, service_id) -> Service:
        db = get_db()
        service_dict = db.get_service(service_id)
        service_dict.pop("created_at", None)
        return Service.from_dict(service_dict)

    def add_service(self, service_id):
        service = self._load_service(service_id)
        self.__services[service.prefix_path] = service
        self.__services_by_id[service.id] = service

    def remove_service(self, service_id):
        service = self.__services_by_id.pop(service_id, None)
        if service is not None:
            self.__services.pop(service.prefix_path)

    def updated_service(self, service_id):
        updated_service = self._load_service(service_id)
        old_service = self.__services_by_id[service_id]
        self.__services.pop(old_service.prefix_path)
        self.__services_by_id[service_id] = updated_service
        self.__services[updated_service.prefix_path] = updated_service

    def get_service(self, prefix_path) -> Optional[Service]:
        return self.__services.get(prefix_path)

    def __iter__(self):
        return iter(self.__services.values())
