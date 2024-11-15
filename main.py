import os.path
import subprocess
from io import BytesIO

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

from utils.data_util import DataUtil
from utils.file_util import FileUtil
from utils.random_util import RandomUtil
from utils.screenshot_util import ScreenshotUtil

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pid_mapper_file = "pid_mapper.json"


class Command(BaseModel):
    command: str


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
async def get_bridge_content_by_pid(pid):
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
async def get_bridge_content(pid, start_line=0, line_length=20):
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
    with open(output_file_path, 'r') as file:
        for _ in range(start_line):
            try:
                next(file)
            except RuntimeError:
                pass
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
async def clear_pid(pid):
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
async def stop_pid(pid):
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
async def get_desktop_screenshot(scale):
    """
    get desktop screenshot
    :param scale: your screen's scale, such as 1, 1.25, 1.5, 1.75, 2, 2.25
    :return: desktop screenshot
    """
    img = ScreenshotUtil.get_screenshot(scale=float(scale))
    output_stream = BytesIO()
    img.save(output_stream, 'JPEG')
    output_stream.seek(0)
    return StreamingResponse(output_stream, media_type='image/jpeg')


FileUtil.makedirs_if_not_exist("output")
FileUtil.create_file_if_not_exist(pid_mapper_file)

# below is for demo usage
# app.include_router(product.router)
# app.include_router(user.router)
