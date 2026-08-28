# 传送带分拣控制系统 — Modbus TCP 通信制作指示文档

| 项目 | 内容 |
|------|------|
| 环境 | CODESYS V3.5 SP22 Patch 3 |
| 仿真器 | CODESYS Control Win V3 x64 |
| 协议 | Modbus TCP |
| 端口 | 502 |
| 从站设备 | ModbusTCP Server Device（通用 TCP 服务器） |
| 寄存器类型 | Input Register（输入寄存器） |
| 功能码 | 04（Read Input Registers） |
| 寄存器数量 | 4 |
| PLC 角色 | 从站（Server，被动响应） |
| 上位机角色 | 主站（Client，主动读数据） |

> ⚠️ **口径说明**：早期方案写的是 `Modbus TCP Slave Device + Unit ID=1 + Holding Register + 5 寄存器（含 wRunState）+ 功能码 03`。实际调试中发现本机 CODESYS 只有 **ModbusTCP Server Device**，无 Unit ID；计数是 PLC 输出给上位机读，应放 **Input Register（输入寄存器）**；运行状态 wRunState 砍掉。最终落地为 **ModbusTCP Server Device + Input Register × 4 + 功能码 04**。旧文档口径与本文档冲突时，以本文档为准。

---

## 一、概述与主从关系

### 1.1 本项目通信要解决什么

毕业设计需要一个"上位机读 PLC 数据"的通信环节，证明 PLC 数据能对外输出、能被监控。

**PLC 做 Modbus TCP 从站（Server），把分拣计数挂到输入寄存器；上位机（PC）做主站（Client），主动去读这些寄存器。**

### 1.2 主从关系

| 角色 | 是谁 | 干什么 |
|------|------|--------|
| **主站 Client** | 上位机 / Python 脚本 | 主动发起读请求，查询 PLC 数据 |
| **从站 Server** | CODESYS PLC | 被动响应，把数据挂到寄存器等主站来读 |

### 1.3 为什么选 Modbus TCP

工业现场设备通信的事实标准，设备岗面试必问，配置简单，与本项目 Codesys + Python 环境最匹配。

---

## 二、前提条件

- 工程已编译通过（F11，0 error）。
- GVL 已声明 4 个计数变量：`wCountRed` / `wCountBlue` / `wCountGreen` / `wCountTotal`（均 INT）。
- 仿真器 CODESYS Control Win V3 x64 已安装。
- Python 3.14 已装，pymodbus 3.15.0 已装。

---

## 三、GVL 设置（关键：用 AT %QW 声明映射变量）

### 3.1 为什么要用 AT %QW

在 CODESYS 里，把普通变量拖到 Modbus I/O Mapping 的 `%QW` 行会报错：

```
输出映射到现有变量 Application.GVL.wCountTotal.%QW0 无法再使用
```

因为被 I/O 映射占用的变量，程序里不能再 `:=` 赋值。

**正确做法**：在 GVL 里用 `AT %QW0` 直接声明映射变量，它本身就是该地址的别名，程序可以正常赋值。

### 3.2 GVL 内部变量区新增

```iecst
    // ===== Modbus TCP 输出映射（PLC → 上位机读）=====
    mbCountTotal AT %QW0 : INT;   // 分拣总数 → 输入寄存器 30001
    mbCountRed   AT %QW1 : INT;   // 红色计数 → 输入寄存器 30002
    mbCountBlue  AT %QW2 : INT;   // 蓝色计数 → 输入寄存器 30003
    mbCountGreen AT %QW3 : INT;   // 绿色计数 → 输入寄存器 30004
```

### 3.3 仿真模式开关（推荐）

为了在不接真实传感器的情况下让计数自动涨起来，方便调试通信，建议在 GVL 加一个仿真开关：

```iecst
    bSimMode : BOOL := TRUE;   // TRUE=自动演示工件；FALSE=真实输入
```

---

## 四、PLC_PRG 设置

### 4.1 把计数复制到 Modbus 映射变量

在 PLC_PRG 末尾，把功能块输出的计数复制给 `mbCountXxx`：

```iecst
// 计数 → Modbus 输入寄存器映射
GVL.mbCountTotal := fbSort.wCountTotal;
GVL.mbCountRed   := fbSort.wCountRed;
GVL.mbCountBlue  := fbSort.wCountBlue;
GVL.mbCountGreen := fbSort.wCountGreen;
```

