"""Routers."""

from core.bases.base_router import BaseRouter
from utils.package import get_all_package_clases

routers = get_all_package_clases(__file__, __name__, '_router', BaseRouter)
"""List of routers."""
