from typing import Annotated, Literal, Union
from pydantic import RootModel, BaseModel, Field

class Service(BaseModel):
    """
    Represents a service with a unique identifier and a name.

    Attributes:
        id (int): The unique identifier for the service.
        name (str): The name of the service.
    """
    id: int
    name: str


class Phx_reply_ok_response(BaseModel):
    """
    Represents a successful reply response that contains service information.

    Attributes:
        service (Service): The service information included in the response.
    """
    service: Service


class Phx_reply_error_response(BaseModel):
    """
    Represents an error reply response with a reason for the error.

    Attributes:
        reason (str): The reason for the error.
    """
    reason: str


class Phx_reply_ok(BaseModel):
    """
    Represents a successful Phoenix reply event.

    Attributes:
        status (Literal["ok"]): A literal value "ok" indicating a successful response.
        response (Phx_reply_ok_response): The successful reply payload.
    """
    status: Literal["ok"]
    response: Phx_reply_ok_response


class Phx_reply_error(BaseModel):
    """
    Represents an error Phoenix reply event.

    Attributes:
        status (Literal["error"]): A literal value "error" indicating an error response.
        response (Phx_reply_error_response): The error reply payload containing the reason for the error.
    """
    status: Literal["error"]
    response: Phx_reply_error_response


class Service_updated_payload(BaseModel):
    """
    Represents the payload for a service update event.

    Attributes:
        service (Service): The updated service information.
    """
    service: Service


class Service_deleted_payload(BaseModel):
    """
    Represents the payload for a service deletion event.

    Attributes:
        service (Service): The service information that was deleted.
    """
    service: Service


class Phx_join_payload(BaseModel):
    """
    Represents the payload for a Phoenix join event.

    Note:
        Currently, this model does not include any fields.
    """
    pass


class Phx_join_event(BaseModel):
    """
    Represents a Phoenix join event.

    Attributes:
        ref (Union[str, None]): A reference identifier for the event.
        topic (str): The topic to which the event is associated.
        event (Literal["phx_join"]): A literal indicating the event type "phx_join".
        payload (Phx_join_payload): The payload of the join event.
    """
    ref: Union[str, None]
    topic: str
    event: Literal["phx_join"]
    payload: Phx_join_payload


class Phx_reply_event(BaseModel):
    """
    Represents a Phoenix reply event that can either be a successful response or an error.

    Attributes:
        ref (Union[str, None]): A reference identifier for the event.
        topic (str): The topic to which the event is associated.
        event (Literal["phx_reply"]): A literal indicating the event type "phx_reply".
        payload (Union[Phx_reply_ok, Phx_reply_error]): The reply payload which is discriminated by the 'status' field.
    """
    ref: Union[str, None]
    topic: str
    event: Literal["phx_reply"]
    payload: Annotated[
        Union[
            Phx_reply_ok,
            Phx_reply_error
        ],
        Field(discriminator="status")
    ]


class Service_updated_event(BaseModel):
    """
    Represents an event indicating that a service has been updated.

    Attributes:
        ref (Union[str, None]): A reference identifier for the event.
        topic (str): The topic to which the event is associated.
        event (Literal["service_updated"]): A literal indicating the event type "service_updated".
        payload (Service_updated_payload): The payload containing updated service information.
    """
    ref: Union[str, None]
    topic: str
    event: Literal["service_updated"]
    payload: Service_updated_payload


class Service_deleted_Event(BaseModel):
    """
    Represents an event indicating that a service has been deleted.

    Attributes:
        ref (Union[str, None]): A reference identifier for the event.
        topic (str): The topic to which the event is associated.
        event (Literal["service_deleted"]): A literal indicating the event type "service_deleted".
        payload (Service_deleted_payload): The payload containing the service information that was deleted.
    """
    ref: Union[str, None]
    topic: str
    event: Literal["service_deleted"]
    payload: Service_deleted_payload


class Event(
    RootModel[
        Annotated[
            Union[
                Phx_join_event,
                Phx_reply_event,
                Service_updated_event,
                Service_deleted_Event
            ],
            Field(discriminator="event")
        ]
    ]
):
    """
    Represents a generic event that can be one of several types including join, reply, service updated, or service deleted events.

    The event type is discriminated by the "event" field, which determines the specific model to use:
        - "phx_join" for Phx_join_event.
        - "phx_reply" for Phx_reply_event.
        - "service_updated" for Service_updated_event.
        - "service_deleted" for Service_deleted_Event.
    """
    pass
