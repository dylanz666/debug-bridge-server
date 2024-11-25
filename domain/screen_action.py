from pydantic import BaseModel
from typing import Literal, Optional


class ScreenAction(BaseModel):
    action: Literal["click", "double_click", "hover", "select", "drag", "mouse_right"]
    start_x: int
    start_y: int
    end_x: Optional[int] = None
    end_y: Optional[int] = None
