import os.path
import subprocess
import sys
import threading
import time
from io import BytesIO

import pyautogui
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse

from domain.command import Command
from domain.screen_action import ScreenAction
from screenshots import device_screenshots
from utils.data_util import DataUtil
from utils.file_util import FileUtil
from utils.random_util import RandomUtil
from utils.screen_action_util import ScreenActionUtil
from utils.screenshot_util import ScreenshotUtil
from uvicorn import run
from typing import Optional
import re
from pyscrcpy import Client
import cv2 as cv
from PIL import Image
from cachetools import TTLCache
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pid_mapper_file = "pid_mapper.json"
FileUtil.makedirs_if_not_exist("output")
FileUtil.create_file_if_not_exist(pid_mapper_file)


@app.get("/", summary="ping", deprecated=False)
async def ping():
    return "success"


@app.get("/ping", summary="ping", deprecated=False)
async def ping():
    return "success"


@app.post("/bridge/run")
async def run_command(command: Command):
    """
    run command
    :param command: request body, it's a Command object, such as: {"command":"ipconfig"}
    :return: response body, including: status, message, pid
    """
    env = os.environ.copy()
    # disable stdout buffer to make it able to get log immediately
    env["PYTHONUNBUFFERED"] = "1"

    if command.command is None or command.command == "":
        return {
            "status": "fail",
            "message": "No command provided!"
        }
    random_output_file_path = f"output/{RandomUtil.get_random_string(10)}.txt"
    with open(random_output_file_path, 'w') as file:
        process = subprocess.Popen(command.command, stdout=file, stderr=file, text=True, shell=True, env=env)
    DataUtil.set_data(pid_mapper_file, f"pid_{process.pid}", {
        "command": command.command,
        "output": random_output_file_path
    })
    return {
        "status": "success",
        "message": f"The command is executed~",
        "pid": process.pid
    }


@app.get("/bridge/content/all")
async def get_bridge_content_by_pid(pid: int):
    """
    get all log content for specific process
    :param pid: process id
    :return: response body, including status, message, command, content
    """
    output_file_path = DataUtil.get_data_by_jsonpath(pid_mapper_file, f"pid_{pid}.output")
    if not output_file_path or not os.path.exists(output_file_path):
        return {
            "status": "fail",
            "message": f"Cannot find content related to your pid {pid}, please double check!"
        }
    command = DataUtil.get_data_by_jsonpath(pid_mapper_file, f"pid_{pid}.command")
    content = FileUtil.read_lines(output_file_path)
    return {
        "status": "success",
        "command": command,
        "content": content
    }


@app.get("/bridge/content")
async def get_bridge_content(pid: int, start_line: int = Query(0, ge=0), line_length: int = Query(20, ge=1)):
    """
    get all log content for specific process with start line and line length
    :param pid: process id
    :param start_line: start line of log content
    :param line_length: how much line you want to get, default is 20
    :return: response body, including status, message, command, content
    """
    output_file_path = DataUtil.get_data_by_jsonpath(pid_mapper_file, f"pid_{pid}.output")
    if not output_file_path or not os.path.exists(output_file_path):
        return {
            "status": "fail",
            "message": f"Cannot find content related to your pid {pid}, please double check!",
            "content": []
        }
    start_line = int(start_line) - 1
    line_length = int(line_length)
    content = []
    try:
        with open(output_file_path, 'r') as file:
            for _ in range(start_line):
                next(file, None)
            for _ in range(line_length):
                line = file.readline()
                if not line:
                    break
                content.append(line)
        command = DataUtil.get_data_by_jsonpath(pid_mapper_file, f"pid_{pid}.command")
        return {
            "status": "success",
            "command": command,
            "content": content
        }
    except IOError as e:
        return {
            "status": "fail",
            "message": f"Error reading file of pid: {str(e)}",
            "content": []
        }


