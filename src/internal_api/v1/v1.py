from fastapi import APIRouter

from internal_api.resources.service import service_resource


v1 = APIRouter(prefix="/v1")
v1.include_router(service_resource)
