"""Custom exceptions."""


class BaseError(Exception):
    """Common base class for all exceptions."""

    def __init__(self, message: str, note: str | None = None):
        """Creates a new exception.

        Parameters
        ----------
        message : str
            Exception message.
        note : str | None, optional
            Exception note, by default None.
        """
        super().__init__(message)
        if note:
            self.add_note(note)


class InvalidRoutePathError(BaseError, RuntimeError):
    """Invalid route path."""

    def __init__(self, note: str | None = None):
        """Invalid route path.

        Parameters
        ----------
        note : str | None, optional
            Exception note, by default None.
        """
        super().__init__("routed paths must start with '/'", note)
