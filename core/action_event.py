from inspect import isawaitable
from typing import TYPE_CHECKING, Callable, ClassVar, Any, Awaitable

from websockets import ClientConnection

from core.action_schema import ActionSchema

if TYPE_CHECKING:
    from core.plugboard_client import PlugboardClient


class ActionEvent(ActionSchema):
    """
    ActionEvent delegates to a callback (sync or async). `run()` does not return anything.

    Subclasses MAY set `callback` to a callable taking (client, websocket).
    If not set, run() is a no-op.
    """
    callback: ClassVar[Callable[["PlugboardClient", ClientConnection], Any | Awaitable[Any]]] | None = None

    async def run(self, client: "PlugboardClient", websocket: ClientConnection, *args: Any, **kwargs: Any) -> None:
        if self.callback is None:
            return

        result = self.callback(client, websocket, *args, **kwargs)
        if isawaitable(result):
            await result
