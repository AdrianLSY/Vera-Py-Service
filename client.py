from asyncio import run
from typing import Optional
from json import dumps, loads, JSONDecodeError
from pydantic import BaseModel, ValidationError
from websockets import connect, ConnectionClosed
from models import Service, Event, PhxJoinEvent, PhxReplyEvent, PhxReplyOk, PhxReplyError, ServiceUpdatedEvent, ServiceDeletedEvent

class PlugboardClient(BaseModel):
    """
    This class represents a client for the Plugboard application.
    It provides methods for connecting to the Plugboard application and handling events.

    Attributes:
        service (Optional[Service]): The service object associated with the client.

    Methods:
        connect(service_id: int): Connects to the Plugboard application and handles events.
        __handle_phx_join_event(event: PhxJoinEvent): Handles a join event.
        __handle_phx_reply_event(event: PhxReplyEvent): Handles a reply event.
        __handle_service_updated_event(event: ServiceUpdatedEvent): Handles a service updated event.
        __handle_service_deleted_event(event: ServiceDeletedEvent): Handles a service deleted event.
    """
    service: Optional[Service] = None

    async def connect(self, service_id: int) -> None:
        """
        Connects to the Plugboard application and handles events.

        Args:
            service_id (int): The ID of the service to connect to.

        Raises:
            JSONDecodeError: If the JSON message cannot be decoded.
            ValidationError: If the event is not recognized.
            ConnectionClosed: If the connection is closed.
        """
        async with connect("ws://localhost:4000/backend/websocket") as websocket:
            await websocket.send(
                dumps(
                    {
                        "topic": f"backend/service/{service_id}",
                        "event": "phx_join",
                        "payload": {},
                        "ref": "1"
                    }
                )
            )
            while True:
                try:
                    event = Event(**loads(await websocket.recv()))
                    if isinstance(event.root, PhxJoinEvent):
                        self.__handle_phx_join_event(event.root)
                        continue
                    if isinstance(event.root, PhxReplyEvent):
                        self.__handle_phx_reply_event(event.root)
                        continue
                    if isinstance(event.root, ServiceUpdatedEvent):
                        self.__handle_service_updated_event(event.root)
                        continue
                    if isinstance(event.root, ServiceDeletedEvent):
                        self.__handle_service_deleted_event(event.root)
                        continue
                except JSONDecodeError:
                    print("Failed to decode JSON message.")
                except ValidationError:
                    print("Received invalid message.")
                except ConnectionClosed:
                    print("WebSocket connection closed.")
                    break

    def __handle_phx_join_event(self, event: PhxJoinEvent) -> None:
        """
        Handles a join event.

        Args:
            event (PhxJoinEvent): The join event to handle.

        Returns:
            None
        """
        print("Join event received.")
        print(event.model_dump_json(indent=4))

    def __handle_phx_reply_event(self, event: PhxReplyEvent) -> None:
        """
        Handles a reply event.

        Args:
            event (PhxReplyEvent): The reply event to handle.

        Returns:
            None
        """
        def handle_phx_reply_ok(event: PhxReplyOk) -> None:
            self.service = event.response.service

        def handle_phx_reply_error(event: PhxReplyError) -> None:
            print(f"Error: {event.response.reason}")

        if isinstance(event.payload, PhxReplyOk):
            handle_phx_reply_ok(event.payload)
        else:
            handle_phx_reply_error(event.payload)

        print("Reply event received.")
        print(event.model_dump_json(indent=4))

    def __handle_service_updated_event(self, event: ServiceUpdatedEvent) -> None:
        """
        Handles a service updated event.

        Args:
            event (ServiceUpdatedEvent): The service updated event to handle.

        Returns:
            None
        """
        self.service = event.payload.service
        print("Service updated event received.")
        print(event.model_dump_json(indent=4))

    def __handle_service_deleted_event(self, event: ServiceDeletedEvent) -> None:
        """
        Handles a service deleted event.

        Args:
            event (ServiceDeletedEvent): The service deleted event to handle.

        Returns:
            None
        """
        self.service = None
        print("Service deleted event received.")
        print(event.model_dump_json(indent=4))


if __name__ == "__main__":
    client = PlugboardClient()
    run(client.connect(service_id=1))
