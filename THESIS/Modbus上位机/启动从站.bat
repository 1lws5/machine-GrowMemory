@echo off
chcp 65001 >nul
title 模拟从站（测试用）
cd /d "%~dp0"

echo 正在清理 502 端口 ...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :502 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 1 /nobreak >nul

echo.
echo 正在启动模拟从站（测试用）...
echo 按 Ctrl+C 或直接关窗口停止。
echo.
python modbus_slave_simulator.py
pause
