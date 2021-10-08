from fastapi import FastAPI

from context import initiate, cleanup
from internal_api import gateway_internal_api
from external_api import gateway_external_api, EXTERNAL_PREFIX


api = FastAPI(title="Gateway")
api.mount("/internal", gateway_internal_api, name="Internal API")
api.mount(EXTERNAL_PREFIX, gateway_external_api, name="External API")


@api.on_event("startup")
async def startup():
    initiate()


@api.on_event("shutdown")
async def shutdown():
    cleanup()
