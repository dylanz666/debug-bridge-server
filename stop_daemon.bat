@echo off
setlocal

rem Find the PID of the process using port 8001
for /f "tokens=5" %%i in ('netstat -ano ^| findstr :8002') do (
    echo Found process using port 8002 with PID %%i
    rem Terminate the process
    taskkill /PID %%i /F
    echo Process with PID %%i has been terminated.
)

endlocal

echo Closing current window...
timeout /t 2 /nobreak > NUL