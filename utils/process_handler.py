import psutil


class ProcessHandler:
    def __init__(self):
        pass

    @staticmethod
    def find_process(app_name, commands):
        for process in psutil.process_iter(['pid', 'name']):
            if app_name not in process.name().lower():
                continue

            cmds = process.cmdline()
            for command in commands:
                for cmd in cmds:
                    if command in cmd:
                        print("Find process!")
                        return process

    @staticmethod
    def stop_process(process):
        if not process:
            print("No process provided, skip stopping process~")
            return
        print("Start to stopping process, PID", process.pid)
        process.terminate()
        print("The process is terminated!")

    @staticmethod
    def stop_process_by_pid(pid):
        if not pid:
            print("No pid provided, skip stopping process~")
            return
        print("Start to stopping process, PID", pid)
        process = psutil.Process(pid)
        process.terminate()
        print(f"The process {pid} is terminated!")


if __name__ == "__main__":
    target_app_name = "uvicorn"
    target_commands = ["uvicorn.exe", "main:app"]
    process_result = ProcessHandler.find_process(app_name=target_app_name, commands=target_commands)
    ProcessHandler.stop_process(process_result)
