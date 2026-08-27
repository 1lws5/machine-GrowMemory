@echo off
chcp 65001 >nul
title Modbus Slave Simulator
cd /d "%~dp0"

echo Clearing port 502 ...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :502 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 1 /nobreak >nul

echo.
echo Starting slave simulator (PLC) ...
echo Press Ctrl+C or close this window to stop.
echo.
python modbus_slave_simulator.py
pause
