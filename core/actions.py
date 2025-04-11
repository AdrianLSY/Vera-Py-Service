from json import dumps, loads
from pydantic import BaseModel
from abc import ABC, abstractmethod

class ActionModel(BaseModel, ABC):
    """
    Base class for action models.
    The ActionModel is a base class for defining an action. It provides a common interface for defining actions and their respective fields.

    Subclasses of ActionModel must implement the description() and run() methods.
    """
    @abstractmethod
    def description(self) -> str:
        """
        Returns the description for the action. Must be implemented by subclasses.
        The description should describe the purpose of the action.

        Returns:
            str: The description of the action.
        """
        pass

    def model_json(self, indent: int = None) -> str:
        """
        Returns the model definition as a JSON schema.

        Args:
            indent (int, optional): The indentation level for the JSON schema. Defaults to None.

        Returns:
            str: The JSON schema for the action model.
        """
        schema = self.model_json_schema()
        class_name = self.__class__.__name__
        properties = schema.get('properties', {})

        fields = {}
        for field_name, field_schema in properties.items():
            field_value = getattr(self, field_name)
            if isinstance(field_value, ActionModel):
                nested_fields = {}
                nested_fields['type'] = field_value.__class__.__name__
                nested_fields['description'] = field_value.description()
                nested_fields['fields'] = next(
                    iter(
                        loads(
                            field_value.model_json()
                        ).values()
                    )
                )['fields']
                fields[field_name] = nested_fields
            else:
                field_info = {
                    key: value
                    for key, value in {
                        "type": field_schema.get('type'),
                        "description": field_schema.get('description'),
                        "default": field_schema.get('default') if 'default' in field_schema else None
                    }.items()
                    if key != 'default' or ('default' in field_schema)
                }
                fields[field_name] = field_info
        return dumps(
            {
                class_name: {
                    "description": self.description(),
                    "fields": fields
                }
            },
            indent = indent
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
