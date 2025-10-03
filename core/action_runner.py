from abc import abstractmethod
from typing import TYPE_CHECKING

from websockets import ClientConnection

from core.action_schema import ActionSchema
from core.action_response import ActionResponse

if TYPE_CHECKING:
    from core.plugboard_client import PlugboardClient

class ActionRunner(ActionSchema):
    """
    Base class for action runners.
    """

    @abstractmethod
    async def run(self, client: "PlugboardClient", websocket: ClientConnection) -> ActionResponse:
        raise NotImplementedError
