"""Admin interface for Starlette applications."""

from .admin import StarletteAdmin
from .auth import AdminAuthProvider

__all__ = ['StarletteAdmin', 'AdminAuthProvider']
