"""This module provides the ``BaseAdminModel`` class
to generate an Admin interface for a SQLAlchemy model.
"""

from typing import TypeVar

from sqlactive.inspection import InspectionMixin
from sqlalchemy.sql.sqltypes import TIMESTAMP
from starlette_admin.contrib.sqla import ModelView
from starlette_admin.contrib.sqla.converters import BaseSQLAModelConverter
from starlette_admin.contrib.sqla.fields import MultiplePKField
from starlette_admin.contrib.sqla.helpers import extract_column_python_type
from starlette_admin.fields import (
    BaseField,
    DateField,
    DateTimeField,
    PasswordField,
    StringField,
)

InspectedBaseModel = TypeVar('InspectedBaseModel', bound=InspectionMixin)


class BaseAdminView(ModelView):

    page_size = 10
    page_size_options = [10, 25, 50, 100]

    exclude_timestamp_fields = False
    exclude_timestamp_fields_from_list = False
    exclude_timestamp_fields_from_details = False
    exclude_timestamp_fields_from_create = True
    exclude_timestamp_fields_from_edit = True
    exclude_password_fields = True

    icon: str | None = None
    name: str | None = None
    label: str | None = None
    identity: str | None = None
    converter: BaseSQLAModelConverter | None = None

    def __init_subclass__(
        cls, model: type[InspectedBaseModel], **kwargs
    ) -> None:
        super().__init_subclass__(**kwargs)
        cls.model = model

    def __init__(self):
        self.__exclude_timestamp_fields()
        if self.exclude_password_fields:
            self.__exclude_password_fields()
        super().__init__(
            self.model,
            self.icon,
            self.name,
            self.label,
            self.identity,
            self.converter,
        )

    def _setup_primary_key(self) -> None:
        """Detects the primary key attribute(s) of the model."""
        _pk_attrs = self.model.primary_keys
        if len(_pk_attrs) > 1:
            self._pk_column = tuple(
                getattr(self.model, attr) for attr in _pk_attrs
            )
            self._pk_coerce = tuple(
                extract_column_python_type(c) for c in self._pk_column
            )
            self.pk_field: BaseField = MultiplePKField(_pk_attrs)
        else:
            assert (
                len(_pk_attrs) == 1
            ), f'no primary key found in model {self.model.__name__}'
            self._pk_column = getattr(self.model, _pk_attrs[0])
            self._pk_coerce = extract_column_python_type(
                self._pk_column  # type: ignore[arg-type]
            )
            try:
                # try to find the primary key field among the fields
                self.pk_field = next(
                    f for f in self.fields if f.name == _pk_attrs[0]
                )
            except StopIteration:
                # If the primary key is not among the fields,
                # treat its value as a string
                self.pk_field = StringField(_pk_attrs[0])

        self.pk_attr = self.pk_field.name

    def __exclude_timestamp_fields(self) -> None:
        """Excludes the timestamp fields
        from the list, create and edit views.
        """
        for field in self.fields:
            _field = None
            if isinstance(field, (DateField, DateTimeField)):
                _field = field.name
            elif hasattr(field, 'type') and isinstance(field.type, TIMESTAMP):
                _field = field

            if _field:
                if (
                    self.exclude_timestamp_fields_from_list
                    or self.exclude_timestamp_fields
                ):
                    self.exclude_fields_from_list.append(field)  # type: ignore
                if (
                    self.exclude_timestamp_fields_from_details
                    or self.exclude_timestamp_fields
                ):
                    self.exclude_fields_from_detail.append(field)  # type: ignore
                if (
                    self.exclude_timestamp_fields_from_create
                    or self.exclude_timestamp_fields
                ):
                    self.exclude_fields_from_create.append(field)  # type: ignore
                if (
                    self.exclude_timestamp_fields_from_edit
                    or self.exclude_timestamp_fields
                ):
                    self.exclude_fields_from_edit.append(field)  # type: ignore

    def __exclude_password_fields(self) -> None:
        """Excludes the password fields
        from the list and detail views.
        """
        for field in self.fields:
            if isinstance(field, PasswordField):
                self.exclude_fields_from_list.append(field.name)  # type: ignore
                self.exclude_fields_from_detail.append(field.name)  # type: ignore
