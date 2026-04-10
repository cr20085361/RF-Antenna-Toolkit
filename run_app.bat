@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" goto run

echo [INFO] Creating virtual environment...
where py >nul 2>nul
if %errorlevel%==0 (
    py -3 -m venv .venv
) else (
    python -m venv .venv
)
if errorlevel 1 goto venv_error

echo [INFO] Installing requirements...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto pip_error

:run
echo [INFO] Starting RF Antenna Toolkit...
".venv\Scripts\python.exe" main.py
if errorlevel 1 goto run_error
endlocal
exit /b 0

:venv_error
echo [ERROR] Failed to create .venv. Please ensure Python 3.9+ is installed.
pause
endlocal
exit /b 1

:pip_error
echo [ERROR] Failed to install requirements.
pause
endlocal
exit /b 1

:run_error
echo [ERROR] Application exited with an error.
pause
endlocal
exit /b 1