### 4.2 仿真模式输入切换（可选但推荐）

```iecst
PROGRAM PLC_PRG
VAR
    fbBelt  : FB_BeltControl;
    fbSort  : FB_Sorter;
    fbDemo  : FB_DemoFeeder;   // 演示工件发生器
END_VAR

fbDemo(bEnable := GVL.bSimMode);

fbBelt(
    iStart := GVL.iStart OR GVL.bSimMode,
    iStop  := GVL.iStop,
    iPause := fbSort.bPause
);

GVL.qBelt     := fbBelt.qBelt;
GVL.qRunLight := fbBelt.qRunLight;

fbSort(
    iDetect     := SEL(GVL.bSimMode, GVL.iDetect, fbDemo.bDetect),
    iColorCode  := SEL(GVL.bSimMode, GVL.iColorCode, fbDemo.iColor),
    bRunning    := fbBelt.bRunning,
    bAlarmReset := GVL.bAlarmReset,
    bCntReset   := GVL.bCntReset
);

GVL.qPushA      := fbSort.qPushA;
GVL.qPushB      := fbSort.qPushB;
GVL.qPushC      := fbSort.qPushC;
GVL.qAlarmLight := fbSort.qAlarmLight;

// 计数 → HMI/Modbus
GVL.wCountRed   := fbSort.wCountRed;
GVL.wCountBlue  := fbSort.wCountBlue;
GVL.wCountGreen := fbSort.wCountGreen;
GVL.wCountTotal := fbSort.wCountTotal;

// 计数 → Modbus 输入寄存器
GVL.mbCountTotal := fbSort.wCountTotal;
GVL.mbCountRed   := fbSort.wCountRed;
GVL.mbCountBlue  := fbSort.wCountBlue;
GVL.mbCountGreen := fbSort.wCountGreen;
```

> `SEL(G, A, B)`：G=FALSE 取 A（真实输入），G=TRUE 取 B（演示激励）。

---

## 五、CODESYS 配置 Modbus TCP 从站

### 5.1 添加 Ethernet 适配器

1. 左侧设备树，右键 `Device (CODESYS Control Win V3)`。
2. 选「添加设备（Add Device）」。
3. 展开 Fieldbuses → Ethernet Adapter → Ethernet → 添加。
4. 双击 Ethernet，点 `...` 选本机网卡。

> **坑点 1**：如果直接右键 Device 添加 Modbus，只能看到 `modbus_com`（串口 RTU），看不到 TCP 设备。TCP 必须挂在 Ethernet 下面。

### 5.2 添加 ModbusTCP Server Device

1. 右键刚加的 `Ethernet` → 添加设备 → Fieldbuses → Modbus → **ModbusTCP Server Device** → 添加。
2. 双击该设备。

### 5.3 General 标签配置

| 参数 | 值 | 说明 |
|------|-----|------|
| Port | 502 | Modbus TCP 标准端口 |
| Input Registers | 4 | 4 个输入寄存器 |
| Holding Registers | 0 | 本项目不用 |
| Unit ID | 无 | Server Device 没有 Unit ID 字段 |

> **坑点 2**：本机 CODESYS V3.5 SP22 Patch 3 里没有 `Modbus TCP Slave Device`，只有 `ModbusTCP Server Device`。它无 Unit ID，不要硬填。

### 5.4 I/O Mapping 标签配置

把 4 个 `mbCountXxx` 变量拖到对应 `%QW` 行：

| 偏移 | 映射变量 | 寄存器地址 | 含义 |
|------|----------|-----------|------|
| 0 | GVL.mbCountTotal | 30001 | 分拣总数 |
| 1 | GVL.mbCountRed | 30002 | 红色计数 |
| 2 | GVL.mbCountBlue | 30003 | 蓝色计数 |
| 3 | GVL.mbCountGreen | 30004 | 绿色计数 |

> **坑点 3**：计数是 PLC 输出给主站读，应放 **Input Register（%QW）**，不是 Holding Register。Input Register 对应 Modbus 功能码 04。

### 5.5 重新编译下载

1. F11 编译（0 error）。
2. Alt+F8 登录仿真器 → 下载 → F5 运行。

