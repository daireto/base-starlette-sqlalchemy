from core.bases.base_middleware import BaseMiddleware


class LanguageMiddleware(BaseMiddleware):
    """Gets the language from the ``Accept-Language`` header."""

    async def before_dispatch(self) -> None:
        await super().before_dispatch()
        accept_language = self.request.headers.get('Accept-Language')
        if not accept_language:
            accept_language = 'es'
        self.request.state.language = accept_language
