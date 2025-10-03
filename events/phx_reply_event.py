from typing import Annotated, Literal

from pydantic import Field

from core.action_schema import ActionSchema
from core.action_event import ActionEvent
from schemas.service import Service
from schemas.token import Token

class PhxReplyEvent(ActionEvent):
    """
    Represents a Phoenix reply event that can either be a successful response or an error.

    Attributes:
        ref (str | None): A reference identifier for the event.
        topic (str): The topic to which the event is associated.
        event (Literal["phx_reply"]): A literal indicating the event type "phx_reply".
        payload (PhxReplyOk | PhxReplyError): The reply payload which is discriminated by the "status" field.
    """
    class PhxReplyOk(ActionSchema):
        """
        Represents a successful Phoenix reply event.

        Attributes:
            status (Literal["ok"]): A literal value "ok" indicating a successful response.
            response (Response): The successful reply payload.
        """
        class Response(ActionSchema):
            """
            Represents a successful reply response that contains service information.

            Attributes:
                service (Service): The service information included in the response.
                token (Token): The api token information included in the response.
                num_consumers (int): The number of clients connected to the service.
            """
            service: Service = Field(description = "The service information included in the response.")
            token: Token = Field(description = "The api token information included in the response.")
            num_consumers: int = Field(description = "The number of consumers connected to the service.")

            @classmethod
            def description(cls) -> str:
                return "Represents a successful reply response that contains service information."

        status: Literal["ok"] = Field(description = "A literal value \"ok\" indicating a successful response.")
        response: Response = Field(description = "The successful reply payload containing service, token and information.")

        @classmethod
        def description(cls) -> str:
            return "Represents a successful Phoenix reply event."

    class PhxReplyError(ActionSchema):
        """
        Represents an error Phoenix reply event.

        Attributes:
            status (Literal["error"]): A literal value "error" indicating an error response.
            response (Response): The error reply payload containing the reason for the error.
        """
        class Response(ActionSchema):
            """
            Represents an error reply response with a reason for the error.

            Attributes:
                reason (str): The reason for the error.
            """
            reason: str = Field(description = "The reason for the error.")

            @classmethod
            def description(cls) -> str:
                return "Represents an error reply response with a reason for the error."

        status: Literal["error"] = Field(description = "A literal value \"error\" indicating an error response.", default = "error")
        response: Response = Field(description = "The error reply payload containing the reason for the error.")

        @classmethod
        def description(cls) -> str:
            return "Represents an error Phoenix reply event."

    ref: str | None = Field(description = "A reference identifier for the event.", default = None)
    topic: str = Field(description = "The topic to which the event is associated.")
    event: Literal["phx_reply"] = Field(description = "A literal indicating the event type \"phx_reply\".", default = "phx_reply")
    payload: Annotated[
        PhxReplyOk | PhxReplyError,
        Field(discriminator = "status")
    ] = Field(description = "The reply payload which is discriminated by the 'status' field.")

    @classmethod
    def discriminator(cls) -> str:
        return "phx_reply"

    @classmethod
    def description(cls) -> str:
        return "Represents a Phoenix reply event that can either be a successful response or an error response."
