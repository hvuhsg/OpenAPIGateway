from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from context import get_settings

from .endpoints.proxy_endpoint import proxy_endpoint
from .utils import openapi_schema


gateway_external_api = FastAPI()

gateway_external_api.openapi = openapi_schema
gateway_external_api.add_middleware(
    SessionMiddleware,
    secret_key=get_settings().secret_key,
    https_only=not get_settings().allow_session_over_http
)

gateway_external_api.include_router(proxy_endpoint)
