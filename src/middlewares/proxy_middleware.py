from urllib.parse import urljoin

from fastapi import Response

from middleware_core import BaseMiddleware


class ProxyMiddleware(BaseMiddleware):
    async def __call__(self, request, service):
        url = urljoin(service.url, request.service_path)
        service.client.cookies.clear()  # Do not save state for security reasons
        service.client.headers.clear()
        service_response = await service.client.request(request.method, url=url, params=request.parameters.query)
        response_content = service_response.content
        response = Response(
            content=response_content,
            status_code=service_response.status_code,
            headers={k: v for k, v in service_response.headers.items()},
        )
        return response
