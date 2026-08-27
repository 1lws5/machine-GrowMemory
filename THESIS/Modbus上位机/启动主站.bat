@echo off
chcp 65001 >nul
title Modbus Master
cd /d "%~dp0"

echo Starting master (read PLC data) ...
echo Press Ctrl+C or close this window to stop.
echo.
python modbus_master.py
pause
