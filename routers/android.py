import time
import subprocess
from fastapi import FastAPI, WebSocket
import cv2 as cv
import asyncio
import threading
from cachetools import TTLCache
from io import BytesIO
from PIL import Image
from starlette.responses import JSONResponse

from domain.screen_action import ScreenAction
from pyscrcpy import Client, ACTION_DOWN, ACTION_UP, ACTION_MOVE, KEYCODE_DEL, KEYCODE_ESCAPE, \
    KEYCODE_TAB, KEYCODE_SHIFT_LEFT, KEYCODE_PAGE_UP, KEYCODE_PAGE_DOWN, KEYCODE_ENTER

from fastapi import APIRouter

router = APIRouter(
    prefix='/bridge/android',
    tags=['router for android devices']
)

# 缓存字典
# 存储每个设备的帧缓存
frame_buffers = {}
# 存储每个设备
caches = {}
# 存储每个设备的 pyscrcpy server 实例
clients = {}
# 用于记录对应设备的 pyscrcpy server 是否还在启动
starting = {}
# 用于记录每个设备调用 /device_status 的情况
request_cache = {}
# 存储连接的每个设备的 WebSocket 服务端
websocket_servers = {}

# How often to sync android's screen, per second
max_fps = 24
# Max size of images that got from android
max_size = 800

# 用于线程安全的锁
buffer_lock = threading.Lock()


@router.get("/ping")
def ping_android():
    return "ping android router: success~"


@router.get("/ws")
async def websocket_endpoint(websocket: WebSocket, device_id):
    await websocket.accept()
    websocket_servers[device_id] = websocket
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message received: {data}")
    except Exception as e:
        print(f"Connection closed: {e}")
    finally:
        del websocket_servers[device_id]


@router.get("/devices")
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


@router.get("/device_status")
async def fetch_device_status(device_id):
    # 非第一次请求设备画面，判断距离第一次请求是否超过 2 秒，没超过则等待，超过则大概率 pyscrcpy server 已经启动好了
    if device_id in request_cache:
        sequence, request_time = request_cache[device_id]
        if sequence == 1 and (time.time() - request_time) <= 2:
            return JSONResponse(status_code=200, content={"message": f"Scrcpy server is starting, please wait..."})
        if sequence == 1 and (time.time() - request_time) > 2:
            new_sequence = sequence + 1
            request_cache[device_id] = (new_sequence, time.time())
    # 第一次请求设备画面，设置请求顺序为 1
    if device_id not in request_cache:
        request_cache[device_id] = (1, time.time())

    # 1. 当设备未连接到电脑的情况
    if not is_device_connected(device_id):
        return JSONResponse(status_code=200, content={"message": f"Device {device_id} is not connected, please check!"})
    # 2. 当 pyscrcpy server 没启动的情况
    if device_id not in starting or device_id not in clients:
        starting[device_id] = (True, time.time())
        start_client_by_threading(device_id)
        return JSONResponse(status_code=200, content={"message": f"Scrcpy server is not started, starting now..."})
    # 3. pyscrcpy server 已启动，设备连接正常的情况
    if clients[device_id].alive:
        starting[device_id] = (False, time.time())

        with buffer_lock:
            if device_id in caches and 'image' in caches[device_id]:
                await send_image_to_websocket_clients(device_id, caches[device_id]['image'])
                return
            starting[device_id] = (True, time.time())
            start_client_by_threading(device_id)
            return JSONResponse(status_code=500, content={"message": f"Technical issue, please refresh again!"})
    # 4. 利用缓存，避免拔插导致的一直 keep 在 starting 状态
    is_starting, starting_time = starting[device_id]
    if is_starting and (time.time() - starting_time) <= 2:
        return JSONResponse(status_code=200, content={"message": f"Scrcpy server is still starting, please wait..."})
    if is_starting and (time.time() - starting_time) > 2:
        starting[device_id] = (True, time.time())
        start_client_by_threading(device_id)
        return JSONResponse(status_code=200, content={"message": f"Fail to start scrcpy server, retrying..."})
    # 5. 设备中途掉线、恢复的情况
    if not is_starting and not clients[device_id].alive:
        starting[device_id] = (True, time.time())
        start_client_by_threading(device_id)
        return JSONResponse(status_code=200, content={"message": f"Scrcpy server is offline, restarting..."})
    # 6. 画面超过缓存时间（120 秒），强制重启
    starting[device_id] = (True, time.time())
    start_client_by_threading(device_id)
    return JSONResponse(status_code=200, content={"message": "Cache expired, restarting scrcpy server..."})


