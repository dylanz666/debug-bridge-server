import os
import time

import pyautogui

from domain.screen_action import ScreenAction


class ScreenActionUtil:
    def __init__(self) -> None:
        pass

    @staticmethod
    def click(screen_action: ScreenAction):
        start_x = screen_action.start_x
        start_y = screen_action.start_y
        device_id = screen_action.device_id
        if device_id is not None and device_id != "":
            os.system(f"adb -s {device_id} shell input tap {start_x} {start_y}")
            return
        try:
            pyautogui.moveTo(start_x, start_y)
            pyautogui.click()
        except pyautogui.FailSafeException:
            pass

    @staticmethod
    def double_click(screen_action: ScreenAction):
        start_x = screen_action.start_x
        start_y = screen_action.start_y
        device_id = screen_action.device_id
        if device_id is not None and device_id != "":
            os.system(f"adb -s {device_id} shell input tap {start_x} {start_y}")
            time.sleep(0.1)
            os.system(f"adb -s {device_id} shell input tap {start_x} {start_y}")
            return
        try:
            pyautogui.moveTo(start_x, start_y)
            pyautogui.doubleClick()
        except pyautogui.FailSafeException:
            pass

    @staticmethod
    def hover(screen_action: ScreenAction):
        start_x = screen_action.start_x
        start_y = screen_action.start_y
        device_id = screen_action.device_id
        if device_id is not None and device_id != "":
            os.system(f"adb -s {device_id} shell input touchscreen swipe {start_x} {start_y} {start_x} {start_y} 0")
            return
        try:
            pyautogui.moveTo(start_x, start_y, duration=0.5)
            time.sleep(2)
        except pyautogui.FailSafeException:
            pass

    @staticmethod
    def select(screen_action: ScreenAction):
        start_x = screen_action.start_x
        start_y = screen_action.start_y
        end_x = screen_action.end_x
        end_y = screen_action.end_y
        device_id = screen_action.device_id
        if device_id is not None and device_id != "":
            os.system(f"adb -s {device_id} shell input touchscreen swipe {start_x} {start_y} {start_x} {start_y} 0")
            os.system(f"adb -s {device_id} shell input touchscreen swipe {start_x} {start_y} {end_x} {end_y} 100")
            return
        try:
            # move to start position
            pyautogui.moveTo(start_x, start_y, duration=0.25)
            # hold the left key of mouse
            pyautogui.mouseDown()
            # move to end position to select
            pyautogui.moveTo(end_x, end_y, duration=0.25)
            # release mouse
            pyautogui.mouseUp()
        except pyautogui.FailSafeException:
            pass

    @staticmethod
    def drag(screen_action: ScreenAction):
        start_x = screen_action.start_x
        start_y = screen_action.start_y
        end_x = screen_action.end_x
        end_y = screen_action.end_y
        device_id = screen_action.device_id
        if device_id is not None and device_id != "":
            os.system(f"adb -s {device_id} shell input touchscreen swipe {start_x} {start_y} {end_x} {end_y} 500")
            return
        try:
            pyautogui.moveTo(start_x, start_y, duration=0.5)
            pyautogui.dragTo(end_x, end_y, duration=1)
        except pyautogui.FailSafeException:
            pass

    @staticmethod
    def mouse_right(screen_action):
        device_id = screen_action.device_id
        if device_id is not None and device_id != "":
            return
        try:
            pyautogui.moveTo(screen_action.start_x, screen_action.start_y, duration=0.5)
            pyautogui.click(button='right')
        except pyautogui.FailSafeException:
            pass

    @staticmethod
    def keyboard_input(screen_action):
        main_key = screen_action.main_key
        if main_key is None or main_key == "":
            return

        device_id = screen_action.device_id
        if device_id is not None and device_id != "":
            os.system(f"adb -s {device_id} shell input text {main_key}")
            return

        bind_key = screen_action.bind_key
        control_keys = ["enter", "delete", "backspace", "escape", "capslock", "shift", "alt", "up", "down", "left",
                        "right", "tab"]
        lower_main_key = main_key.lower()
        try:
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
        except pyautogui.FailSafeException:
            pass
