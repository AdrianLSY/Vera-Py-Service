from pydantic import BaseModel
from abc import ABC, abstractmethod
from json import dumps

class Action(BaseModel, ABC):

    @abstractmethod
    def description(self) -> str:
        """
        Returns the description for the action. Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def run(self) -> any:
        """
        Execute the action. Must be implemented by subclasses.
        """
        pass

    def model_json(self, indent: int = None) -> str:
        """
        Returns the model definition as a JSON schema.
        """
        schema = self.model_json_schema()
        class_name = self.__class__.__name__
        properties = schema.get('properties', {})

        return dumps(
            {
                class_name: {
                    "description": self.description(),
                    "fields": {
                        field_name: {
                            key: value
                            for key, value in {
                                "type": field_schema.get('type'),
                                "description": field_schema.get('description'),
                                "default": field_schema.get('default') if 'default' in field_schema else None
                            }.items()
                            if key != 'default' or ('default' in field_schema)
                        }
                        for field_name, field_schema in properties.items()
                    }
                }
            },
            indent = indent
        )