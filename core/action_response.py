from typing import Any, Union, override

from pydantic import Field

from core.action_schema import ActionSchema


class ActionResponse(ActionSchema):
    status_code: int = Field(description = "The HTTP status code of the response")
    message: Union[str, None] = Field(description = "The message of the response", default = None)
    fields: Union[str, int, float, bool, dict[str, Any], None] = Field(description = "The fields of the response", default = None)

    @classmethod
    @override
    def description(cls) -> str:
        return "The schema used as a standard response returned by ActionRunner.run()"
