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
    The ActionRunner inherits from ActionSchema and provides a common interface for for defining actions and their respective fields.
    In addition, it provides a common interface for executing the action.

    Class Methods:
        discriminator(cls) -> str: Returns the event discriminator for the action. Defaults to the class name.
        description(cls) -> str: Returns the description for the action. Must be implemented by subclasses.
        run(self, client: "PlugboardClient", websocket: ClientConnection) -> str: Executes the action.
        to_dict(cls) -> dict: Returns the schema definition as a dictionary.
        to_json(cls, indent: int = None) -> str: Returns the schema definition as a JSON schema.

    Subclasses of ActionRunner must implement the run() and description() method.
    """

    @abstractmethod
    async def run(self, client: "PlugboardClient", websocket: ClientConnection) -> ActionResponse:
        """
        Execute the action. Must be implemented by subclasses.
        Implementing class must return an ActionResponse
        """
        raise NotImplementedError
