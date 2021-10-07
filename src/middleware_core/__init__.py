from typing import List

from .base_middleware import BaseMiddleware
from .exceptions import MiddlewareException
from .middleware_context import MiddlewareContext


__all__ = ["BaseMiddleware", "MiddlewareContext", "MiddlewareException", "middleware_chain_builder"]


def middleware_chain_builder(middleware_classes: List[type], context: MiddlewareContext = None) -> BaseMiddleware:
    """
    Build middleware chain and return the root middleware
    :param middleware_classes: list of middleware classes
    :param context: middleware context
    :return: the root middleware in the chain
    """
    if context is None:
        context = MiddlewareContext()

    if not middleware_classes:
        return None

    return _get_middleware_chain_root(middleware_classes, context)


def _get_middleware_chain_root(middleware_classes: List[type], context: MiddlewareContext, current_index: int = 0):
    if current_index == len(middleware_classes) - 1:
        return middleware_classes[current_index](context=context, next_middleware=None)
    return middleware_classes[current_index](
        context=context,
        next_middleware=_get_middleware_chain_root(middleware_classes, context, current_index + 1)
    )

