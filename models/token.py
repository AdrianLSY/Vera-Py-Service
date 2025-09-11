from datetime import datetime
from typing import override

from pydantic import Field

from core.action_model import ActionModel


class Token(ActionModel):
    """
    Represents a token with a unique identifier, context, value, service id, and inserted and expiration date.
    The token defaults to all None values. The Token fields will be set when the PlugboardClient is connected.

    Attributes:
        id (Optional[int]): The unique identifier for the token.
        context (str | None): The context for the token.
        value (str | None): The value for the token.
        service_id (Optional[int]): The ID of the service associated with the token.
        inserted_at (Optional[datetime]): The date and time the token was inserted.
        expires_at (Optional[datetime]): The date and time the token expires.
    """
    id: int | None = Field(description = "The unique identifier for the token.", default = None)
    context: str | None = Field(description = "The context for the token.", default = None)
    value: str | None = Field(description = "The value for the token.", default = None)
    service_id: int | None = Field(description = "The ID of the service associated with the token.", default = None)
    inserted_at: datetime | None = Field(description = "The date and time the token was inserted.", default = None)
    expires_at: datetime | None = Field(description = "The date and time the token expires.", default = None)

    @classmethod
    @override
    def description(cls) -> str:
        return "Represents a token with a unique identifier, context, value, service id, and inserted and expiration date."
