# 传送带分拣控制系统 — Modbus TCP 通信调试文档

| 项目 | 内容 |
|------|------|
| 环境 | CODESYS V3.5 SP22 Patch 3 |
| 仿真器 | CODESYS Control Win V3 x64 |
| 协议 | Modbus TCP |
| 端口 | 502 |
| 从站设备 | ModbusTCP Server Device（通用 TCP 服务器，无 Unit ID） |
| 寄存器 | Input Register（输入寄存器）× 4，功能码 04 |
| PLC 角色 | 从站（Server，被动响应） |
| 上位机角色 | 主站（Client，主动读数据） |

> ⚠️ **口径说明**：本文档以工程**实际落地状态**为准。早期《thesis-ModbusTCP通信制作指示.md》写的是「Modbus TCP Slave Device + Unit ID=1 + Holding Register + 5 寄存器（含 wRunState）+ 功能码03」，但实际调试中发现：本机 CODESYS 只有 **ModbusTCP Server Device**（无 Unit ID），且计数是 PLC 输出给上位机读的值，应放 **Input Register（功能码04）**，运行状态 wRunState 未做、砍掉。**两文档冲突处以本调试文档为准。**

---

## 一、调试目标

验证完整链路：**CODESYS 仿真器（PLC 从站）对外输出分拣计数 → 上位机 Python 主站经 Modbus TCP 实时读到 → 计数随分拣动作变化**。

判定成功的唯一标准：**主站读到的 4 个计数（总数/红/蓝/绿）能随分拣动作自动变化**，而不是永远停在全 0。

---

## 二、前置条件

- [ ] 工程已编译通过（F11，0 error）
- [ ] 仿真器 CODESYS Control Win SysTray 已启动
- [ ] GVL 已声明 4 个计数变量：`wCountTotal` / `wCountRed` / `wCountBlue` / `wCountGreen`（均 INT）
- [ ] Python 3.14 已装，pymodbus 已装（`python -c "import pymodbus; print(pymodbus.__version__)"` 显示 3.15.0）
- [ ] 上位机工具已就绪（桌面 `Modbus上位机` 文件夹：主站脚本 + 模拟从站脚本 + 启动 bat）

---

## 三、从站配置（实际状态核对）

### 3.1 从站类型：为什么是 Server Device 不是 Slave Device

| 设备 | 有无 Unit ID | 适用 |
|------|-------------|------|
| **Modbus TCP Slave Device** | 有（1~247） | 单元寻址从站，走 Modbus TCP/RTU 网关时用 |
| **ModbusTCP Server Device**（本项目） | 无 | 通用 TCP 服务器，主站直接连 IP:502，服务器不校验单元号 |

本项目 PLC 是纯服务器（被动等上位机来读），没有网关寻址需求，**用 ModbusTCP Server Device 即可，没有 Unit ID 是正常的**。

### 3.2 配置步骤（工程内已做，此处用于核对）

1. 设备树 `Device (CODESYS Control Win V3)` 下加 **Ethernet** 适配器。
2. Ethernet 下加 **ModbusTCP Server Device**。
3. 双击从站设备 → General 标签：
   - **Port（端口）**：`502`
   - **Input Registers（输入寄存器）数量**：`4`
   - Holding Registers 数量：`0`（不用）
4. 切到 **I/O Mapping** 标签，把 4 个计数变量绑到输入寄存器（%QW 行）：

| 偏移 | 绑定变量 | 含义 |
|------|----------|------|
| 0 | GVL.wCountTotal | 分拣总数 |
| 1 | GVL.wCountRed | 红色计数 |
| 2 | GVL.wCountBlue | 蓝色计数 |
| 3 | GVL.wCountGreen | 绿色计数 |

### 3.3 寄存器映射总表

| 寄存器 | 偏移 | 变量 | 类型 | 含义 | 功能码 |
|--------|------|------|------|------|--------|
| 30001 | 0 | GVL.wCountTotal | INT | 分拣总数 | 04 |
| 30002 | 1 | GVL.wCountRed | INT | 红色计数 | 04 |
| 30003 | 2 | GVL.wCountBlue | INT | 蓝色计数 | 04 |
| 30004 | 3 | GVL.wCountGreen | INT | 绿色计数 | 04 |

