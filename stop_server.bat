@echo off
setlocal

rem find uvicorn process
for /f "tokens=2" %%i in ('tasklist ^| findstr uvicorn') do (
    echo Found uvicorn with PID %%i
    taskkill /PID %%i /F
    echo uvicorn process with PID %%i has been terminated.
)

endlocal

echo Closing current window...
timeout /t 2 /nobreak > NUL