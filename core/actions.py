from os import listdir
from os.path import exists
from json import dumps, loads
from pydantic import BaseModel
from typing import Any, Dict, Type
from abc import ABC, abstractmethod
from importlib import import_module
from inspect import getmembers, isclass

class ActionModel(BaseModel, ABC):
    """
    Base class for action models.
    The ActionModel is a base class for defining an action. It provides a common interface for defining actions and their respective fields.

    Subclasses of ActionModel must implement the description() and run() methods.
    """
    @classmethod
    @abstractmethod
    def description(self) -> str:
        """
        Returns the description for the action. Must be implemented by subclasses.
        The description should describe the purpose of the action.

        Returns:
            str: The description of the action.
        """
        pass

    @classmethod
    def model_json(cls, indent: int = None) -> str:
        """
        Returns the model definition as a JSON schema.

        Args:
            indent (int, optional): The indentation level for the JSON schema. Defaults to None.

        Returns:
            str: The JSON schema for the action model.
        """
        schema = cls.model_json_schema()
        class_name = cls.__name__
        properties = schema.get('properties', {})

        fields = {}
        for field_name, field_schema in properties.items():
            field_type = field_schema.get('type')

            # Handle nested ActionModel fields
            if '$ref' in field_schema:
                field_class = cls.model_fields[field_name].annotation
                if issubclass(field_class, ActionModel):
                    nested_fields = {}
                    nested_fields['type'] = field_class.__name__
                    nested_fields['description'] = field_class.description()
                    nested_fields['fields'] = next(
                        iter(
                            loads(
                                field_class.model_json()
                            ).values()
                        )
                    )['fields']
                    fields[field_name] = nested_fields
                    continue

            field_info = {
                key: value
                for key, value in {
                    "type": field_type,
                    "description": field_schema.get('description'),
                    "default": field_schema.get('default') if 'default' in field_schema else None
                }.items()
                if key != 'default' or ('default' in field_schema)
            }
            fields[field_name] = field_info

        return dumps(
            {
                class_name: {
                    "description": cls.description(),
                    "fields": fields
                }
            },
            indent=indent
        )


class ActionRunner(ActionModel):
    """
    Base class for action runners.
    The ActionRunner inherits from ActionModel and provides a common interface for for defining actions and their respective fields.
    In addition, it provides a common interface for executing the action.

    Subclasses of ActionRunner must implement the run() and description() method.
    """
    @abstractmethod
    def run(self) -> any:
        """
        Execute the action. Must be implemented by subclasses.
        """
        pass


class ActionRegistry():
    """
    A registry for ActionRunner classes.
    The ActionRegistry provides a way to dynamically load all ActionRunner classes from the actions directory.

    Methods:
        load_actions(): Dynamically loads all ActionRunner classes from the actions directory.
    """

    @staticmethod
    def actions(path: str = "actions") -> Dict[str, Type[ActionRunner]]:
        """
        Dynamically loads all ActionRunner classes from the actions directory.

        Args:
            path (str, optional): The path to the actions directory. Defaults to actions.

        Returns:
            Dict[str, Type[ActionRunner]]: Dictionary mapping class names to ActionRunner classes
        """
        if not exists(path):
            return {}
        actions: Dict[str, Type[ActionRunner]] = {}
        for filename in listdir(path):
            if filename.endswith('.py') and filename != '__init__.py':
                # Change this line to use the full module path
                module_path = path.replace("/", ".").split(".")[-2:]
                module_name = f"{'.'.join(module_path)}.{filename[:-3]}"
                for name, obj in getmembers(import_module(module_name)):
                    if isclass(obj) and issubclass(obj, ActionRunner) and obj != ActionRunner:
                        actions[name] = obj
        return actions

    @staticmethod
    def json(path: str = "actions", indent: int = None) -> str:
        """
        Returns a JSON string containing the JSON schemas for all ActionRunner classes.

        Args:
            path (str, optional): The path to the actions directory. Defaults to actions/.
            indent (int, optional): The indentation level for the JSON schema. Defaults to None.

        Returns:
            str: A JSON string containing the JSON schemas for all ActionRunner classes.
        """
        actions = ActionRegistry.actions(path)
        schemas: Dict[str, Dict[str, Any]] = {}

        for name, action in actions.items():
            schemas[name] = loads(action.model_json())[name]

        return dumps(schemas, indent = indent)