> 计数是 PLC 输出 → 主站读，放 **Input Register（%QW）**，主站用 **功能码 04（Read Input Registers）** 读。

---

## 四、上位机主站（Python）

### 4.1 工具清单（桌面 `Modbus上位机` 文件夹）

| 文件 | 作用 |
|------|------|
| `启动从站.bat` | 双击 = 清 502 端口 + 启动**模拟从站（测试用，假数据）** |
| `启动主站.bat` | 双击 = 启动上位机主站（读 PLC 数据） |
| `modbus_slave_simulator.py` | 模拟从站（测试用），改顶部 `REGISTERS = [16, 4, 6, 6]` 改假数据 |
| `modbus_master.py` | 上位机主站主体 |

### 4.2 主站脚本要点（已按实际口径改好）

- 读函数：`client.read_input_registers(address=0, count=4, device_id=1)`（功能码 04）
- 面板只显示 4 个计数，**无运行状态**（wRunState 已砍）
- pymodbus 3.15 注意：参数用 `device_id=`（旧名 `slave=` 已弃用）

---

## 五、调试步骤（分两步，先假后真）

### 5.1 第一步：模拟从站验证（不依赖 CODESYS，先确认主站脚本本身没问题）

1. 双击 `启动从站.bat`（启动模拟从站，假数据 [16,4,6,6]）
2. 双击 `启动主站.bat`
3. 预期主站面板显示：

```
  分拣总数 : 16
  红色计数 : 4
  蓝色计数 : 6
  绿色计数 : 6
```

> 这一步只验证「主站脚本能正常读 Input Register」。读不到 → 是脚本/端口问题，与 CODESYS 无关。

### 5.2 第二步：真实 PLC 验证（CODESYS 仿真器）

1. **先关掉模拟从站窗口**（否则占着 502 端口，仿真器起不来）
2. CODESYS 里 F11 编译 → Alt+F8 登录 localhost → 下载 → F5 运行
3. 双击 `启动主站.bat`
4. 预期：读到全 0（因为还没触发任何分拣）——**读到全 0 也是成功**，说明链路通了

### 5.3 让计数动起来（关键一步，否则永远全 0）

全 0 只能证明"链路通"，证明不了"数据实时更新"。必须让分拣动作发生、计数涨起来。两种方式：

#### 方式 A：手动在监视窗口强制输入（原始方式，繁琐）

在 CODESYS 监视窗口手动强制：
1. `iStart` 置 TRUE → 传送带转
2. `iColorCode` 写 `1` → `iDetect` 置 TRUE → 触发一次红色分拣 → 红色 +1、总数 +1
3. 依次换 2/3 验证蓝绿

> 缺点：要不停手动点，繁琐且容易漏，仅作补充手段。

#### 方式 B：自动演示块 FB_DemoFeeder（推荐，项目自己跑）

在工程里加一个「演示工件发生器」，仿真时自动模拟工件流（启动→到位→换色→分拣），计数自动累加：

**① GVL 内部变量区加一行：**

```iecst
    bSimMode : BOOL := TRUE;   // 仿真自动演示开关：TRUE=自动跑工件，FALSE=真实输入
```

**② 新建 POU：FB_DemoFeeder（功能块，ST 语言）**

```iecst
FUNCTION_BLOCK FB_DemoFeeder
// 演示工件发生器：仿真模式下自动模拟"工件到位 + 循环换色"
VAR_INPUT
    bEnable  : BOOL;    // TRUE=启用自动演示
END_VAR
VAR_OUTPUT
    bDetect  : BOOL;    // 模拟到位传感器（周期性脉冲）
    iColor   : INT;     // 模拟颜色代码（1红/2蓝/3绿循环）
END_VAR
VAR
    tOn      : TON;          // 到位阶段计时
    tOff     : TON;          // 间隙阶段计时
    bOn      : BOOL;         // 当前处于"到位"阶段
    iColorIdx: INT := 0;     // 颜色循环索引 1..3
END_VAR

IF bEnable THEN
    IF NOT bOn THEN
        bDetect := FALSE;
        tOn(IN := FALSE);
        tOff(IN := TRUE, PT := T#5S);
        IF tOff.Q THEN
            iColorIdx := iColorIdx + 1;
            IF iColorIdx > 3 THEN
                iColorIdx := 1;
            END_IF;
            iColor  := iColorIdx;
            bOn     := TRUE;
        END_IF;
    ELSE
        bDetect := TRUE;
        tOff(IN := FALSE);
        tOn(IN := TRUE, PT := T#1S);
        IF tOn.Q THEN
            bOn := FALSE;
        END_IF;
    END_IF;
ELSE
    bDetect  := FALSE;
    iColor   := 0;
    bOn      := FALSE;
    iColorIdx := 0;
    tOn(IN := FALSE);
    tOff(IN := FALSE);
END_IF;
```

