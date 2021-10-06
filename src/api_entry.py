from fastapi import FastAPI, Request as FastAPIRequest
from fastapi.responses import JSONResponse, Response

from db.mongo import MongoDB
from service import Service
from request import Request
from internal_api import gateway_internal_api

api = FastAPI(title="Gateway")
api.mount("/internal", gateway_internal_api, name="Internal api")

services = {}

ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"]


@api.route("/{p:path}", name="entry", methods=ALLOWED_METHODS, include_in_schema=False)
async def entry_point(r: FastAPIRequest):
    service_name = r.path_params["p"].split("/")[0]
    print(service_name)
    service = services[service_name]

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
    db = MongoDB.get_instance()
    all_services_dict = db.services.find({}, {"_id": 0, "created_at": 0})
    services.update({service_dict["name"].lower(): Service(**service_dict) for service_dict in all_services_dict})


@api.on_event("shutdown")
async def shutdown():
    MongoDB.get_instance().close()
