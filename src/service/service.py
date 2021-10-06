from urllib.parse import urljoin
import json

from openapi_core import create_spec
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.validation.request.datatypes import RequestValidationResult
import httpx

from request import Request


class Service:
    def __init__(self, id: str, name: str, url: str, openapi_spec: str):
        self.id = id
        self.name = name
        self.url = url
        self.openapi_json = json.loads(openapi_spec)

        self.prefix_path = name
        self.openapi_json["servers"] = [{"url": f"http://127.0.0.1:116/{self.prefix_path}"}]
        self.openapi_spec = create_spec(self.openapi_json)
        self.openapi_version = self.openapi_json["openapi"]
        self.client = httpx.AsyncClient()

    async def forward_request(self, request: Request) -> httpx.Response:
        url = urljoin(self.url, request.service_path)
        response = await self.client.request(request.method, url=url, params=request.parameters.query)
        return response

    def validate_request(self, request: Request) -> RequestValidationResult:
        return RequestValidator(self.openapi_spec).validate(request)
