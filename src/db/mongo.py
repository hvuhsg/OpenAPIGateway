from qwhale_client import APIClient

from context import get_settings


class MongoDB:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if self.__class__._instance is not None:
            raise RuntimeError("Singleton all ready initialized ( use MongoDB.get_instance() )")

        self._client = APIClient(get_settings().qwhale_token)
        self.db = self._client.get_database()
        self.services = self.db.get_collection("services")

    def create_service(self, service):
        return self.services.insert_one(service)

    def delete_service(self, service_id) -> bool:
        return self.services.delete_one({"id": service_id}).deleted_count > 0

    def get_service(self, field_value, check_existence: bool = False, find_by: str = "id"):
        """
        Get service where find_by == field_value e.g: {"id": "some id value"}
        :param field_value: the field value
        :param check_existence: return is service exist (bool)
        :param find_by: the field to find by
        :return: service document or bool
        """
        if check_existence:
            return self.services.find_one({find_by: field_value}, {"_id": 1}) is not None
        return self.services.find_one({find_by: field_value}, {"_id": 0})

    def update_service(self, service_id, key, updated_value):
        return self.services.update_one({"id": service_id}, {"$set": {key: updated_value}})

    def get_all_services(self, exclude_fields: list = None, include_fields: list = None) -> list:
        filters = {}
        if exclude_fields:
            filters.update({field: 0 for field in exclude_fields})
        if include_fields:
            filters.update({field: 1 for field in include_fields})
        return list(self.services.find({}, filters))

    def close(self):
        self._client.close()
