@echo off
echo Start daemon process...
python daemon.py

echo Closing current window...
timeout /t 2 /nobreak > NUL