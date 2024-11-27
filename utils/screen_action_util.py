import time

import pyautogui

from domain.screen_action import ScreenAction


class ScreenActionUtil:
    def __init__(self) -> None:
        pass

    @staticmethod
    def click(screen_action: ScreenAction):
        pyautogui.moveTo(screen_action.start_x, screen_action.start_y)
        pyautogui.click()

    @staticmethod
    def double_click(screen_action: ScreenAction):
        pyautogui.moveTo(screen_action.start_x, screen_action.start_y)
        pyautogui.doubleClick()

    @staticmethod
    def hover(screen_action: ScreenAction):
        pyautogui.moveTo(screen_action.start_x, screen_action.start_y, duration=0.5)
        time.sleep(2)

    @staticmethod
    def select(screen_action: ScreenAction):
        # move to start position
        pyautogui.moveTo(screen_action.start_x, screen_action.start_y, duration=0.25)
        # hold the left key of mouse
        pyautogui.mouseDown()
        # move to end position to select
        pyautogui.moveTo(screen_action.end_x, screen_action.end_y, duration=0.25)
        # release mouse
        pyautogui.mouseUp()

    @staticmethod
    def drag(screen_action: ScreenAction):
        pyautogui.moveTo(screen_action.start_x, screen_action.start_y, duration=0.5)
        pyautogui.dragTo(screen_action.end_x, screen_action.end_y, duration=1)

    @staticmethod
    def mouse_right(screen_action):
        pyautogui.moveTo(screen_action.start_x, screen_action.start_y, duration=0.5)
        pyautogui.click(button='right')

    @staticmethod
    def keyboard_input(screen_action):
        main_key = screen_action.main_key
        bind_key = screen_action.bind_key
        if main_key is None or main_key == "":
            return
        control_keys = ["enter", "delete", "backspace", "escape", "capslock", "shift", "alt", "up", "down", "left",
                        "right", "tab"]
        lower_main_key = main_key.lower()
        if lower_main_key in control_keys and (bind_key is None or bind_key == ""):
            main_key = main_key.lower()
            pyautogui.press(main_key)
            return
        if lower_main_key == "control" and (bind_key is None or bind_key == ""):
            main_key = "ctrl"
            pyautogui.press(main_key)
            return
        if lower_main_key == "control" and bind_key is not None and bind_key != "":
            pyautogui.hotkey('ctrl', bind_key)
            return
        if lower_main_key in ["shift", "alt"] and bind_key is not None and bind_key != "":
            pyautogui.hotkey(lower_main_key, bind_key)
            return
        pyautogui.typewrite(main_key)
