"""This module provides the ``BaseDTO`` class
to define Data Transfer Objects (DTOs).
"""

from pydantic import BaseModel


class BaseDTO(BaseModel):
    """Base class for Data Transfer Objects (DTOs)."""

    def to_dict(self) -> dict[str, object]:
        """Serialize DTO to dict.

        Returns
        -------
        dict[str, object]
            Serialized DTO.
        """
        return self.model_dump()

    @classmethod
    def from_model(cls, obj: object) -> 'BaseDTO':
        """Converts a model object to a DTO
        in order to be serialized.

        Parameters
        ----------
        obj : object
            Model object.

        Returns
        -------
        BaseDTO
            The parsed DTO object.
        """
        return cls.model_validate(obj)

    @classmethod
    def from_model_many(cls, objs: list[object]) -> list['BaseDTO']:
        """Converts a list of model objects to DTOs
        in order to be serialized.

        Parameters
        ----------
        objs : list[object]
            List of model objects.

        Returns
        -------
        list[BaseDTO]
            List of parsed DTO objects.
        """
        return [cls.from_model(obj) for obj in objs]

    class Config:
        from_attributes = True


class BaseRequestDTO(BaseDTO):
    """Base DTO class for the body of requests."""

    pass


class BaseResponseDTO(BaseDTO):
    """Base DTO class for responses."""

    def to_response(self) -> dict[str, object]:
        """Serialize DTO to dict.

        Returns
        -------
        dict[str, object]
            Serialized DTO.
        """
        response = self.to_dict()
        for key, value in response.items():
            if isinstance(value, BaseResponseDTO):
                response[key] = value.to_response()
            elif isinstance(value, list):
                for item in value:
                    response[key] = (
                        item.to_response()
                        if isinstance(item, BaseResponseDTO)
                        else item
                    )
            else:
                response[key] = value

        return response
