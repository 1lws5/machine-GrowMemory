# 传送带分拣控制系统 — Modbus TCP 通信制作指示文档

| 项目 | 内容 |
|------|------|
| 环境 | CODESYS V3.5 SP22 Patch 3 |
| 仿真器 | CODESYS Control Win V3 x64 |
| 协议 | Modbus TCP |
| 端口 | 502 |
| 从站地址 | Unit ID = 1 |
| PLC 角色 | 从站（Server，被动响应） |
| 上位机角色 | 主站（Client，主动读数据） |
| 设计原则 | 无自建逻辑，只把 GVL 计数/状态变量映射到保持寄存器 |

## 一、概述与主从关系（先理清方向）

### 1.1 本项目通信要解决什么

毕业设计需要一个"上位机读 PLC 数据"的通信环节，证明 PLC 数据能对外输出、能被监控。本项目做法：

**PLC 做 Modbus TCP 从站（Slave Device），把分拣计数、运行状态挂到保持寄存器（Holding Register）；上位机（PC）做主站（Client），主动去读这些寄存器。**

### 1.2 主从关系（最容易搞反的点）

| 角色 | 是谁 | 干什么 |
|------|------|--------|
| **主站 Client** | 上位机 / HMI / PC 脚本 | 主动发起读请求，查询 PLC 数据 |
| **从站 Server** | CODESYS PLC | 被动响应，把数据挂到寄存器等主站来读 |

> **纠正一个常见误区**：需求文档早期版本把主从关系写反了。正确是"上位机是主、PLC 是从"——因为上位机主动问、PLC 被动答。
>
> 另一个概念 **Modbus TCP Master（PLC 做主机主动读别的设备）** 本项目用不上：我们没有任何"别的从站设备"要 PLC 去读，是反过来让别人读我们。

### 1.3 为什么选 Modbus TCP（而不是 OPC UA / MQTT）

| 协议 | 定位 | 本项目取舍 |
|------|------|-----------|
| **Modbus TCP** | 工业设备通信事实标准，设备岗面试必问 | ✅ 选它，最对口 |
| OPC UA | 现代工厂信息化标准，但配置重、偏上位 | 进阶可选，不本次做 |
| MQTT | 物联网消息协议，偏 IT/云 | 过度，不用 |

## 二、前提条件

- 工程已编译通过（F11，0 error）。
- GVL 已声明 4 个计数变量（wCountRed / wCountBlue / wCountGreen / wCountTotal，均 INT）。
- 仿真器 CODESYS Control Win SysTray 已启动（阶段三已装）。
- Python 3.14 已装（用于主站读数据脚本）。

## 三、CODESYS 配置 Modbus TCP 从站（施工步骤）

### 3.1 添加 Modbus TCP Slave Device

1. 左侧设备树，右键 `Device (CODESYS Control Win V3)`。
2. 选「添加设备（Add Device）」。
3. 展开 Fieldbuses → Modbus → 选 **Modbus TCP Slave Device**。
4. 点「添加设备」，从站设备出现在设备树下。

### 3.2 配置从站参数

1. 双击刚添加的 `Modbus_TCP_Slave_Device`。
2. 常规（General）标签页设置：

| 参数 | 值 | 说明 |
|------|-----|------|
| Unit ID | 1 | 从站地址（默认 255 表示"任意"，改成 1 更规范） |
| 端口（Port） | 502 | Modbus TCP 标准端口 |

### 3.3 添加通道（Channel）

1. 右键从站设备 → 添加设备 → **Modbus Slave Channel**。
2. 通道配置：

| 参数 | 值 | 说明 |
|------|-----|------|
| 访问类型（Access Type） | 读保持寄存器（Read Holding Registers，功能码 03） | 主站用 03 读 |
| 数量（Count） | 5 | 5 个寄存器 |

### 3.4 I/O 映射（把 GVL 变量拖到通道）

1. 双击通道，打开右侧「Modbus Slave Channel I/O Mapping」标签页。
2. 把 GVL 变量拖到通道的每个寄存器位（GVL 开了 qualified_only，必须带 `GVL.` 前缀）：

| 寄存器地址 | 偏移 | 映射变量 | 含义 |
|-----------|------|----------|------|
| 40001 | 0 | GVL.wCountTotal | 分拣总数 |
| 40002 | 1 | GVL.wCountRed | 红色计数 |
| 40003 | 2 | GVL.wCountBlue | 蓝色计数 |
| 40004 | 3 | GVL.wCountGreen | 绿色计数 |
| 40005 | 4 | GVL.wRunState | 运行状态（0=停 1=运行） |

> **说明**：Holding Register 是 16 位字，每个 INT 变量正好占 1 个寄存器。BOOL 变量（如 qBelt）位打包麻烦，所以运行状态用 INT 变量 wRunState 单独占一个寄存器，而不是直接用 qBelt。

### 3.5 重新编译

1. F11 编译（0 error）。
2. Alt+F8 登录（localhost，设备用户名 DeviceUser）→ 下载 → F5 运行。

## 四、寄存器映射总表（一图看懂全部）

| 寄存器地址 | 偏移 | 变量 | 类型 | 含义 | 值域 |
|-----------|------|------|------|------|------|
| 40001 | 0 | GVL.wCountTotal | INT | 分拣总数 | 0~32767 |
| 40002 | 1 | GVL.wCountRed | INT | 红色计数 | 0~32767 |
| 40003 | 2 | GVL.wCountBlue | INT | 蓝色计数 | 0~32767 |
| 40004 | 3 | GVL.wCountGreen | INT | 绿色计数 | 0~32767 |
| 40005 | 4 | GVL.wRunState | INT | 运行状态 | 0=停止 1=运行 |

