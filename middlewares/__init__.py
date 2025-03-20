"""Middlewares."""

from starlette.middleware import Middleware

from core.bases.base_middleware import BaseMiddleware
from utils.package import get_all_package_clases

middlewares = [
    Middleware(cls)
    for cls in get_all_package_clases(
        __file__, __name__, '_middleware', BaseMiddleware
    )
]
"""List of middlewares."""
