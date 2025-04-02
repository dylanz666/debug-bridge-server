from pydantic import BaseModel
from typing import Literal, Optional


class ScreenAction(BaseModel):
    action: Literal[
        "click", "double_click", "hover", "select", "drag", "mouse_right", "keyboard_input", "touch", "touch_down", "touch_up", "touch_move", "input_text", "input_key_event"]
    start_x: Optional[int] = None
    start_y: Optional[int] = None
    start_x_percent: Optional[float] = None
    start_y_percent: Optional[float] = None
    end_x: Optional[int] = None
    end_y: Optional[int] = None
    end_x_percent: Optional[float] = None
    end_y_percent: Optional[float] = None
    main_key: Optional[str] = None
    bind_key: Optional[str] = None
    device_id: Optional[str] = None
    text: Optional[str] = None
