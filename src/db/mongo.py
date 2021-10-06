import os
from dotenv import load_dotenv
from qwhale_client import APIClient

load_dotenv(".env")
QWHALE_TOKEN = os.getenv("QWHALE_TOKEN")


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

        self._client = APIClient(QWHALE_TOKEN)
        self.db = self._client.get_database()
        self.services = self.db.get_collection("services")

    def close(self):
        self._client.close()
