@echo off
cd /d "%~dp0.."
if not exist venv\Scripts\python.exe (echo Execute primeiro scripts\preparar_ambiente.bat & pause & exit /b 1)
call venv\Scripts\activate.bat
python manage.py runserver 127.0.0.1:8000