@router.post("/screen_action")
async def do_screen_action(screen_action: ScreenAction):
    if screen_action.device_id not in clients:
        return JSONResponse(status_code=400, content={"message": "Please refresh the page!"})
    x_resolution = clients[screen_action.device_id].resolution[0]
    y_resolution = clients[screen_action.device_id].resolution[1]
    control = clients[screen_action.device_id].control
    if screen_action.action == "touch_down":
        start_x = screen_action.start_x_percent * x_resolution
        start_y = screen_action.start_y_percent * y_resolution
        control.touch(x=start_x, y=start_y, action=ACTION_DOWN)
    if screen_action.action == "touch_up":
        end_x = screen_action.end_x_percent * x_resolution
        end_y = screen_action.end_y_percent * y_resolution
        control.touch(x=end_x, y=end_y, action=ACTION_UP)
    if screen_action.action == "touch_move":
        end_x = screen_action.end_x_percent * x_resolution
        end_y = screen_action.end_y_percent * y_resolution
        control.touch(x=end_x, y=end_y, action=ACTION_MOVE)
    if screen_action.action == "input_text":
        control.text(screen_action.text)
    if screen_action.action == "input_key_event":
        key_mappings = {
            'Enter': KEYCODE_ENTER,
            'Escape': KEYCODE_ESCAPE,
            'Backspace': KEYCODE_DEL,
            'Tab': KEYCODE_TAB,
            'Shift': KEYCODE_SHIFT_LEFT,
            'Delete': KEYCODE_DEL,
            'PageUp': KEYCODE_PAGE_UP,
            'PageDown': KEYCODE_PAGE_DOWN,
        }
        main_key = screen_action.main_key
        bind_key = screen_action.bind_key
        if main_key in key_mappings and (bind_key is None or bind_key == ""):
            control.keycode(keycode=key_mappings[main_key], action=ACTION_DOWN)
            control.keycode(keycode=key_mappings[main_key], action=ACTION_UP)
    return JSONResponse(status_code=200, content={
        "screen_action": screen_action.dict()
    })


# 发送数据给所有连接的客户端（目前没用到）
async def send_data_to_clients(device_id: str, message: str):
    if not device_id or not message:
        return
    for unique_device_id, websocket_server in websocket_servers.items():
        if unique_device_id != device_id:
            continue
        await websocket_server.send_text(message)


# 发送图片给所有连接的客户端，不同设备画面分离
async def send_image_to_websocket_clients(device_id: str, image_stream):
    if not device_id or not image_stream:
        return
    for unique_device_id, websocket_server in websocket_servers.items():
        if unique_device_id != device_id:
            continue
        await websocket_server.send_bytes(image_stream)


def on_frame(client, frame, device_id):
    global frame_buffers

    # 将帧保存到内存中
    _, buffer = cv.imencode('.jpg', frame)
    with buffer_lock:
        # 降低图片质量为 50%
        output_stream = BytesIO()
        img = Image.open(BytesIO(buffer))
        img.convert("RGB").save(output_stream, format='JPEG', quality=50)
        output_stream.seek(0)

        frame_buffer = output_stream
        # 更新设备的帧缓存
        frame_buffers[device_id] = frame_buffer.getvalue()
        # 更新设备的缓存
        if device_id not in caches:
            # 设置缓存画面最多 120 秒
            caches[device_id] = TTLCache(maxsize=1, ttl=120)
        # 缓存图像数据
        caches[device_id]['image'] = frame_buffers[device_id]
        # 通过 WebSocket 发送图像数据
        asyncio.run(send_image_to_websocket_clients(device_id, frame_buffers[device_id]))


client_started_event = threading.Event()


def start_client(device_id):
    if device_id in clients:
        clients[device_id].stop()
        del clients[device_id]
    if device_id in caches:
        del caches[device_id]

    try:
        client = Client(device=device_id, max_fps=max_fps, max_size=max_size, stay_awake=True)
        client.on_frame(lambda c, f: on_frame(c, f, device_id))  # 传递设备 ID
        clients[device_id] = client
        client.start()

        # 通知主线程客户端已启动
        client_started_event.set()
    except Exception as e:
        print(e)
        client_started_event.clear()


def start_client_by_threading(device_id):
    client_thread = threading.Thread(target=start_client, args=(device_id,))
    client_thread.daemon = True
    client_thread.start()

    while device_id not in clients:
        time.sleep(0.1)
    print("pyscrcpy server 已启动~")


def is_device_connected(device_id):
    try:
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, check=True)
        devices_output = result.stdout.strip()
        return device_id in devices_output
    except subprocess.CalledProcessError as e:
        print(f"Error executing adb command: {e}")
        return False
