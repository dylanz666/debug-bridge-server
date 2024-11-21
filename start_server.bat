@echo off
start /B uvicorn main:app --host 0.0.0.0 --port 8001 > NUL 2>&1