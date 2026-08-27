# -*- coding: utf-8 -*-
"""
从站模拟器 —— 模拟 PLC（Modbus TCP Server）

用途：不启动 CODESYS，本地验证上位机主站能正确读到数据。
地址：127.0.0.1:502   Unit ID = 1

改数据：直接改下面 REGISTERS 列表，保存后重启本脚本。
"""

import sys
from pymodbus.server import StartTcpServer
from pymodbus.datastore import (
    ModbusDeviceContext,
    ModbusServerContext,
    ModbusSequentialDataBlock,
)

# ============ 在这里改模拟数据 ============
# 顺序：[分拣总数, 红色计数, 蓝色计数, 绿色计数, 运行状态(1=运行 0=停止)]
REGISTERS = [16, 4, 6, 6, 1]
# ==========================================

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

store = ModbusDeviceContext(
    di=ModbusSequentialDataBlock(1, [0] * 100),               # 离散输入
    co=ModbusSequentialDataBlock(1, [0] * 100),               # 线圈
    hr=ModbusSequentialDataBlock(1, REGISTERS + [0] * 95),    # 保持寄存器
    ir=ModbusSequentialDataBlock(1, [0] * 100),               # 输入寄存器
)
context = ModbusServerContext(devices={1: store}, single=False)

print("从站模拟器已启动：127.0.0.1:502（Unit ID=1）")
print(f"当前模拟数据：总数={REGISTERS[0]} 红={REGISTERS[1]} 蓝={REGISTERS[2]} 绿={REGISTERS[3]} 运行={REGISTERS[4]}")
print("按 Ctrl+C 或直接关窗口退出")
StartTcpServer(context=context, address=("127.0.0.1", 502))
