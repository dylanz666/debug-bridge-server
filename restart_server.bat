@echo off
setlocal

rem 查找 uvicorn 进程
for /f "tokens=5" %%i in ('netstat -ano ^| findstr :8001') do (
    echo Found process using port 8001 with PID %%i
    rem Terminate the process
    taskkill /PID %%i /F
    echo Process with PID %%i has been terminated.
)

endlocal

cd cd C:\dylanz\debug-bridge-server && python start_server.py

echo Closing current window...
timeout /t 2 /nobreak > NUL