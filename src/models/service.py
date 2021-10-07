import json

from openapi_core import create_spec
import httpx


class Service:
    def __init__(self, id: str, name: str, url: str, openapi_dict: dict):
        self.id: str = id
        self.name = name
        self.url = url
        self.openapi_dict = openapi_dict

        self.prefix_path = name.lower()
        self.openapi_spec = self._build_openapi_spec()
        self.client = httpx.AsyncClient()

    def _build_openapi_spec(self):
        if not self.openapi_dict:
            return None
        self.openapi_dict["servers"] = [{"url": f"http://127.0.0.1:116/{self.prefix_path}"}]
        openapi_spec = create_spec(self.openapi_dict)
        return openapi_spec

    @classmethod
    def from_dict(cls, service_dict: dict):
        if type(service_dict.get("openapi_spec", None)) is str:
            service_dict["openapi_spec"] = json.loads(service_dict["openapi_spec"])
        service_dict["openapi_dict"] = service_dict.pop("openapi_spec")
        return cls(**service_dict)
