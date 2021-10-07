from fastapi.responses import JSONResponse
from openapi_core.validation.request.validators import RequestValidator

from middleware_core import BaseMiddleware


class OpenAPIValidationMiddleware(BaseMiddleware):
    async def __call__(self, request, service):
        if service.openapi_spec:
            validation_response = RequestValidator(service.openapi_spec).validate(request)
            if validation_response.errors:
                response_content = [str(error) for error in validation_response.errors]
                return JSONResponse(content=response_content, status_code=400)
        return await self.next(request, service)
