from abc import ABC, abstractmethod


class DBInterface(ABC):
    @classmethod
    @abstractmethod
    def get_connection(cls):
        pass

    @abstractmethod
    def get_item(self, key):
        pass

    @abstractmethod
    def set_item(self, key, value):
        pass
