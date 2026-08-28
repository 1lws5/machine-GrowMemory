@echo off
chcp 65001 >nul
title 上位机主站
cd /d "%~dp0"

echo 正在启动上位机主站（读 PLC 数据）...
echo 按 Ctrl+C 或直接关窗口停止。
echo.
python modbus_master.py
pause
