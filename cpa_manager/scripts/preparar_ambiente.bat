@echo off
setlocal
cd /d "%~dp0.."
echo === CPA Manager - Preparar ambiente ===
if not exist .env copy .env.example .env >nul
if not exist venv\Scripts\python.exe (
  echo Criando ambiente virtual...
  py -3.12 -m venv venv 2>nul
  if errorlevel 1 python -m venv venv
  if errorlevel 1 (echo Nao foi possivel criar o ambiente virtual. & exit /b 1)
)
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
if errorlevel 1 exit /b 1
pip install -r requirements.txt
if errorlevel 1 exit /b 1
python manage.py migrate
if errorlevel 1 exit /b 1
python manage.py check
if errorlevel 1 exit /b 1
echo Ambiente preparado com sucesso.
pause