@app.get("/bridge/pids")
async def get_pids():
    """
    get all existing pids which are saved to pid mapper json file
    :return: response body, including status, pids, all pids details
    """
    pid_mapper = DataUtil.get_data(pid_mapper_file)
    pids = []
    for pid in pid_mapper:
        pids.append(pid[4:])
    pids = pids[::-1]
    return {
        "status": "success",
        "pids": pids,
        "details": pid_mapper
    }


@app.post("/bridge/pids/clear")
async def clear_all_pids():
    """
    stop all processes and delete their log content files
    :return: response body, including status, message, quantity
    """
    output_files = FileUtil.list_all_files("output")
    file_deleted_quantity = 0
    for file in output_files:
        try:
            FileUtil.remove_if_exist(file)
            file_deleted_quantity += 1
        except PermissionError:
            print(f"cannot remove file: {file}")
            pass
    # close pid
    pid_mapper = DataUtil.get_data(pid_mapper_file)
    quantity = 0
    for pid in pid_mapper:
        quantity += 1
        os.system(f"taskkill /F /PID {pid[4:]}")
    # delete pid_mapper_file
    FileUtil.clear(pid_mapper_file)
    clear_quantity = file_deleted_quantity if file_deleted_quantity < quantity else quantity
    return {
        "status": "success",
        "quantity": clear_quantity,
        "message": f"{clear_quantity} pids have been cleared~"
    }


@app.post("/bridge/pid/clear")
async def clear_pid(pid: int):
    """
    stop process and delete it's log content file
    :param pid: process id
    :return: response body, including status, message, pid
    """
    os.system(f"taskkill /F /PID {pid}")

    output_file_path = DataUtil.get_data_by_jsonpath(pid_mapper_file, f"pid_{pid}.output")
    FileUtil.remove_if_exist(output_file_path)
    data = DataUtil.get_data(pid_mapper_file)
    del data[f"pid_{pid}"]
    FileUtil.clear(pid_mapper_file)
    DataUtil.write_json(pid_mapper_file, data)
    return {
        "status": "success",
        "pid": pid,
        "message": f"Clear PID: {pid}, Success~"
    }


@app.post("/bridge/pid/stop")
async def stop_pid(pid: int):
    """
    stop pid
    :param pid: process id
    :return: response body, including status, message, pid
    """
    os.system(f"taskkill /F /PID {pid}")
    return {
        "status": "success",
        "pid": pid,
        "message": f"Stop PID: {pid}, Success~"
    }


@app.get("/bridge/screenshot")
async def get_desktop_screenshot():
    """
    get desktop screenshot
    :return: desktop screenshot
    """
    img = ScreenshotUtil.get_screenshot()
    output_stream = BytesIO()
    img.save(output_stream, 'JPEG')
    output_stream.seek(0)
    return StreamingResponse(output_stream, media_type='image/jpeg')


@app.get("/bridge/screen_size")
async def get_screen_size(device_id: Optional[str] = None):
    """
    get screen size
    :param device_id: android device's serial number
    :return: screen size
    """
    width = 0
    height = 0
    if not device_id:
        width, height = pyautogui.size()
        return {
            "width": width,
            "height": height
        }
    try:
        args = ['adb', '-s', device_id, 'shell', 'wm size']
        result = subprocess.run(args, capture_output=True, text=True, check=True)
        output = result.stdout.strip()
        # output sample: Physical size: 1920x1200
        match = re.search(r'(\d+)x(\d+)', output)
        width = int(match.group(1)) if match else 0
        height = int(match.group(2)) if match else 0
    except subprocess.CalledProcessError as e:
        pass
    finally:
        return {
            "width": width,
            "height": height
        }


@app.post("/bridge/screen_action")
async def do_screen_action(screen_action: ScreenAction):
    """
    do screen action
    :param screen_action: object
    :return: response body, including status, message, screen_action
    """
    if screen_action.action == "click":
        ScreenActionUtil.click(screen_action)
    if screen_action.action == "double_click":
        ScreenActionUtil.double_click(screen_action)
    if screen_action.action == "hover":
        ScreenActionUtil.hover(screen_action)
    if screen_action.action == "select":
        ScreenActionUtil.select(screen_action)
    if screen_action.action == "drag":
        ScreenActionUtil.drag(screen_action)
    if screen_action.action == "mouse_right":
        ScreenActionUtil.mouse_right(screen_action)
    if screen_action.action == "keyboard_input":
        ScreenActionUtil.keyboard_input(screen_action)
    return {
        "status": "success",
        "screen_action": screen_action
    }


