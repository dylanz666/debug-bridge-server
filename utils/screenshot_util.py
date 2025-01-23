import time

import pyautogui
import win32gui
import win32ui
import win32con
from PIL import Image
import subprocess
from io import BytesIO

from screenshots import device_screenshots

screenshotting_device_ids = []


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
        try:
            print("Take screenshot...")
            result = subprocess.run(
                ["adb", "-s", device_id, "exec-out", "screencap", "-p"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5
            )

            if result.returncode != 0:
                return {"error": "Failed to capture screenshot by adb", "details": result.stderr.decode()}

            img = Image.open(BytesIO(result.stdout))
            new_width = int(img.width * 0.4)
            new_height = int(img.height * 0.4)
            img = img.resize((new_width, new_height))
            # set image's quality to 40% of original one
            output_stream = BytesIO()
            img.convert("RGB").save(output_stream, format='JPEG', quality=40)
            output_stream.seek(0)

            device_screenshots[device_id] = (output_stream.getvalue(), time.time())

            return {"message": "success", "device_id": device_id}
        except subprocess.TimeoutExpired:
            return {"error": "Timeout expired while trying to capture screenshot."}
        except Exception as e:
            return {"error": "An error occurred.", "details": str(e)}
