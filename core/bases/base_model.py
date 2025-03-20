"""This module provides the ``BaseModel`` class
to define a base class for SQL models.
"""

from jinja2 import Template
from sqlactive import ActiveRecordBaseModel
from starlette.requests import Request


class BaseModel(ActiveRecordBaseModel):
    """Base class for SQL models."""

    __abstract__ = True

    async def __admin_repr__(self, request: Request) -> str:
        """This is a special method that can be defined
        to customize the object representation in
        the admin interface.

        By default, it returns the primary key as a string.

        Parameters
        ----------
        request : Request
            The request object.

        Returns
        -------
        str
            Object representation.
        """
        return self.id_str

    async def __admin_select2_repr__(self, request: Request) -> str:
        """This method is similar to ``__admin_repr__``, but it
        returns an HTML string that is used to display
        the object in a ``select2`` widget.

        .. warning::
            Escape all database values to avoid Cross-Site Scripting
            (XSS) attack. Jinja2 Template can be used to render with
            ``autoescape=True``::

                template_str = '<span><strong>{{ pk }}</strong></span>'
                template = Template(template_str, autoescape=True)
                return template.render(pk=self.id_str)

            For more information, visit `OWASP website <https://owasp.org/www-community/attacks/xss/>`_.

        Parameters
        ----------
        request : Request
            The request object.

        Returns
        -------
        str
            HTML object representation for ``select2`` widget.
        """
        template_str = '<span><strong>{{ pk }}</strong></span>'
        return Template(template_str, autoescape=True).render(pk=self.id_str)
