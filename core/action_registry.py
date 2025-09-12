from importlib import import_module
from inspect import getmembers, isclass
from os import listdir
from os.path import exists
from typing import Any, Dict, Type

from core.action_schema import ActionSchema
from core.action_runner import ActionRunner


class ActionRegistry():
    """
    A registry for ActionRunner classes.
    The ActionRegistry provides a way to dynamically load all Action classes that match the specified action_type from the specified directory.

    Static Methods:
        valid_action_types() -> list[Type]: Returns a list of valid action types.
        discover(path: str, action_type: Type) -> Dict[str, Type[ActionSchema]]: Dynamically discovers and loads all Action classes that match the specified action_type from the specified directory.

    Methods:
        actions(path: str, action_type: Type) -> Dict[str, Type[ActionSchema]]: Dynamically loads all Action classes that match the specified action_type from the specified directory.
        dict(path: str = "actions") -> dict: Returns a dictionary containing the dictionary schemas for all ActionRunner classes.
        json(path: str = "actions", indent: int = None) -> str: Returns a JSON string containing the JSON schemas for all ActionRunner classes.
    """

    @staticmethod
    def valid_action_types() -> list[Type[Any]]:
        """
        Returns a list of valid action types.

        Returns:
            list[Type]: A list of valid action types.
        """
        return [ActionSchema, ActionRunner]

    @staticmethod
    def discover(path: str, action_type: Type[Any]) -> Dict[str, Type[ActionSchema]]:
        """
        Load classes of specified action_type from directory.

        Args:
            path: Directory containing action classes
            action_type: Type to match (ActionSchema or ActionRunner)

        Raises:
            ValueError: If action_type is not a valid action type

        Returns:
            Dictionary of {discriminator: class}
        """
        if not exists(path):
            return {}

        if action_type not in ActionRegistry.valid_action_types():
            raise ValueError(f"Invalid action type: {action_type}")

        actions: Dict[str, Type[ActionSchema]] = {}
        module_prefix = path.replace("/", ".")

        for filename in listdir(path):
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = f"{module_prefix}.{filename[:-3]}"
                module = import_module(module_name)
                for _, obj in getmembers(module, lambda x: isclass(x) and x.__base__ == action_type):
                    actions[obj.discriminator()] = obj

        return actions

    @staticmethod
    def actions(path: str, action_type: Type[Any]) -> Dict[str, Type[ActionSchema]]:
        """
        Dynamically loads all Action classes that match the specified action_type from the specified directory.

        Args:
            path (str): Directory containing action classes
            action_type (Type[Any]): Type to match (ActionSchema or ActionRunner)

        Returns:
            Dict[str, Type[ActionSchema]]: Dictionary of {discriminator: class}
        """
        return ActionRegistry.discover(path, action_type)

    @staticmethod
    def dict(path: str = "actions") -> dict[str, Any]:
        """
        Returns a dictionary containing the dictionary schemas for all ActionRunner classes.

        Args:
            path (str): Directory containing action classes. Defaults to "actions".

        Returns:
            dict[str, Any]: Dictionary containing the schemas for all ActionRunner classes.
        """
        actions = ActionRegistry.discover(path, ActionRunner)
        result: dict[str, Any] = {}
        for action_class in actions.values():
            result.update(action_class.to_dict())
        return result

    @staticmethod
    def json(path: str = "actions", indent: int | None = None) -> str:
        """
        Returns a JSON string containing the JSON schemas for all ActionRunner classes.

        Args:
            path (str): Directory containing action classes. Defaults to "actions".
            indent (int | None): The indentation level for the JSON schema. Defaults to None.

        Returns:
            str: JSON string containing the schemas for all ActionRunner classes.
        """
        from json import dumps
        return dumps(ActionRegistry.dict(path), indent = indent)
