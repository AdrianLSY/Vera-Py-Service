from pydantic import Field
from core.models import Service, Token
from typing import Annotated, Literal, Union
from core.actions import ActionRunner, ActionModel

class PhxReplyEvent(ActionRunner):
    """
    Represents a Phoenix reply event that can either be a successful response or an error.

    Attributes:
        ref (Optional[str]): A reference identifier for the event.
        topic (str): The topic to which the event is associated.
        event (Literal["phx_reply"]): A literal indicating the event type "phx_reply".
        payload (Union[PhxReplyOk, PhxReplyError]): The reply payload which is discriminated by the 'status' field.
    """
    class PhxReplyOk(ActionModel):
        """
        Represents a successful Phoenix reply event.

        Attributes:
            status (Literal["ok"]): A literal value "ok" indicating a successful response.
            response (Response): The successful reply payload.
        """
        class Response(ActionModel):
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

            def description(self) -> str:
                return "Represents a successful reply response that contains service information."

        status: Literal["ok"] = Field(description = "A literal value \"ok\" indicating a successful response.")
        response: Response = Field(description = "The successful reply payload containing service, token and information.")

        def description(self) -> str:
            return "Represents a successful Phoenix reply event."

    class PhxReplyError(ActionModel):
        """
        Represents an error Phoenix reply event.

        Attributes:
            status (Literal["error"]): A literal value "error" indicating an error response.
            response (Response): The error reply payload containing the reason for the error.
        """
        class Response(ActionModel):
            """
            Represents an error reply response with a reason for the error.

            Attributes:
                reason (str): The reason for the error.
            """
            reason: str = Field(description = "The reason for the error.")

            def description(self) -> str:
                return "Represents an error reply response with a reason for the error."

        status: Literal["error"] = Field(description = "A literal value \"error\" indicating an error response.")
        response: Response = Field(description = "The error reply payload containing the reason for the error.")

        def description(self) -> str:
            return "Represents an error Phoenix reply event."

    ref: str = Field(description = "A reference identifier for the event.", default = None)
    topic: str = Field(description = "The topic to which the event is associated.")
    event: Literal["phx_reply"] = Field(description = "A literal indicating the event type \"phx_reply\".")
    payload: Annotated[
        Union[
            PhxReplyOk,
            PhxReplyError
        ],
        Field(discriminator = "status")
    ] = Field(description = "The reply payload which is discriminated by the 'status' field.")

    def description(self) -> str:
        return "Represents a Phoenix reply event that can either be a successful response or an error response."

    def run(self) -> str:
        print(self.model_dump_json(indent = 4))