---

## 六、寄存器映射总表

| Modbus 地址 | 偏移 | 变量 | 类型 | 含义 | 功能码 |
|------------|------|------|------|------|--------|
| 30001 | 0 | GVL.mbCountTotal | INT | 分拣总数 | 04 |
| 30002 | 1 | GVL.mbCountRed | INT | 红色计数 | 04 |
| 30003 | 2 | GVL.mbCountBlue | INT | 蓝色计数 | 04 |
| 30004 | 3 | GVL.mbCountGreen | INT | 绿色计数 | 04 |

---

## 七、Python 上位机主站

### 7.1 环境准备

```powershell
python -c "import pymodbus; print(pymodbus.__version__)"
```

应显示 `3.15.0`。

### 7.2 主站脚本要点

- 使用 `read_input_registers(address=0, count=4, device_id=1)`
- pymodbus 3.15 参数用 `device_id`（旧名 `slave` 已弃用）
- 服务器不校验 Unit ID，`device_id` 填几都行

### 7.3 桌面工具包

`C:\Users\Administrator\Desktop\Modbus上位机\` 下含：

| 文件 | 作用 |
|------|------|
| `启动从站.bat` | 清 502 端口 + 启动 Python 模拟从站（测试用，假数据 `[16,4,6,6]`） |
| `启动主站.bat` | 启动上位机主站，读 PLC 或模拟从站数据 |
| `modbus_slave_simulator.py` | 模拟从站主体 |
| `modbus_master.py` | 上位机主站主体 |
| `使用说明.md` | 完整使用说明 |

---

## 八、验收清单

| # | 操作 | 预期结果 |
|---|------|----------|
| 1 | 设备树出现 Ethernet + ModbusTCP Server Device | 配置正确 |
| 2 | General 中 Input Registers = 4，Port = 502 | 参数正确 |
| 3 | I/O Mapping 中 4 个 mbCountXxx 已绑定 | 映射正确 |
| 4 | F11 编译 | 0 error |
| 5 | Alt+F8 登录 + F5 运行 | 仿真器运行 |
| 6 | 双击 `启动从站.bat` 再双击 `启动主站.bat` | 读到 16/4/6/6，脚本 OK |
| 7 | 关模拟从站，启动 CODESYS 仿真器，再开主站 | 读到 PLC 真实计数（初始全 0 也 OK） |
| 8 | 启用 `bSimMode` 让计数自动涨 | 主站数字自动变化 |

---

## 九、常见问题与踩坑记录

### 9.1 找不到 Modbus TCP Slave Device

**原因**：CODESYS SP22 Patch 3 默认没有 `Modbus TCP Slave Device`，只有 `ModbusTCP Server Device`。
**解决**：用 `ModbusTCP Server Device`，效果一样，只是无 Unit ID。

### 9.2 编译报错 "输出映射到现有变量...无法再使用"

**原因**：把普通变量拖到 I/O Mapping 的 `%QW` 后，该变量被 I/O 占用，程序不能再赋值。
**解决**：在 GVL 里用 `AT %QW` 声明映射变量（如 `mbCountTotal AT %QW0 : INT`），程序正常写它。

### 9.3 主站读全 0 且不变

**原因 1**：没有触发分拣动作。解决：开 `bSimMode` 用 FB_DemoFeeder 自动演示。
**原因 2**：I/O Mapping 没绑上变量。
**原因 3**：仿真器没重新下载，跑的是旧程序。解决：Login with download 强制覆盖。

### 9.4 主站连接失败

- 确认 CODESYS 仿真器已启动并运行（F5）。
- 确认 502 端口没被旧进程占用。
- 确认 Python 主站连的是 `127.0.0.1:502`。

### 9.5 pymodbus 3.15 API 变更

- `ModbusSlaveContext` → `ModbusDeviceContext`
- `read_holding_registers(slave=1)` → `read_input_registers(device_id=1)`
- `ModbusServerContext(slaves={1:store}, single=False)` → `ModbusServerContext(devices={1:store}, single=False)`

---

相关文档：《thesis代码.md》（GVL/程序结构）、《thesis需求文档.md》（Modbus 章节）、《thesis-ModbusTCP通信调试文档.md》（详细调试步骤）、《thesis-BOM物料清单.md》。
