from typing import Any
from uuid import uuid4
from datetime import datetime
import json

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, AnyHttpUrl, constr, validator, Field
from openapi_spec_validator import validate_spec

from db.mongo import MongoDB

service_resource = APIRouter(prefix="/service", tags=["service"])


class NewService(BaseModel):
    name: constr(max_length=40)
    url: AnyHttpUrl
    openapi_spec: dict

    @validator("openapi_spec")
    def validate_openapi_spec(cls, spec):
        validate_spec(spec=spec)
        return spec


class ServiceModel(BaseModel):
    id: str
    name: str
    url: AnyHttpUrl
    openapi_spec: dict
    created_at: datetime = Field(default_factory=datetime.utcnow, description="creation time in UTC timezone")

    @validator("openapi_spec", whole=True, pre=True)
    def convert_spec_to_dict(cls, spec):
        if type(spec) is not dict:
            spec = json.loads(spec)
        return spec

    def dict(self, escape: bool = False, *args, **kwargs):
        dict_res = super().dict(*args, **kwargs)
        if escape:
            dict_res["openapi_spec"] = json.dumps(dict_res["openapi_spec"])
        return dict_res


@service_resource.delete("")
def remove(service_id: str):
    services_col = MongoDB.get_instance().services
    removed = services_col.delete_one({"id": service_id})
    return {"removed": bool(removed.deleted_count)}


@service_resource.put("", status_code=201)
def create(service: NewService):
    services_col = MongoDB.get_instance().services
    if services_col.find_one({"url": service.url}, {"_id": 1}) or services_col.find_one({"name": service.name}, {"_id": 1}):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="URL or name are all ready exist.")
    new_service_id = str(uuid4())
    while services_col.find_one({"id": new_service_id}) is not None:
        new_service_id = str(uuid4())
    new_service = ServiceModel(id=new_service_id, **service.dict())
    services_col.insert_one(new_service.dict(escape=True))
    return {"service_id": new_service_id}


@service_resource.get("")
def get(service_id: str):
    services_col = MongoDB.get_instance().services
    service_dict = services_col.find_one({"id": service_id}, {"_id": 0})
    if service_dict is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"service with id '{service_id}' not found")
    return ServiceModel(**service_dict).dict()


@service_resource.patch("")
def update(service_id: str, field: str, value: Any):
    services_col = MongoDB.get_instance().services
    if field in ("id", ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"cant update field '{field}'")
    service_dict = get(service_id)
    service = ServiceModel(**service_dict)
    try:
        setattr(service, field, value)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Field not exist or invalid value")
    updated = services_col.update_one({"id": service_id}, {"$set": service.dict(escape=True)})
    return {"updated": bool(updated.modified_count)}


@service_resource.get("/list")
def service_list():
    services_col = MongoDB.get_instance().services
    services = list(services_col.find({}, {"id": 1, "name": 1, "_id": 0}))
    return services
