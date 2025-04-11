from typing import Optional, Dict, Type
from json import dumps, loads, JSONDecodeError
from pydantic import BaseModel, ValidationError
from core.actions import ActionRegistry, ActionRunner
from websockets import connect, ClientConnection, ConnectionClosed
from core.models import Service, Event, PhxJoinEvent, PhxReplyEvent, PhxReplyOk, PhxReplyError, ServiceUpdatedEvent, ServiceDeletedEvent, ClientsConnectedEvent, RequestEvent

class PlugboardClient(BaseModel):
    """
    This class represents a client for the Plugboard application.
    It provides methods for connecting to the Plugboard application and handling events.

    Attributes:
        service (Optional[Service]): The service object associated with the client.
        clients_connected (int): The number of clients connected to the service.
        connected (bool): A flag indicating whether this client is connected to the service.

    Methods:
        connect(service_id: int): Connects to the Plugboard application and handles events.
        __handle_phx_join_event(event: PhxJoinEvent): Handles a join event.
        __handle_phx_reply_event(event: PhxReplyEvent): Handles a reply event.
        __handle_service_updated_event(event: ServiceUpdatedEvent): Handles a service updated event.
        __handle_service_deleted_event(event: ServiceDeletedEvent): Handles a service deleted event.
    """
    service: Optional[Service] = None
    clients_connected: int = 0
    connected: bool = False

    async def connect(self, websocket_url: str, service_id: str | int) -> None:
        """
        Connects to the Plugboard application and handles events.

        Args:
            websocket_url (str): The URL of the websocket to connect to.
            service_id (str | int): The ID of the service to connect to.

        Raises:
            JSONDecodeError: If the JSON message cannot be decoded.
            ValidationError: If the event is not recognized.
            ConnectionClosed: If the connection is closed.
        """
        async with connect(websocket_url) as websocket:
            self.connected = True
            actions = ActionRegistry.actions()
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
                    if not self.connected:
                        await websocket.close()

                    message = loads(await websocket.recv())
                    print(message)
                    event = Event(**message)

                    if isinstance(event.root, PhxJoinEvent):
                        await self.__handle_phx_join_event(event.root, websocket, actions)
                    elif isinstance(event.root, PhxReplyEvent):
                        await self.__handle_phx_reply_event(event.root, websocket, actions)
                    elif isinstance(event.root, ServiceUpdatedEvent):
                        await self.__handle_service_updated_event(event.root, websocket, actions)
                    elif isinstance(event.root, ServiceDeletedEvent):
                        await self.__handle_service_deleted_event(event.root, websocket, actions)
                    elif isinstance(event.root, ClientsConnectedEvent):
                        await self.__handle_clients_connected_event(event.root, websocket, actions)
                    elif isinstance(event.root, RequestEvent):
                        await self.__handle_request_event(event.root, websocket, actions)
                    else:
                        print(f"Unknown event")
                        print(event.model_dump_json(indent = 4))
                except JSONDecodeError:
                    print(f"Invalid JSON")
                except ValidationError:
                    print(f"Invalid event")
                except ConnectionClosed:
                    break

    async def __handle_phx_join_event(self, event: PhxJoinEvent, websocket: ClientConnection, actions: Dict[str, Type[ActionRunner]]) -> None:
        """
        Handles a join event.

        Args:
            event (PhxJoinEvent): The join event to handle.

        Returns:
            None
        """
        print("PHX join event:")
        print(event.model_dump_json(indent = 4))

    async def __handle_phx_reply_event(self, event: PhxReplyEvent, websocket: ClientConnection, actions: Dict[str, Type[ActionRunner]]) -> None:
        """
        Handles a reply event.

        Args:
            event (PhxReplyEvent): The reply event to handle.

        Returns:
            None
        """
        def handle_phx_reply_ok(event: PhxReplyOk) -> None:
            self.service = event.response.service
            self.clients_connected = event.response.clients_connected
            print("PHX reply ok event:")
            print(event.model_dump_json(indent = 4))

        def handle_phx_reply_error(event: PhxReplyError) -> None:
            self.connected = False
            print("PHX reply error event:")
            print(event.model_dump_json(indent = 4))

        if isinstance(event.payload, PhxReplyOk):
            handle_phx_reply_ok(event.payload)
        else:
            handle_phx_reply_error(event.payload)

    async def __handle_service_updated_event(self, event: ServiceUpdatedEvent, websocket: ClientConnection, actions: Dict[str, Type[ActionRunner]]) -> None:
        """
        Handles a service updated event.

        Args:
            event (ServiceUpdatedEvent): The service updated event to handle.

        Returns:
            None
        """
        self.service = event.payload.service
        print("Service updated event:")
        print(event.model_dump_json(indent = 4))

    async def __handle_service_deleted_event(self, event: ServiceDeletedEvent, websocket: ClientConnection, actions: Dict[str, Type[ActionRunner]]) -> None:
        """
        Handles a service deleted event.

        Args:
            event (ServiceDeletedEvent): The service deleted event to handle.

        Returns:
            None
        """
        self.service = None
        self.connected = False
        print("Service deleted event:")
        print(event.model_dump_json(indent = 4))

    async def __handle_clients_connected_event(self, event: ClientsConnectedEvent, websocket: ClientConnection, actions: Dict[str, Type[ActionRunner]]) -> None:
        """
        Handles a clients connected event.

        Args:
            event (ClientsConnectedEvent): The clients connected event to handle.

        Returns:
            None
        """
        self.clients_connected = event.payload.clients_connected
        print("Clients connected event:")
        print(event.model_dump_json(indent = 4))

    async def __handle_request_event(self, event: RequestEvent, websocket: ClientConnection, actions: Dict[str, Type[ActionRunner]]) -> None:
        """
        Handles a request event.

        Args:
            event (RequestEvent): The request event to handle.

        Returns:
            None
        """
        print("Request event:")
        print(event.model_dump_json(indent = 4))
        if event.payload.response_ref is None:
            return
        await websocket.send(
            dumps(
                {
                    "topic": event.topic,
                    "event": "response",
                    "payload": actions[event.payload.action](**event.payload.fields).run(),
                    "ref": event.payload.response_ref
                }
            )
        )
