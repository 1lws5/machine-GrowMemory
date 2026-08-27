# -*- coding: utf-8 -*-
"""
上位机主站 —— Modbus TCP Client

用途：循环读取 PLC（从站）的 5 个保持寄存器，显示成监控面板。
地址：127.0.0.1:502   Unit ID = 1

寄存器映射（对应 thesis 需求文档）：
    偏移0 : 分拣总数  wCountTotal
    偏移1 : 红色计数  wCountRed
    偏移2 : 蓝色计数  wCountBlue
    偏移3 : 绿色计数  wCountGreen
    偏移4 : 运行状态  wRunState（1=运行 0=停止）
"""

import sys
import time
from pymodbus.client import ModbusTcpClient

HOST = "127.0.0.1"
PORT = 502
SLAVE_ID = 1
ADDR_START = 0      # 40001 对应偏移 0
REG_COUNT = 5       # 读 5 个保持寄存器
REFRESH_SEC = 2     # 刷新间隔（秒）

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def fmt_panel(regs):
    total, red, blue, green, run = regs
    run_text = "运行中" if run == 1 else "已停止"
    return (
        "=" * 42 + "\n"
        "     传送带分拣监控（上位机主站）\n"
        "=" * 42 + "\n"
        f"  运行状态 : {run_text}\n"
        f"  分拣总数 : {total}\n"
        f"  红色计数 : {red}\n"
        f"  蓝色计数 : {blue}\n"
        f"  绿色计数 : {green}\n"
        "=" * 42
    )


def main():
    client = ModbusTcpClient(HOST, port=PORT, timeout=3)
    print(f"正在连接 PLC 从站 {HOST}:{PORT} ...")

    if not client.connect():
        print("[错误] 连接失败！请检查：")
        print("  1. 从站模拟器（slave）或 CODESYS 仿真器是否已启动")
        print("  2. 端口 502 是否被占用")
        return 1

    print(f"连接成功，开始循环读取寄存器（每 {REFRESH_SEC} 秒刷新，Ctrl+C 退出）...\n")
    try:
        while True:
            rr = client.read_holding_registers(
                address=ADDR_START, count=REG_COUNT, device_id=SLAVE_ID
            )
            if rr.isError():
                print(f"[错误] 读取失败: {rr}")
            else:
                print(fmt_panel(rr.registers))
                print(f"\n  [刷新 {time.strftime('%H:%M:%S')}]")
            time.sleep(REFRESH_SEC)
    except KeyboardInterrupt:
        print("\n已停止监控。")
    finally:
        client.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
