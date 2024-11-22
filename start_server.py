import subprocess
import asyncio
from datetime import datetime

from utils.file_util import FileUtil


async def start_uvicorn_server():
    FileUtil.makedirs_if_not_exist("log")
    log_file = f'log/{datetime.now().strftime("%m-%d-%Y")}.log'
    FileUtil.create_file_if_not_exist(log_file)
    with open(log_file, "a") as log_file:
        log_file.write(f"{datetime.now().strftime('%m-%d-%Y %H:%M:%S')} - Starting server...\n")
        # start uvicorn server without any new command window opened
        process = subprocess.Popen(
            ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--log-config", "log-config.yaml"],
            stdout=log_file,
            stderr=log_file,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        print("Your server is started, process id: ", process.pid)


async def main():
    await start_uvicorn_server()
    print("Wait a little bit to close the window...")
    await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
