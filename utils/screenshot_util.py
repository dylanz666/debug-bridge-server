import pyautogui
import win32gui
import win32ui
import win32con
from PIL import Image
import subprocess
from io import BytesIO


class ScreenshotUtil:
    def __init__(self) -> None:
        pass

    @staticmethod
    def get_screenshot():
        # 获取屏幕尺寸
        width, height = pyautogui.size()
        print(f"Scaled screen width: {width}, Scaled screen height: {height}")

        # 创建设备上下文
        hwndDC = win32gui.GetWindowDC(0)  # 0 表示整个屏幕
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()

        # 创建位图
        saveBitMap = win32ui.CreateBitmap()
        saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
        saveDC.SelectObject(saveBitMap)

        # 从屏幕复制到位图
        saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)

        # 获取位图数据
        bmpstr = saveBitMap.GetBitmapBits(True)

        # 创建图像
        img = Image.frombuffer('RGB', (width, height), bmpstr, 'raw', 'BGRX', 0, 1)

        # 清理资源
        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(0, hwndDC)

        return img

    @staticmethod
    def get_adb_screenshot(device_id):
        process = subprocess.Popen(
            ["adb", "-s", device_id, "exec-out", "screencap", "-p"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            return {"error": "Failed to capture screenshot by adb", "details": stderr.decode()}
        return Image.open(BytesIO(stdout))
