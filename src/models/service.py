import asyncio
from urllib.parse import urljoin
import json

from openapi_core import create_spec
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.validation.request.datatypes import RequestValidationResult
import httpx

from models.request import Request


class Service:
    def __init__(self, id: str, name: str, url: str, openapi_spec: dict):
        self.id: str = id
        self.name = name
        self.url = url
        self.openapi_json = openapi_spec

        self.prefix_path = name.lower()
        self.openapi_json["servers"] = [{"url": f"http://127.0.0.1:116/{self.prefix_path}"}]
        self.openapi_spec = create_spec(self.openapi_json)
        self.openapi_version = self.openapi_json["openapi"]
        self.client = httpx.AsyncClient()

    async def forward_request(self, request: Request) -> httpx.Response:
        url = urljoin(self.url, request.service_path)
        self.client.cookies.clear()
        self.client.headers.clear()
        response = await self.client.request(request.method, url=url, params=request.parameters.query)
        return response

    def validate_request(self, request: Request) -> RequestValidationResult:
        return RequestValidator(self.openapi_spec).validate(request)

    @classmethod
    def from_dict(cls, service_dict: dict):
        if type(service_dict.get("openapi_spec", None)) is str:
            service_dict["openapi_spec"] = json.loads(service_dict["openapi_spec"])
        return cls(**service_dict)

    def __del__(self):
        asyncio.run(self.client.aclose())
