from fastapi import FastAPI

from .endpoints.proxy_endpoint import proxy_endpoint

from external_api.utils import openapi_schema


gateway_external_api = FastAPI()
gateway_external_api.openapi = openapi_schema

gateway_external_api.include_router(proxy_endpoint)
