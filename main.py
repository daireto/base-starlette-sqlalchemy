import uvicorn
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.requests import Request
from starlette.routing import Mount
from starlette.routing import Route as StarletteRoute
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette_di import DependencyInjectionMiddleware, ServiceCollection

from core import logger
from core.api.route import Route
from core.auth.middleware import AuthenticationMiddlewareBackend
from core.i18n import I18N
from core.settings import Settings
from lib.admin_interface import StarletteAdmin
from lib.apispec import StarletteAPISpec
from middlewares import middlewares
from models import admin as admin_views
from models import db as db_models
from routers import routers
from seed import seed
from services.auth_service import AuthService, IAuthService
from services.user_service import IUserService, UserService
from utils.func import get_robohash_url

services = ServiceCollection()
services.add_transient(I18N)
services.add_scoped(IUserService, UserService)
services.add_scoped(IAuthService, AuthService)
service_provider = services.build_provider()

templates = Jinja2Templates(directory='templates')

conn = Settings.create_db_connection()


async def on_startup():
    try:
        logger.info('Connecting to database and initializing models...')
        await conn.init_db(db_models.BaseModel)
        logger.info('Database connected and models initialized')

        if not Settings.server.PROD:
            await seed()

        logger.info('Application accessible at: ' + Settings.get_server_url())
    except Exception as e:
        Settings.status.status = 'error'
        Settings.status.message = 'cannot connect to database'
        logger.critical(f'Database connection error: {e}')


async def on_shutdown():
    logger.info('Disconnecting from database...')
    await conn.close(db_models.BaseModel)
    logger.info('Shutting down...')


async def homepage(request: Request):
    return templates.TemplateResponse(
        request, 'index.j2', {'title': Settings.api_spec.OPENAPI_TITLE}
    )


routes = [
    *Route.get_from_routers(routers),
    Mount('/static', app=StaticFiles(directory='static'), name='static'),
    StarletteRoute('/', endpoint=homepage, include_in_schema=False),
]

middlewares = [
    Middleware(
        TrustedHostMiddleware,
        allowed_hosts=Settings.trusted_host.ALLOWED_HOSTS,
    ),
    Middleware(
        CORSMiddleware,
        allow_origins=Settings.cors.ALLOW_ORIGINS,
        allow_methods=Settings.cors.ALLOW_METHODS,
        allow_headers=Settings.cors.ALLOW_HEADERS,
        expose_headers=Settings.cors.EXPOSE_HEADERS,
    ),
    Middleware(
        AuthenticationMiddleware, backend=AuthenticationMiddlewareBackend()
    ),
    Middleware(
        DependencyInjectionMiddleware, service_provider=service_provider
    ),
    *middlewares,
]

app = Starlette(
    debug=not Settings.server.PROD,
    routes=routes,
    middleware=middlewares,
    on_startup=[on_startup],
    on_shutdown=[on_shutdown],
)

StarletteAPISpec(
    app=app,
    servers=[Settings.get_server_url()],
    title=Settings.api_spec.OPENAPI_TITLE,
    version=Settings.api_spec.OPENAPI_VERSION,
    description=Settings.api_spec.OPENAPI_DESCRIPTION,
    logger=logger,
).mount()

StarletteAdmin(
    app=app,
    engine=conn.async_engine,
    models=admin_views.BaseAdminView.__subclasses__(),
    index_view=admin_views.IndexView(label='Home', icon='fa fa-home'),
    login_func=db_models.User.authenticate,
    session_secret_key=Settings.admin.SESSION_SECRET_KEY,
    user_photo_url_func=get_robohash_url,
    logger=logger,
    debug=not Settings.server.PROD,
).mount()

if __name__ == '__main__':
    if not Settings.server.PROD:
        logger.info('Running in development mode')

    uvicorn.run(
        app='main:app',
        port=Settings.server.PORT,
        log_config=Settings.get_logger_conf(),
        reload=not Settings.server.PROD,
    )
