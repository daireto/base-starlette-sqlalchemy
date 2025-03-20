"""This module provides the ``StarletteAdmin`` class
to generate an Admin interface for a Starlette application.
"""

from collections.abc import Awaitable, Callable
from logging import Logger, getLogger
from typing import TypeVar

from sqlalchemy.ext.asyncio import AsyncEngine
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette_admin import CustomView
from starlette_admin.contrib.sqla import Admin as BaseAdmin
from starlette_admin.contrib.sqla import ModelView
from starlette_admin.views import BaseView

from .auth import AdminAuthProvider

BaseModelView = TypeVar('BaseModelView', bound=ModelView)


class Admin(BaseAdmin):
    def custom_render_js(self, request: Request) -> str | None:
        return str(request.url_for('static', path='js/customRender.js'))


class StarletteAdmin:
    """Admin interface for Starlette applications."""

    _logger: Logger
    """Logger."""

    def __init__(
        self,
        app: Starlette,
        engine: AsyncEngine,
        models: list[type[BaseModelView]],
        index_view: CustomView | None = None,
        title: str = 'Admin Interface',
        base_url: str = '/admin',
        route_name: str = 'admin',
        templates_dir: str = 'templates/admin',
        login_func: Callable[[str, str], Awaitable[bool] | bool] | None = None,
        login_path: str = '/login',
        logout_path: str = '/logout',
        session_secret_key: str = '',
        favicon_url: str = '/static/icons/favicon.ico',
        user_photo_url_func: Callable[[str], str] | None = None,
        logger: Logger | None = None,
        debug: bool = False,
    ) -> None:
        """Creates an Admin interface for Starlette applications.

        Parameters
        ----------
        app : Starlette
            Application.
        engine : AsyncEngine
            SQLAlchemy engine.
        models : list[type[Any]]
            List of SQLAlchemy models.
        index_view : CustomView | None, optional
            Index view of the Admin interface, by default None.
        title : str, optional
            Title of the Admin interface, by default 'Admin interface'.
        base_url : str, optional
            Base URL of the Admin interface, by default '/admin'.
        route_name : str, optional
            Route name of the Admin interface, by default 'admin'.
        templates_dir : str, optional
            Templates directory of the Admin interface, by default 'templates'.
        login_func : Callable[[str, str], Awaitable[bool] | bool] | None, optional
            Login function of the Admin interface, by default None.
            If given, the Admin interface will be protected
            with the custom ``AdminAuthProvider`` auth provider.
        login_path : str, optional
            Login path of the Admin interface, by default '/login'.
            Used only if ``login_func`` is not None.
        logout_path : str, optional
            Logout path of the Admin interface, by default '/logout'.
            Used only if ``login_func`` is not None.
        session_secret_key : str, optional
            Secret key for the session, by default ''.
        favicon_url : str, optional
            Favicon URL of the Admin interface, by default '/static/icons/favicon.ico'.
        user_photo_url_func : Callable[[str], str] | None, optional
            User photo URL function, by default None.
        logger : Logger | None, optional
            Logger of the Admin interface, by default None.
        debug : bool, optional
            Debug mode of the Admin interface, by default False.
        """
        self._app = app
        self._models = models

        auth_provider = None
        if login_func is not None:
            auth_provider = AdminAuthProvider(
                login_func=login_func,
                login_path=login_path,
                logout_path=logout_path,
                photo_url_func=user_photo_url_func,
            )

        self._admin = Admin(
            engine=engine,
            title=title,
            base_url=base_url,
            route_name=route_name,
            templates_dir=templates_dir,
            index_view=index_view,
            auth_provider=auth_provider,
            middlewares=[
                Middleware(
                    SessionMiddleware,
                    secret_key=session_secret_key,
                    same_site='strict',
                    max_age=None,
                )
            ],
            favicon_url=favicon_url,
            debug=debug,
        )

        if logger is None:
            self._logger = getLogger(__name__)
        else:
            self._logger = logger

    def mount(self) -> None:
        """Mounts the Admin interface."""
        self._logger.debug('Initializing admin interface...')
        self.__add_model_views()
        self._admin.mount_to(self._app)
        self._logger.info('Admin interface mounted on "/admin"')

    def add_view(self, view: type[BaseView] | BaseView) -> None:
        """Adds a view to the Admin interface."""
        self._logger.debug(
            f'Adding view: {view.label if view.label else str(view)}'
        )
        self._admin.add_view(view)

    def __add_model_views(self) -> None:
        """Adds model views to the Admin interface."""
        for model in self._models:
            self._logger.debug(f'Adding model view: {model.__name__}')
            self._admin.add_view(model)
