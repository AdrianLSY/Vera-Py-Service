from pydantic import RootModel, BaseModel, Field
from typing import Annotated, Literal, Optional, Union

class Service(BaseModel):
    """
    Represents a service with a unique identifier and a name.

    Attributes:
        id (int): The unique identifier for the service.
        name (str): The name of the service.
    """
    id: int
    name: str


class PhxJoinPayload(BaseModel):
    """
    Represents the payload for a Phoenix join event.

    Attributes:
        None: This model does not include any fields.
    """
    pass


class PhxJoinEvent(BaseModel):
    """
    Represents a Phoenix join event.

    Attributes:
        ref (Union[str, None]): A reference identifier for the event.
        topic (str): The topic to which the event is associated.
        event (Literal["phx_join"]): A literal indicating the event type "phx_join".
        payload (PhxJoinPayload): The payload of the join event.
    """
    ref: Union[str, None]
    topic: str
    event: Literal["phx_join"]
    payload: PhxJoinPayload


class PhxReplyOkResponse(BaseModel):
    """
    Represents a successful reply response that contains service information.

    Attributes:
        service (Service): The service information included in the response.
        clients_connected (int): The number of clients connected to the service.
    """
    service: Service
    clients_connected: int


class PhxReplyOk(BaseModel):
    """
    Represents a successful Phoenix reply event.

    Attributes:
        status (Literal["ok"]): A literal value "ok" indicating a successful response.
        response (PhxReplyOkResponse): The successful reply payload.
    """
    status: Literal["ok"]
    response: PhxReplyOkResponse


class PhxReplyErrorResponse(BaseModel):
    """
    Represents an error reply response with a reason for the error.

    Attributes:
        reason (str): The reason for the error.
    """
    reason: str


class PhxReplyError(BaseModel):
    """
    Represents an error Phoenix reply event.

    Attributes:
        status (Literal["error"]): A literal value "error" indicating an error response.
        response (PhxReplyErrorResponse): The error reply payload containing the reason for the error.
    """
    status: Literal["error"]
    response: PhxReplyErrorResponse


class PhxReplyEvent(BaseModel):
    """
    Represents a Phoenix reply event that can either be a successful response or an error.

    Attributes:
        ref (Union[str, None]): A reference identifier for the event.
        topic (str): The topic to which the event is associated.
        event (Literal["phx_reply"]): A literal indicating the event type "phx_reply".
        payload (Union[PhxReplyOk, PhxReplyError]): The reply payload which is discriminated by the 'status' field.
    """
    ref: Union[str, None]
    topic: str
    event: Literal["phx_reply"]
    payload: Annotated[
        Union[
            PhxReplyOk,
            PhxReplyError
        ],
        Field(discriminator = "status")
    ]


class ServiceUpdatedPayload(BaseModel):
    """
    Represents the payload for a service update event.

    Attributes:
        service (Service): The updated service information.
    """
    service: Service


class ServiceUpdatedEvent(BaseModel):
    """
    Represents an event indicating that a service has been updated.

    Attributes:
        ref (Union[str, None]): A reference identifier for the event.
        topic (str): The topic to which the event is associated.
        event (Literal["service_updated"]): A literal indicating the event type "service_updated".
        payload (ServiceUpdatedPayload): The payload containing updated service information.
    """
    ref: Union[str, None]
    topic: str
    event: Literal["service_updated"]
    payload: ServiceUpdatedPayload


class ServiceDeletedPayload(BaseModel):
    """
    Represents the payload for a service deletion event.

    Attributes:
        service (Service): The service information that was deleted.
    """
    service: Service


class ServiceDeletedEvent(BaseModel):
    """
    Represents an event indicating that a service has been deleted.

    Attributes:
        ref (Union[str, None]): A reference identifier for the event.
        topic (str): The topic to which the event is associated.
        event (Literal["service_deleted"]): A literal indicating the event type "service_deleted".
        payload (ServiceDeletedPayload): The payload containing the service information that was deleted.
    """
    ref: Union[str, None]
    topic: str
    event: Literal["service_deleted"]
    payload: ServiceDeletedPayload


class ClientsConnectedPayload(BaseModel):
    """
    Represents the payload for a clients connected event.

    Attributes:
        clients_connected (int): The number of clients connected to the service.
    """
    clients_connected: int


class ClientsConnectedEvent(BaseModel):
    """
    Represents an event indicating that the number of clients connected to the service has changed.

    Attributes:
        ref (Union[str, None]): A reference identifier for the event.
        topic (str): The topic to which the event is associated.
        event (Literal["clients_connected"]): A literal indicating the event type "clients_connected".
        payload (ClientsConnectedPayload): The payload containing the number of clients connected to the service.
    """
    ref: Union[str, None]
    topic: str
    event: Literal["clients_connected"]
    payload: ClientsConnectedPayload


class RequestPayload(BaseModel):
    """
    Represents the payload for a request event.

    Attributes:
        action (str): The name of the action to run.
        fields (dict): The fields to pass to the action.
        response_ref (Optional[str]): The reference to send a response for the request.
    """
    action: str
    fields: dict
    response_ref: Optional[str] = None


class RequestEvent(BaseModel):
    """
    Represents a request event that can be either a join or reply event.

    Attributes:
        ref (Union[str, None]): A reference identifier for the event.
        topic (str): The topic to which the event is associated.
        event (Literal["request"]): A literal indicating the event type "request".
        payload (RequestPayload): The payload containing the request information.
    """
    ref: Union[str, None]
    topic: str
    event: Literal["request"]
    payload: RequestPayload


class Event(
    RootModel[
        Annotated[
            Union[
                PhxJoinEvent,
                PhxReplyEvent,
                ServiceUpdatedEvent,
                ServiceDeletedEvent,
                ClientsConnectedEvent,
                RequestEvent
            ],
            Field(discriminator = "event")
        ]
    ]
):
    """
    Represents a generic event that can be one of several types including join, reply, service updated, or service deleted events.

    The event type is discriminated by the "event" field, which determines the specific model to use:
        - "phx_join" for PhxJoinEvent.
        - "phx_reply" for PhxReplyEvent.
        - "service_updated" for ServiceUpdatedEvent.
        - "service_deleted" for ServiceDeletedEvent.
        - "clients_connected" for ClientsConnectedEvent.
        - "request" for RequestEvent.
    """
    pass
