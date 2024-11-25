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
