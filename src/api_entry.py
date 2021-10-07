from fastapi import FastAPI, Request as FastAPIRequest, HTTPException, status
from fastapi.responses import JSONResponse, Response

from context import get_services, initiate, cleanup
from models.request import Request
from internal_api import gateway_internal_api

api = FastAPI(title="Gateway")
api.mount("/internal", gateway_internal_api, name="Internal api")

ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"]


@api.route("/{p:path}", name="entry", methods=ALLOWED_METHODS, include_in_schema=False)
async def entry_point(r: FastAPIRequest):
    services = get_services()
    service_prefix_path = r.path_params["p"].split("/")[0]
    service = services.get_service(service_prefix_path.lower())
    if service is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="service not found")

    request = await Request.from_fastapi_request(r)
    validation_response = service.validate_request(request)

    if validation_response.errors:
        response_content = [str(error) for error in validation_response.errors]
        response = JSONResponse(content=response_content, status_code=400)
    else:
        service_response = await service.forward_request(request)
        response_content = service_response.content
        response = Response(
            content=response_content,
            status_code=service_response.status_code,
            headers={k: v for k, v in service_response.headers.items()},
        )

    return response


@api.on_event("startup")
async def startup():
    initiate()


@api.on_event("shutdown")
async def shutdown():
    cleanup()
