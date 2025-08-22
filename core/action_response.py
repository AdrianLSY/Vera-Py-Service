from typing import Union
from pydantic import Field
from core.action_model import ActionModel

class ActionResponse(ActionModel):
    status_code: int = Field(description = "The HTTP status code of the response")
    message: Union[str, None] = Field(description = "The message of the response", default = None)
    fields: Union[str, int, float, bool, dict, None] = Field(description = "The fields of the response", default = None)

    @classmethod
    def description(cls) -> str:
        return "The model used as a standard response returned by ActionRunner.run()"