@app.get("/bridge/adb_devices")
async def get_adb_devices():
    """
    get result of 'adb devices'
    :return: android devices
    """
    try:
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, check=True)

        devices_output = result.stdout.strip().split('\n')[1:]
        device_sn_list = []

        for line in devices_output:
            if line.strip():
                device_info = line.split()
                device_sn = device_info[0]
                device_sn_list.append(device_sn)

        return device_sn_list
    except subprocess.CalledProcessError as e:
        print(f"Error executing adb command: {e}")
        return []


# # cache dict
# cache = {}
# # cache duration
cache_duration = 3


@app.get("/bridge/adb_screenshot")
async def do_adb_screenshot(device_id: str):
    """
    do adb screenshot
    :param device_id: android device's serial number
    :return: screenshot of current android device
    """
    try:
        if device_id in device_screenshots:
            cached_img_stream, screenshot_time = device_screenshots[device_id]
            if (time.time() - screenshot_time) > cache_duration:
                thread = threading.Thread(target=ScreenshotUtil.get_adb_screenshot, args=(device_id,))
                thread.start()
            return StreamingResponse(BytesIO(cached_img_stream), media_type='image/jpeg')

        thread = threading.Thread(target=ScreenshotUtil.get_adb_screenshot, args=(device_id,))
        thread.start()
        return JSONResponse(status_code=200, content={"message": "Please wait..."})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/bridge/device_ip")
async def get_device_ip(device_id: str):
    """
    get device ip
    :param device_id: android device's serial number
    :return: response body
    """
    try:
        command = f'adb -s {device_id} shell ip route'
        result = subprocess.run(command, capture_output=True, text=True, check=True, shell=True)

        match = re.search(r'src (\d+\.\d+\.\d+\.\d+)', result.stdout)
        if match:
            device_ip = match.group(1)  # 获取匹配的 IP 地址
        else:
            raise ValueError("IP address not found in the output")

        return {
            "status": "success",
            "device_id": device_id,
            "device_ip": device_ip
        }
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return {
            "status": "failed",
            "device_id": device_id,
            "device_ip": ""
        }
    except Exception as e:
        print(f"Error: {e}")
        return {
            "status": "failed",
            "device_id": device_id,
            "device_ip": ""
        }


@app.post("/bridge/device/wake_up")
async def wake_up_device(device_id: str):
    """
    wake up device
    :param device_id: android device's serial number
    :return: response body
    """
    try:
        command = f'adb -s {device_id} shell input keyevent KEYCODE_WAKEUP'
        subprocess.run(command, capture_output=True, text=True, check=True, shell=True)

        return {
            "status": "success",
            "device_id": device_id,
            "message": "Your device has woken up"
        }
    except Exception as e:
        return {
            "status": "failed",
            "device_id": device_id,
            "message": f"Failed to wake up your device, error: {e}"
        }


@app.post("/bridge/device/reboot")
async def reboot_device(device_id: str):
    """
    reboot device
    :param device_id: android device's serial number
    :return: response body
    """
    try:
        command = f'adb -s {device_id} reboot'
        subprocess.run(command, capture_output=True, text=True, check=True, shell=True)

        return {
            "status": "success",
            "device_id": device_id,
            "message": "Your device has rebooted"
        }
    except Exception as e:
        return {
            "status": "failed",
            "device_id": device_id,
            "message": f"Failed to reboot your device, error: {e}"
        }


# below is for demo usage
# app.include_router(product.router)
# app.include_router(user.router)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide port number, such as 8001")
        sys.exit(1)
    port = int(sys.argv[1])
    run(app, host='0.0.0.0', port=port, log_config="log-config.yaml")
