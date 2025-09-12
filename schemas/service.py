from datetime import datetime
from typing import override

from pydantic import Field

from core.action_schema import ActionSchema


class Service(ActionSchema):
    """
    Represents a service with a unique identifier and a name.

    Attributes:
        id (int): The unique identifier for the service.
        name (str): The name of the service.
        inserted_at (datetime): The date and time the service was inserted.
        updated_at (datetime): The date and time the service was last updated.
    """
    id: int = Field(description = "The unique identifier for the service.")
    name: str = Field(description = "The name of the service.")
    inserted_at: datetime = Field(description = "The date and time the service was inserted.")
    updated_at: datetime = Field(description = "The date and time the service was last updated.")

    @classmethod
    @override
    def description(cls) -> str:
        return "Represents a service with a unique identifier and a name."
