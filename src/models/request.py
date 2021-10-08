from fastapi import Request as FastAPIRequest
from openapi_core.validation.request.datatypes import OpenAPIRequest
from openapi_core.validation.request.datatypes import RequestParameters


class Headers(dict):
    pass


class Request(OpenAPIRequest):
    def __init__(
            self,
            base_url,
            service_path,
            path,
            method: str,
            client,
            body: str,
            content_type,
            query_params,
            headers,
            cookies: dict,
    ):
        self.base_url = base_url
        self.service_path = service_path
        self.path = path
        self.full_url_pattern = str(base_url) + str(path)

        self.method = method.lower()
        self.mimetype = content_type
        self.client = client

        self.body = body
        self.cookies = cookies
        self.query_parameters = query_params
        self.headers = headers
        self.parameters = RequestParameters(query=query_params, header=headers, cookie=cookies, path={})

    @classmethod
    async def from_fastapi_request(cls, r: FastAPIRequest):
        segments = r.url.path.split("/")
        segments.pop(1)  # remove '/external'
        request_path = '/'.join(segments)[1:]
        service_path = '/'.join(r.url.path.split("/")[3:])

        query_params = {k: v for k, v in r.query_params.items()}
        full_content_type = r.headers.get("Content-Type")
        content_type = None if full_content_type is None else full_content_type.split(";")[0].lower()
        headers = Headers()
        headers.update({k: v for k, v in r.headers.items()})
        body = (await r.body()).decode()
        return cls(
            base_url=r.base_url,
            service_path=service_path,
            path=request_path,
            headers=headers,
            client=r.client,
            query_params=query_params,
            body=body,
            content_type=content_type,
            method=r.method.lower(),
            cookies=r.cookies,
        )
