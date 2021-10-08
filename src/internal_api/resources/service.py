from typing import Any
from uuid import uuid4
from datetime import datetime
import json

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, AnyHttpUrl, constr, validator, Field
from openapi_spec_validator import validate_spec
from openapi_spec_validator.exceptions import OpenAPIValidationError

from context import get_db, get_services
from context.services import Services

from db.mongo import MongoDB

service_resource = APIRouter(prefix="/service", tags=["service"])


class NewService(BaseModel):
    name: constr(max_length=40)
    url: AnyHttpUrl
    openapi_spec: dict

    @validator("openapi_spec")
    def validate_openapi_spec(cls, spec):
        try:
            validate_spec(spec=spec)
        except OpenAPIValidationError:
            raise ValueError("Invalid openapi spec")
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
def remove(service_id: str, db: MongoDB = Depends(get_db), services: Services = Depends(get_services)):
    removed = db.delete_service(service_id)
    services.remove_service(service_id)
    services.remove_service(service_id)
    return {"removed": removed}


@service_resource.put("", status_code=201)
def create(service: NewService, db: MongoDB = Depends(get_db), services: Services = Depends(get_services)):
    if db.get_service(service.url, check_existence=True, find_by="url") \
            or db.get_service(service.name, check_existence=True, find_by="name"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="URL or name are all ready exist.")
    new_service_id = str(uuid4())
    while db.get_service(new_service_id, check_existence=True):
        new_service_id = str(uuid4())
    new_service = ServiceModel(id=new_service_id, **service.dict())
    service_dict = new_service.dict(escape=True)
    db.create_service(service_dict)
    services.add_service(new_service_id)
    return {"service_id": new_service_id}


@service_resource.get("")
def get(service_id: str, db: MongoDB = Depends(get_db)):
    service_dict = db.get_service(field_value=service_id)
    if service_dict is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"service with id '{service_id}' not found")
    return ServiceModel(**service_dict).dict()


@service_resource.patch("")
def update(
        service_id: str, field: str, value: Any, db: MongoDB = Depends(get_db), services: Services = Depends(get_services)
):
    if field in ("id", ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"cant update field '{field}'")
    service_dict = db.get_service(service_id)
    service = ServiceModel(**service_dict)
    try:
        setattr(service, field, value)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Field not exist or invalid value")

    updated_value = service.dict(escape=True)[field]
    updated_result = db.update_service(service_id, field, updated_value)
    updated = bool(updated_result.modified_count)
    if updated:
        services.updated_service(service_id)
    return {"updated": updated}


@service_resource.get("/list")
def service_list(db: MongoDB = Depends(get_db)):
    services = db.get_all_services(include_fields=["id", "name"], exclude_fields=["_id"])
    return services
