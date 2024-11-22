@echo off
setlocal

rem 查找 uvicorn 进程
for /f "tokens=2" %%i in ('tasklist ^| findstr uvicorn') do (
    echo Found uvicorn with PID %%i
    taskkill /PID %%i /F
    echo uvicorn process with PID %%i has been terminated.
)

endlocal

python start_server.py

echo Closing current window...
timeout /t 2 /nobreak > NUL