from abc import ABC, abstractmethod
from json import dumps, loads
from typing import Any, Type, cast

from pydantic import BaseModel


class ActionSchema(BaseModel, ABC):
    """
    Base class for action action_schemas.
    The ActionSchema is a base class for defining an action. It provides a common interface for defining actions and their respective fields.

    Subclasses of ActionSchema must implement the description() method.
    """

    @classmethod
    def discriminator(cls) -> str:
        """
        Discriminator is used to identify the action. Defaults to the class name.

        Returns
            str: The discriminator for the action.
        """
        return cls.__name__

    @classmethod
    @abstractmethod
    def description(cls) -> str:
        """
        Returns the description for the action. Must be implemented by subclasses.
        The description should describe the purpose of the action.

        Returns:
            str: The description of the action.
        """
        pass

    @classmethod
    def to_dict(cls) -> dict[str, Any]:
        """
        Returns the action_schema definition as a dictionary.

        Returns:
            dict: The action_schema definition as a dictionary.
        """
        def check_subclass(class_type: type | None, parent_cls: type) -> bool:
            if class_type is None:
                return False
            return issubclass(class_type, parent_cls)

        schema = cls.model_json_schema()
        class_name = cls.__name__
        properties = schema.get("properties", {})

        fields: dict[str, Any] = {}
        for field_name, field_schema in properties.items():
            field_type = field_schema.get("type")

            # Handle nested ActionSchema fields
            if "$ref" in field_schema:
                field_class = cls.model_fields[field_name].annotation
                if check_subclass(field_class, ActionSchema):
                    # Explicitly cast field_class to Type[ActionSchema]
                    action_schema_class = cast(Type[ActionSchema], field_class)

                    # Now use action_schema_class instead of field_class
                    nested_fields: dict[str, Any] = {}
                    nested_fields["type"] = action_schema_class.discriminator()
                    nested_fields["description"] = action_schema_class.description()
                    nested_fields["fields"] = next(
                        iter(
                            loads(
                                action_schema_class.to_json()
                            ).values()
                        )
                    )["fields"]
                    fields[field_name] = nested_fields
                    continue

            field_data: dict[str, Any] = {
                "type": field_type,
                "description": field_schema.get("description"),
                "default": field_schema.get("default") if "default" in field_schema else None
            }
            field_info: dict[str, Any] = {
                key: value
                for key, value in field_data.items()
                if key != "default" or ("default" in field_schema)
            }
            fields[field_name] = field_info

        return {
            class_name: {
                "description": cls.description(),
                "fields": fields
            }
        }

    @classmethod
    def to_json(cls, indent: int | None = None) -> str:
        """
        Returns the action_schema definition as a JSON schema.

        Args:
            indent (int, optional): The indentation level for the JSON schema. Defaults to None.

        Returns:
            str: The JSON schema for the action action_schema.
        """
        return dumps(cls.to_dict(), indent = indent)
