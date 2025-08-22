from typing import Union
from pydantic import BaseModel

class ActionResponse(BaseModel):
    status_code: int
    message: Union[str, None] = None
    fields: Union[str, int, float, bool, dict, None] = None
