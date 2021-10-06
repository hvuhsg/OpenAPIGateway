from fastapi import FastAPI

from .v1 import v1

gateway_internal_api = FastAPI(title="Internal")
gateway_internal_api.include_router(v1)


