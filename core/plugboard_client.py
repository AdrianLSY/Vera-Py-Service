import asyncio
from json import JSONDecodeError, dumps, loads
from typing import ClassVar, Any
from urllib.parse import quote

from pydantic import BaseModel, Field, ValidationError
from websockets import ClientConnection, ConnectionClosed, connect

from core.action_runner import ActionRunner
from events.phx_join_event import PhxJoinEvent
from schemas.service import Service
from schemas.token import Token

class PlugboardClient(BaseModel):
    """
    This class represents a singleton client for the Plugboard application.
    It provides methods for connecting to the Plugboard application and handling events.

    Attributes:
        service (Service | None): The service instance.
        token (Token): The token for authentication.
        num_consumers (int): The number of consumers.
        connected (bool): Whether the client is connected.
        actions (dict[str, type[ActionRunner]]): The actions.
    """

    service: Service | None = Field(default=None)
    token: Token = Field(default=Token())
    num_consumers: int = Field(default=0)
    connected: bool = Field(default=False)
    actions: dict[str, type[ActionRunner]] = Field(default={})
    __instance: ClassVar["PlugboardClient"] | None = None
    __instance_lock: ClassVar[asyncio.Lock] = asyncio.Lock()

    def __init__(self, *args: Any, _allow_create: bool = False, **kwargs: Any):
        if not _allow_create and self.__class__.__instance is not None:
            raise RuntimeError("PlugboardClient is a singleton. Use `await PlugboardClient.get()`")
        super().__init__(*args, **kwargs)

    @classmethod
    async def get(cls) -> "PlugboardClient":
        """
        Gets the singleton instance in an async context.

        Returns:
            PlugboardClient: The singleton instance.
        """
        if cls.__instance is None:
            async with cls.__instance_lock:
                if cls.__instance is None:
                    cls.__instance = cls(_allow_create=True)
        return cls.__instance

    async def __loop(self, websocket: ClientConnection) -> None:
        """
        Main loop for the PlugboardClient.
        """
        await websocket.send(PhxJoinEvent(topic="service").model_dump_json())
        while self.connected:
            try:
                message = loads(await websocket.recv())
                await self.actions[message["event"]](**message).run(self, websocket)
            except JSONDecodeError:
                print("Invalid JSON")
            except KeyError:
                print("Invalid message")
            except ValidationError as error:
                print(f"Invalid event: {error}")
            except ConnectionClosed:
                self.connected = False
            except ConnectionAbortedError:
                self.connected = False

    def add_action(self, name: str, action: type[ActionRunner]) -> None:
        """
        Register a single action handler.

        Raises:
            ValueError: If an action with the same name already exists.
        """
        if name in self.actions:
            raise ValueError(f"Action '{name}' is already registered")
        self.actions[name] = action

    def add_actions(self, actions: dict[str, type[ActionRunner]]) -> None:
        """
        Register multiple action handlers.

        Raises:
            ValueError: If an action with the same name already exists.
        """
        for name, action in actions.items():
            self.add_action(name, action)

    async def connect(self, websocket_url: str, token: str) -> None:
        """
        Connects to the Plugboard application and handles events.
        """
        if self.connected:
            return
        self.token.value = token
        actions_json = quote(dumps({k: v for action in self.actions.values() for k, v in action.to_dict().items()}))
        async with connect(f"{websocket_url}?token={token}&actions={actions_json}") as websocket:
            self.connected = True
            await self.__loop(websocket)
