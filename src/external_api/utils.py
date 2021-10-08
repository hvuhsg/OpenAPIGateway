from context import get_services
from .config import EXTERNAL_PREFIX


def openapi_schema():
    services = get_services()

    merged_schema = {
        "openapi": "3.0.2",
        "info": {
                "title": "APIGateway",
                "version": "0.1.0"
            },
        "servers": [
            {"url": EXTERNAL_PREFIX}
        ],
        "paths": {},
        "components": {
            "schemas": {},
        },
    }
    for service in services:
        schema = service.openapi_dict
        for path, data in schema["paths"].items():
            for operation in data.values():
                operation.pop("tags", None)
                operation["tags"] = [service.name]
            merged_schema["paths"]['/' + service.prefix_path + path] = data
        merged_schema["components"]["schemas"].update(schema.get("components", {}).get("schemas"))
    return merged_schema