> 主站读数据的功能码统一用 **03（Read Holding Registers）**。

## 五、wRunState 变量（唯一需要动代码的点）

### 5.1 现状与问题

4 个计数变量（wCountRed/Blue/Green/Total）GVL 里已有，直接映射即可。

但"运行状态"目前没有现成的 INT 变量——现有的是 BOOL 的 `qBelt`（传送带输出）和 `bRunning`（FB_BeltControl 内部）。为避免 BOOL 位打包，需要新增一个 INT 变量 `wRunState`。

### 5.2 需要改动两处（**待用户确认后再改**）

**① GVL 内部变量区新增：**

```iecst
    wRunState   : INT := 0;     // 运行状态（0=停 1=运行），供 Modbus 映射
```

**② PLC_PRG 末尾新增一句：**

```iecst
GVL.wRunState := BOOL_TO_INT(fbBelt.bRunning);   // 运行状态 → INT，供 Modbus 映射
```

> **说明**：`fbBelt.bRunning` 是 FB_BeltControl 输出的"运行中"状态（BOOL），用 BOOL_TO_INT 转成 0/1 赋给 wRunState。这样寄存器 40005 读到 0=停、1=运行。

> ⚠️ **此改动尚未执行**——按项目铁律"没得到明确开工命令不许修改代码"，本文档只给方案，改 GVL/PLC_PRG 前需用户确认。改的是源工程 thesis.project（CODESYS 内手动改）和《thesis代码.md》快照。

## 六、主站测试（上位机读数据）

仿真器在本机 `localhost:502` 开从站，主站也跑在本机，本地环回直接读。

### 6.1 方案一：Python + pymodbus（推荐，自写上位机最能吹）

**为什么推荐**：Python 3.14 现成、一条 `pip install pymodbus` 装好；毕设答辩能展示"自己写上位机读 PLC 数据"比用现成工具更有说服力；脚本可存 GitHub 当交付物。

**安装**：

```powershell
pip install pymodbus
```

**脚本 `modbus_read.py`**：

```python
from pymodbus.client import ModbusTcpClient

client = ModbusTcpClient("127.0.0.1", port=502)
client.connect()

# 读 5 个保持寄存器（地址 0 起，数量 5，从站 Unit ID = 1）
rr = client.read_holding_registers(address=0, count=5, slave=1)

if rr.isError():
    print("读取失败:", rr)
else:
    total = rr.registers[0]
    red   = rr.registers[1]
    blue  = rr.registers[2]
    green = rr.registers[3]
    run   = rr.registers[4]
    print(f"总计数={total} 红={red} 蓝={blue} 绿={green} 运行状态={run}")

client.close()
```

**验证**：脚本跑起来能打印出 5 个数字（初始 0,0,0,0,0 或 0/1 的运行状态），即证明链路通。

### 6.2 方案二：QModMaster（免费 GUI，零代码快速验证）

- 开源地址：`https://github.com/jdunmire/qModMaster`（官方 Release 停在 2017 v0.4.7）
- 国内 fork（含中文界面）：`https://github.com/xakod/QModMaster`
- 用法：连 localhost:502 → 选 Holding Register → 起始地址 0 → 数量 5 → 读。

适合先 5 分钟验证链路通不通，正式交付还是用 Python 脚本。

### 6.3 方案对比

| 方案 | 成本 | 上手 | 答辩说服力 | 建议 |
|------|------|------|-----------|------|
| Python + pymodbus | 免费 | 中 | 高（自写上位机） | ✅ 正式交付 |
| QModMaster | 免费 | 低 | 低（现成工具） | 快速验证 |
| Modbus Poll | 付费试用 | 低 | 低 | 不推荐 |

**建议两步走**：QModMaster 先 5 分钟验证链路 → Python 脚本正式读数据、存 GitHub 当交付物。

## 七、验收清单（逐条）

| # | 操作 | 预期结果 |
|---|------|----------|
| 1 | 设备树出现 Modbus TCP Slave Device | 从站设备 + 通道 + 5 寄存器 |
| 2 | F11 编译 | 0 error |
| 3 | Alt+F8 登录 localhost + F5 运行 | 仿真器运行，无通信报错 |
| 4 | QModMaster 连 localhost:502 读 5 寄存器 | 读到 0,0,0,0,0 |
| 5 | Python 脚本跑一遍 | 打印出 5 个数字，无异常 |
| 6 | HMI 触发一次分拣（计数+1）后重读 | 对应颜色计数 +1，总计数 +1 |

## 八、常见问题

### 8.1 连不上 / 读不到

- 确认仿真器在运行（SysTray C64 图标）。
- 确认从站设备 Unit ID=1、端口 502，与主站请求的 slave 参数一致。
- 确认通道 Access Type 选的是 Read Holding Registers（03），不是线圈/输入寄存器。

### 8.2 读到全 0

- 数据本来就是 0（还没触发过分拣）。
- 确认 GVL 变量已拖到通道的 I/O Mapping（不是空的）。

### 8.3 端口 502 被占用

- 换端口（如 1502），同时主站脚本同步改端口。

---

相关文档：《thesis代码.md》（GVL/程序结构）、《thesis需求文档.md》（Modbus 章节+寄存器映射）、《thesis调试文档.md》（仿真/登录/强制变量流程）。
