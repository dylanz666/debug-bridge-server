import subprocess
import asyncio


async def start_uvicorn_server():
    # start uvicorn server without any new command window opened
    process = subprocess.Popen(
        ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    print("Your server is started, process id: ", process.pid)
    return process


async def main():
    await start_uvicorn_server()
    print("Wait a little bit to close the window...")
    await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(main())
