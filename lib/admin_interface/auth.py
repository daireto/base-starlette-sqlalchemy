"""Admin auth provider."""

from collections.abc import Awaitable, Callable, Sequence
from datetime import datetime, timedelta, timezone
from inspect import iscoroutinefunction

from starlette.concurrency import run_in_threadpool
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette.status import (
    HTTP_303_SEE_OTHER,
    HTTP_400_BAD_REQUEST,
    HTTP_422_UNPROCESSABLE_ENTITY,
)
from starlette_admin import BaseAdmin
from starlette_admin.auth import AdminUser, AuthProvider
from starlette_admin.exceptions import FormValidationError, LoginFailed


class AdminAuthProvider(AuthProvider):
    """Auth provider for the admin interface."""

    _login_func: Callable[[str, str], Awaitable[bool] | bool]
    """Login function."""

    _login_failed_message: str
    """Login failed message."""

    _photo_url_func: Callable[[str], str] | None
    """Photo URL function."""

    def __init__(
        self,
        login_func: Callable[[str, str], Awaitable[bool] | bool],
        login_path: str = '/login',
        logout_path: str = '/logout',
        allow_routes: Sequence[str] | None = None,
        failed_login_message: str = 'Invalid username or password',
        photo_url_func: Callable[[str], str] | None = None,
    ) -> None:
        """Initializes the admin auth provider.

        Parameters
        ----------
        login_func : Callable[[str, str], Awaitable[bool]  |  bool]
            Login function.
        login_path : str, optional
            Login path, by default '/login'.
        logout_path : str, optional
            Logout path, by default '/logout'.
        allow_routes : Sequence[str] | None, optional
            Allowed routes, by default None.
        failed_login_message : str, optional
            Login failed message, by default 'Invalid username or password'.
        photo_url_func : Callable[[str], str] | None, optional
            Photo URL function, by default None.
        """
        super().__init__(
            login_path=login_path,
            logout_path=logout_path,
            allow_routes=allow_routes,
        )
        self._login_func = login_func
        self._login_failed_message = failed_login_message
        self._photo_url_func = photo_url_func

    async def login(
        self,
        username: str,
        password: str,
        request: Request,
        response: Response,
    ) -> Response:
        if iscoroutinefunction(self._login_func):
            authenticated = await self._login_func(username, password)
        else:
            authenticated = await run_in_threadpool(
                self._login_func, username, password
            )

        if not authenticated:
            raise LoginFailed(self._login_failed_message)

        exp = datetime.timestamp(
            datetime.now(timezone.utc) + timedelta(days=1)
        )
        request.session.update({'username': username, 'exp': exp})
        return response

    async def is_authenticated(self, request: Request) -> bool:
        username = request.session.get('username')
        exp = request.session.get('exp')
        if username is None or exp is None:
            return False

        try:
            if float(exp) < datetime.timestamp(datetime.now(timezone.utc)):
                return False
        except ValueError:
            return False

        return True

    def get_admin_user(self, request: Request) -> AdminUser | None:
        username = request.session.get('username')
        if username is None:
            return None

        if self._photo_url_func is None:
            return AdminUser(username=username)

        photo_url = self._photo_url_func(username)
        return AdminUser(username=username, photo_url=photo_url)

    async def logout(self, request: Request, response: Response) -> Response:
        request.session.clear()
        return response

    async def render_login(
        self, request: Request, admin: BaseAdmin
    ) -> Response:
        TEMPLATE_FILENAME = 'login.j2'

        if request.method == 'GET':
            return admin.templates.TemplateResponse(
                TEMPLATE_FILENAME,
                {'request': request, '_is_login_path': True},
            )

        form = await request.form()
        try:
            return await self.login(
                username=form.get('username'),  # type: ignore
                password=form.get('password'),  # type: ignore
                request=request,
                response=RedirectResponse(
                    request.query_params.get('next')
                    or request.url_for(admin.route_name + ':index'),
                    status_code=HTTP_303_SEE_OTHER,
                ),
            )
        except FormValidationError as errors:
            return admin.templates.TemplateResponse(
                TEMPLATE_FILENAME,
                {
                    'request': request,
                    'form_errors': errors,
                    '_is_login_path': True,
                },
                status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            )
        except LoginFailed as error:
            return admin.templates.TemplateResponse(
                TEMPLATE_FILENAME,
                {
                    'request': request,
                    'error': error.msg,
                    '_is_login_path': True,
                },
                status_code=HTTP_400_BAD_REQUEST,
            )
