from functools import lru_cache

from fastapi import FastAPI, Request as FastAPIRequest, HTTPException, status

from context import get_services, initiate, cleanup
from models.request import Request
from internal_api import gateway_internal_api
from middleware_core import middleware_chain_builder
from middlewares.proxy_middleware import ProxyMiddleware
from middlewares.openapi_validator_middleware import OpenAPIValidationMiddleware


api = FastAPI(title="Gateway")
api.mount("/internal", gateway_internal_api, name="Internal api")

ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"]


@api.route("/{p:path}", name="entry", methods=ALLOWED_METHODS, include_in_schema=False)
async def entry_point(r: FastAPIRequest):
    service = get_service(r)
    request = await Request.from_fastapi_request(r)

    middleware = build_middleware()
    service_response = await middleware(request, service)
    return service_response


@lru_cache
def build_middleware():
    middleware_classes = [
        OpenAPIValidationMiddleware,
        ProxyMiddleware,
    ]
    root = middleware_chain_builder(middleware_classes)
    return root


def get_service(request):
    services = get_services()
    service_prefix_path = request.path_params["p"].split("/")[0]
    service = services.get_service(service_prefix_path.lower())
    if service is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="service not found")
    return service


@api.on_event("startup")
async def startup():
    initiate()


@api.on_event("shutdown")
async def shutdown():
    cleanup()
