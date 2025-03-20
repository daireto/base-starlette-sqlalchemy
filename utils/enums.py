"""This module provides custom ``enum.Enum`` classes."""

from enum import Enum, auto


class StrEnum(str, Enum):
    """Enum where members are also (and must be) strings.

    The default ``auto()`` behavior uses the member name as its value.

    Usage:
    >>> class Example(StrEnum):
    ...     UPPER_CASE = auto()
    ...     lower_case = auto()
    ...     MixedCase = auto()
    >>> assert Example.UPPER_CASE == "UPPER_CASE"
    >>> assert Example.lower_case == "lower_case"
    >>> assert Example.MixedCase == "MixedCase"
    """

    def __new__(cls, value, *args, **kwargs):
        if not isinstance(value, (str, auto)):
            raise TypeError(
                f'values of StrEnums must be strings: type of {value!r} '
                f'is {type(value)}'
            )

        return super().__new__(cls, value, *args, **kwargs)

    def __str__(self):
        return str(self.value)

    def _generate_next_value_(name, *_):
        return name
