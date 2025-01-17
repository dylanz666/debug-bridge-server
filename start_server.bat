@echo off
cd cd C:\dylanz\debug-bridge-server && python start_server.py

echo Closing current window...
timeout /t 2 /nobreak > NUL