@echo off
cd /d C:\newproject\backend
C:\newproject\.venv\Scripts\python.exe -m uvicorn main:app --port 8000 --reload
