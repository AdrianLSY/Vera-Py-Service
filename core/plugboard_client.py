from models.token import Token
from models.service import Service
from json import loads, JSONDecodeError
from core.action_runner import ActionRunner
from core.action_runner import ActionRunner
from events.phx_join_event import PhxJoinEvent
from core.action_registry import ActionRegistry
from websockets import connect, ConnectionClosed
from pydantic import BaseModel, ValidationError, Field

class PlugboardClient(BaseModel):
    """
    This class represents a client for the Plugboard application.
    It provides methods for connecting to the Plugboard application and handling events.

    Attributes:
        service (Optional[Service]): The service object associated with the client.
        token (Optional[Token]): The token object associated with the client.
        num_consumers (int): The number of clients connected to the service.
        connected (bool): A flag indicating whether this client is connected to the service.
        events (dict[str, ActionRunner]): A dictionary of event handlers.
        actions (dict[str, ActionRunner]): A dictionary of action handlers.

    Methods:
        connect(websocket_url: str, service_id: str | int, token: str): Connects to the Plugboard application and handles events.
    """
    service: Service = Field(default = None)
    token: Token = Field(default = Token())
    num_consumers: int = Field(default = 0)
    connected: bool = Field(default = False)
    events: dict[str, ActionRunner] = Field(default = ActionRegistry.discover("events", ActionRunner))
    actions: dict[str, ActionRunner] = Field(default = ActionRegistry.discover("actions", ActionRunner))

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
        if self.connected:
            return
        self.token.value = token
        async with connect(websocket_url) as websocket:
            self.connected = True

            await websocket.send(
                PhxJoinEvent(
                    topic = f"service/{service_id}",
                    payload = PhxJoinEvent.Payload(
                        token = token,
                        actions = {k: v for action in self.actions.values() for k, v in action.model_dict().items()}
                    )
                ).model_dump_json(indent = 4)
            )

            while True:
                try:
                    message = loads(await websocket.recv())
                    print(message)
                    await self.events[message["event"]](**message).run(self, websocket)
                    print(f"Client connected: {self.num_consumers}")
                    print(self.service.model_dump_json(indent = 4))
                    print(self.token.model_dump_json(indent = 4))
                except JSONDecodeError:
                    print(f"Invalid JSON")
                except KeyError:
                    print(f"Invalid message")
                except ValidationError as error:
                    print(f"Invalid event: {error}")
                except ConnectionClosed:
                    break
                except ConnectionAbortedError:
                    break

            self.connected = False
