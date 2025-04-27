from typing import cast, Type
from json import dumps, loads
from pydantic import BaseModel
from abc import ABC, abstractmethod

class ActionModel(BaseModel, ABC):
    """
    Base class for action models.
    The ActionModel is a base class for defining an action. It provides a common interface for defining actions and their respective fields.

    Subclasses of ActionModel must implement the description() method.
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
    def model_dict(cls) -> dict:
        """
        Returns the model definition as a dictionary.
    
        Returns:
            dict: The model definition as a dictionary.
        """  
        def check_subclass(class_type: type | None, parent_cls: type) -> bool:
            if class_type is None:
                return False
            return issubclass(class_type, parent_cls)
    
        schema = cls.model_json_schema()
        class_name = cls.__name__
        properties = schema.get('properties', {})
    
        fields = {}
        for field_name, field_schema in properties.items():
            field_type = field_schema.get('type')
    
            # Handle nested ActionModel fields
            if '$ref' in field_schema:
                field_class = cls.model_fields[field_name].annotation
                if check_subclass(field_class, ActionModel):
                    # Explicitly cast field_class to Type[ActionModel]
                    action_model_class = cast(Type[ActionModel], field_class)
                    
                    # Now use action_model_class instead of field_class
                    nested_fields = {}
                    nested_fields['type'] = action_model_class.discriminator()
                    nested_fields['description'] = action_model_class.description()
                    nested_fields['fields'] = next(
                        iter(
                            loads(
                                action_model_class.model_json()
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

        return{
            class_name: {
                "description": cls.description(),
                "fields": fields
            }
        }

    @classmethod
    def model_json(cls, indent: int | None = None) -> str:
        """
        Returns the model definition as a JSON schema.

        Args:
            indent (int, optional): The indentation level for the JSON schema. Defaults to None.

        Returns:
            str: The JSON schema for the action model.
        """
        return dumps(cls.model_dict(), indent = indent)
