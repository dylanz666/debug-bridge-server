from pydantic import BaseModel
from typing import Literal


class ScreenAction(BaseModel):
    action: Literal["click", "double_click", "hover", "select", "drag"]
    start_x: int
    start_y: int
    end_x: int
    end_y: int
