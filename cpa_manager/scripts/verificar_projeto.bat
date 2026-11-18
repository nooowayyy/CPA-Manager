@echo off
cd /d "%~dp0.."
if not exist venv\Scripts\python.exe (echo Ambiente virtual nao encontrado. Execute scripts\preparar_ambiente.bat & pause & exit /b 1)
call venv\Scripts\activate.bat
python manage.py check
if errorlevel 1 exit /b 1
python manage.py makemigrations --check --dry-run
if errorlevel 1 exit /b 1
python manage.py test cpa.tests
if errorlevel 1 exit /b 1
python -m compileall -q config cpa
if errorlevel 1 exit /b 1
echo Verificacoes concluidas.
pause
