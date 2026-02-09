@echo off
cd /d C:\newproject\backend
set PYTHONPATH=.
C:\newproject\.venv\Scripts\python.exe -m uvicorn main:app --port 8000 --host 127.0.0.1
