"""This module contains authentication and authorization enums."""

from utils.enums import StrEnum, auto


class Roles(StrEnum):
    ADMIN = auto()
    USER = auto()
