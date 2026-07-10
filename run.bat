@echo off
REM ================================================================
REM WINDOWS LAUNCHER (run.bat)
REM Double-click this file to start the CV Analyzer.
REM The first run installs libraries and takes a few minutes.
REM Keep this window OPEN while using the app.
REM
REM NOTE: this file must contain plain English text only. The old
REM version had Arabic text, which cmd.exe garbles into broken
REM commands ("xit", "kdir"), so the app never started.
REM ================================================================

REM Always work from the folder this file lives in
cd /d "%~dp0"

REM --- Find Python (tries "python", then the "py" launcher) ---
set PYTHON=python
python --version >nul 2>&1
if errorlevel 1 (
    py --version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Python is not installed or not on PATH.
        echo.
        echo Download it from: https://www.python.org/downloads/
        echo IMPORTANT: tick "Add Python to PATH" during installation.
        pause
        exit /b 1
    )
    set PYTHON=py
)
echo [OK] Python found.

REM --- Create the virtual environment on first run ---
if not exist "venv" (
    echo [SETUP] Creating virtual environment - first run only...
    %PYTHON% -m venv venv
)

call venv\Scripts\activate.bat

echo [SETUP] Installing required libraries - please wait...
python -m pip install --upgrade pip
pip install -r requirements.txt

if not exist "data" mkdir data

echo.
echo [RUN] Starting the app... your browser link is:
echo.
echo        http://localhost:8501
echo.
echo Keep this window open while using the app.
echo.
streamlit run src\dashboard.py

pause
