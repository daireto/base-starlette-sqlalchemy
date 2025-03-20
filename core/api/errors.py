"""HTTP errors."""


class HTTPError(IOError):
    """HTTP error (status code >= 400)."""

    def __init__(self, message: str, status_code: int = 500):
        """Creates an HTTP error.

        Parameters
        ----------
        message : str
            Exception message.
        status_code : int, optional
            Exception status code, by default 500.

        Raises
        ------
        ValueError
            If the status code is less than 400.
        """
        self.message = message
        self.set_status_code(status_code)
        super().__init__(message)

    def set_status_code(self, status_code: int) -> None:
        """Sets the status code which must be >= 400.

        Parameters
        ----------
        status_code : int
            Status code.

        Raises
        ------
        ValueError
            If the status code is less than 400.
        """
        if status_code < 400:
            raise ValueError('status code must be >= 400')

        self.status_code = status_code


class BadRequestError(HTTPError):
    """HTTP 400 Bad request"""

    def __init__(self, message: str = 'Bad request'):
        """HTTP 400 Bad request

        Parameters
        ----------
        message : str, optional
            Exception message, by default 'Bad request'.
        """
        super().__init__(message, 400)


class NotFoundError(HTTPError):
    """HTTP 404 Not found"""

    def __init__(self, message: str = 'Not found'):
        """HTTP 404 Not found

        Parameters
        ----------
        message : str, optional
            Exception message, by default 'Not found'.
        """
        super().__init__(message, 404)


class UnauthorizedError(HTTPError):
    """HTTP 401 Unauthorized"""

    def __init__(self, message: str = 'Unauthorized'):
        """HTTP 401 Unauthorized

        Parameters
        ----------
        message : str, optional
            Exception message, by default 'Unauthorized'.
        """
        super().__init__(message, 401)


class ForbiddenError(HTTPError):
    """HTTP 403 Forbidden"""

    def __init__(self, message: str = 'Forbidden'):
        """HTTP 403 Forbidden

        Parameters
        ----------
        message : str, optional
            Exception message, by default 'Forbidden'.
        """
        super().__init__(message, 403)
