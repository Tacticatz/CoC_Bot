@echo off
setlocal enabledelayedexpansion

title CoC Bot - Windows 11 Setup Wizard

echo.
echo ========================================
echo   CoC Bot - Windows 11 Setup Wizard
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo.
    echo Please install Python 3.11+ from https://www.python.org/downloads/
    echo During installation, MAKE SURE to check "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% found
echo.

REM Change to script directory
cd /d "%~dp0"

REM Run setup wizard
echo Launching Windows 11 Setup Wizard...
echo.
python windows_setup_wizard.py

if errorlevel 1 (
    echo.
    echo Setup wizard failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup complete! Ready to run the bot.
echo ========================================
echo.
pause