**③ PLC_PRG 替换为（加 fbDemo 实例 + 输入源选择）：**

```iecst
PROGRAM PLC_PRG
VAR
    fbBelt  : FB_BeltControl;
    fbSort  : FB_Sorter;
    fbDemo  : FB_DemoFeeder;
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

GVL.wCountRed   := fbSort.wCountRed;
GVL.wCountBlue  := fbSort.wCountBlue;
GVL.wCountGreen := fbSort.wCountGreen;
GVL.wCountTotal := fbSort.wCountTotal;
```

> 说明：`SEL(G, A, B)` 是二选一函数，G=FALSE 取 A（真实输入）、G=TRUE 取 B（演示激励）。`iStart` 用 `OR GVL.bSimMode`（仿真模式直接自动开机）。演示节拍 = 到位 1 秒 + 间隙 5 秒 = 6 秒一个工件。接真机时把 `bSimMode` 改 FALSE 即恢复物理输入。

**④ 加完重新 F11 编译 → 下载 → F5 运行**，不用碰监视窗口，计数自动涨。再看主站窗口，数字自己跳。

---

## 六、验收清单（逐条）

| # | 操作 | 预期结果 | 判定 |
|---|------|----------|------|
| 1 | 模拟从站 + 主站 双开 | 主站读到 16/4/6/6 | 脚本本身 OK |
| 2 | 关模拟从站，CODESYS 仿真器运行，开主站 | 读到 0/0/0/0 | 链路通 |
| 3 | 加 FB_DemoFeeder 后重新下载运行 | 传送带自动转，推杆周期性动作 | 演示块工作 |
| 4 | 观察主站窗口（等待 >6 秒） | 总数/红/蓝/绿 依次自动 +1 | **数据实时更新，核心成功标志** |
| 5 | 计数复位（HMI 或监视窗口 bCntReset）后重读 | 计数归零后重新累加 | 复位链路正常 |

---

## 七、常见问题排错

### 7.1 主站「连接失败」
1. 从站（模拟器或仿真器）没在跑
2. 502 端口被旧进程占着 → 双击 `启动从站.bat`（内部会先清端口），或手动：
   ```powershell
   Get-NetTCPConnection -LocalPort 502 | Select-Object -ExpandProperty OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force }
   ```

### 7.2 读到全 0 且一直不变
- **先确认是不是真"通"了**：全 0 可能是链路通但没触发分拣。用方式 B 加演示块让计数动起来。
- 若加了演示块仍全 0：检查 I/O Mapping 里 4 个变量是否真绑上了（不是空的）。

### 7.3 主站报 `pymodbus 找不到`
- 终端 `python` 指向了别的版本。用 `py -3.14 -m pip install pymodbus` 装到 3.14。

### 7.4 模拟从站改了 REGISTERS 但主站没变
- 旧从站进程没退干净，重新双击 `启动从站.bat` 即可（会自动清端口）。

### 7.5 改了工程代码但计数没变化
- 没重新下载：Alt+F8 登录 → **Login with download（强制覆盖）** → F5，否则仿真器跑的还是旧程序。

---

## 八、关键结论（一句话）

- **从站**：ModbusTCP Server Device，无 Unit ID，Port 502，Input Register × 4
- **主站**：Python pymodbus，`read_input_registers(address=0, count=4, device_id=1)`（功能码 04）
- **数据动起来**：加 FB_DemoFeeder 自动演示块，仿真时计数自动累加，证明"实时读"成立
- **接真机**：`bSimMode` 改 FALSE 即回物理输入，其余不动

---

相关文档：《thesis代码.md》（GVL/程序结构）、《thesis需求文档.md》（Modbus 章节）、《thesis-ModbusTCP通信制作指示.md》（早期方案，口径以本文档为准）、《thesis调试文档.md》（仿真/登录/强制变量流程）。
