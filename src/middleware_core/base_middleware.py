from abc import ABC, abstractmethod

from .middleware_context import MiddlewareContext
from models.service import Service
from models.request import Request


class BaseMiddleware(ABC):
    def __init__(self, context: MiddlewareContext, next_middleware):
        self.context = context
        self.next = next_middleware

    @abstractmethod
    async def __call__(self, request: Request, service: Service):
        raise NotImplementedError

