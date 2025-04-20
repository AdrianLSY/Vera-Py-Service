from typing import Optional, Dict, Type
from json import dumps, loads, JSONDecodeError
from pydantic import BaseModel, ValidationError
from core.actions import ActionRegistry, ActionRunner
from websockets import connect, ClientConnection, ConnectionClosed
from core.models import Service, Event, PhxJoinEvent, PhxReplyEvent, PhxReplyOk, PhxReplyError, ServiceUpdatedEvent, ServiceDeletedEvent, ConsumersConnectedEvent, RequestEvent, Token, TokenCreatedEvent, TokenDeletedEvent

class PlugboardClient(BaseModel):
    """
    This class represents a client for the Plugboard application.
    It provides methods for connecting to the Plugboard application and handling events.

    Attributes:
        service (Optional[Service]): The service object associated with the client.
        token (Optional[Token]): The token object associated with the client.
        consumers_connected (int): The number of clients connected to the service.
        connected (bool): A flag indicating whether this client is connected to the service.

    Methods:
        connect(service_id: int): Connects to the Plugboard application and handles events.

    Private Methods:
        __handle_phx_join_event(event: PhxJoinEvent): Handles a join event.
        __handle_phx_reply_event(event: PhxReplyEvent): Handles a reply event.
        __handle_service_updated_event(event: ServiceUpdatedEvent): Handles a service updated event.
        __handle_service_deleted_event(event: ServiceDeletedEvent): Handles a service deleted event.
        __handle_consumers_connected_event(event: ConsumersConnectedEvent): Handles a clients connected event.
        __handle_request_event(event: RequestEvent): Handles a request event.
        __handle_token_created_event(event: TokenCreatedEvent): Handles a token created event.
        __handle_token_deleted_event(event: TokenDeletedEvent): Handles a token deleted event.
    """
    service: Optional[Service] = None
    token: Token = Token()
    consumers_connected: int = 0
    connected: bool = False

    async def connect(self, websocket_url: str, service_id: str | int, token: str) -> None:
        """
        Connects to the Plugboard application and handles events.

        Args:
            websocket_url (str): The URL of the websocket to connect to.
            service_id (str | int): The ID of the service to connect to.
            token (str): The token to use for authentication.

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
                        "topic": f"service/{service_id}",
                        "event": "phx_join",
                        "payload": {
                            "token": token,
                            "actions": ActionRegistry.dict()
                        },
                        "ref": None
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
                        await self.__handle_phx_join_event(event.root,)
                    elif isinstance(event.root, PhxReplyEvent):
                        await self.__handle_phx_reply_event(event.root, token)
                    elif isinstance(event.root, ServiceUpdatedEvent):
                        await self.__handle_service_updated_event(event.root)
                    elif isinstance(event.root, ServiceDeletedEvent):
                        await self.__handle_service_deleted_event(event.root)
                    elif isinstance(event.root, ConsumersConnectedEvent):
                        await self.__handle_consumers_connected_event(event.root)
                    elif isinstance(event.root, RequestEvent):
                        await self.__handle_request_event(event.root, websocket, actions)
                    elif isinstance(event.root, TokenCreatedEvent):
                        await self.__handle_token_created_event(event.root)
                    elif isinstance(event.root, TokenDeletedEvent):
                        await self.__handle_token_deleted_event(event.root)
                    else:
                        print(f"Unknown event")
                        print(event.model_dump_json(indent = 4))
                except JSONDecodeError:
                    print(f"Invalid JSON")
                except ValidationError as error:
                    print(f"Invalid event: {error}")
                except ConnectionClosed:
                    break

    async def __handle_phx_join_event(self, event: PhxJoinEvent) -> None:
        """
        Handles a join event.

        Args:
            event (PhxJoinEvent): The join event to handle.

        Returns:
            None
        """
        print("PHX join event:")
        print(event.model_dump_json(indent = 4))

    async def __handle_phx_reply_event(self, event: PhxReplyEvent, token: str) -> None:
        """
        Handles a reply event.

        Args:
            event (PhxReplyEvent): The reply event to handle.
            token (str): The token used for authentication.

        Returns:
            None
        """
        def handle_phx_reply_ok(event: PhxReplyOk, token: str) -> None:
            self.service = event.response.service
            self.consumers_connected = event.response.consumers_connected
            self.token = event.response.token
            self.token.value = token
            print("PHX reply ok event:")
            print(event.model_dump_json(indent = 4))

        def handle_phx_reply_error(event: PhxReplyError) -> None:
            self.connected = False
            print("PHX reply error event:")
            print(event.model_dump_json(indent = 4))

        if isinstance(event.payload, PhxReplyOk):
            handle_phx_reply_ok(event.payload, token)
        else:
            handle_phx_reply_error(event.payload)

    async def __handle_service_updated_event(self, event: ServiceUpdatedEvent) -> None:
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

    async def __handle_service_deleted_event(self, event: ServiceDeletedEvent) -> None:
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

    async def __handle_consumers_connected_event(self, event: ConsumersConnectedEvent) -> None:
        """
        Handles a clients connected event.

        Args:
            event  ConsumersConnectedEvent): The clients connected event to handle.

        Returns:
            None
        """
        self.consumers_connected = event.payload.consumers_connected
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
        response = {
            "message": None,
            "status": None
        }
        try:
            response["message"] = actions[event.payload.action](**event.payload.fields).run()
            response["status"] = "success"
        except KeyError:
            response["message"] = f"Unknown action: {event.payload.action}"
            response["status"] = "error"
        except ValidationError:
            response["message"] = f"Mallformed action fields"
            response["status"] = "error"
        except Exception as error:
            response["message"] = error
            response["status"] = "error"
        await websocket.send(
            dumps(
                {
                    "topic": event.topic,
                    "event": "response",
                    "payload": response,
                    "ref": event.payload.response_ref
                }
            )
        )

    async def __handle_token_created_event(self, event: TokenCreatedEvent) -> None:
        """
        Handles a token created event.

        Args:
            event (TokenCreatedEvent): The token created event to handle.

        Returns:
            None
        """
        self.token = event.payload.token
        print("Token created event:")
        print(event.model_dump_json(indent = 4))

    async def __handle_token_deleted_event(self, event: TokenDeletedEvent) -> None:
        """
        Handles a token deleted event.

        Args:
            event (TokenDeletedEvent): The token deleted event to handle.

        Returns:
            None
        """
        print("Token deleted event:")
        print(event.model_dump_json(indent = 4))
