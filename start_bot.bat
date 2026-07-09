@echo off
REM Simple bot launcher for Windows 11

setlocal enabledelayedexpansion

title CoC Bot

cd /d "%~dp0"

if exist .venv (
    echo Starting CoC Bot...
    .venv\Scripts\python src\main.py
) else (
    echo ERROR: Virtual environment not found!
    echo Please run setup_windows.bat first
    pause
    exit /b 1
)
