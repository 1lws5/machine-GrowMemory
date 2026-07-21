# Machine GrowMemory - Schneider TM241 PLC 学习项目

## 项目简介
基于 Schneider Electric EcoStruxure Machine Expert 编程，使用 TM241C24R 控制器（仿真模式），系统学习 IEC 61131-3 PLC 编程。

## 软硬件环境
- **控制器**: Schneider TM241C24R（仅仿真，未接真机）
- **开发环境**: EcoStruxure Machine Expert Logic Builder V2.6
- **编程语言**: 梯形图 (LD) / 结构化文本 (ST)
- **软件内核**: 基于 Codesys 内核（IEC 61131-3 标准）

## 已完成练习

### 基础指令（阶段一）
| 序号 | 练习内容 | 编程语言 | 关键知识点 |
|------|---------|---------|-----------|
| 1 | 启保停控制 | 梯形图 | 自锁（OR 并联）、停止常闭触点 |
| 2 | 正反转互锁 | 梯形图 | 互锁（对方常闭串联）、iStop 总开关 |
| 3 | TON/TOF 定时器 | 梯形图 | PT 引脚需声明 TIME 变量、延时启停 |
| 4 | 星三角启动 | 梯形图 | 5 网络时序控制、主→星→延时→星断→三角 |
| 5 | CTU/CTD 计数器 | 梯形图 | CV 联动比较器 GE、计数到达触发 |
| 6 | 比较指令 | 梯形图 | Block 块不阻断能流、GE/GT/EQ |
| 7 | R_TRIG 边沿检测 | 梯形图 | 上升沿触发、单次脉冲 |
| 8 | SET/RESET 置位复位 | 梯形图 | 置位/复位线圈、保持型输出 |
| 9 | 单按钮启停 | 梯形图 | SET/RESET + 边沿检测组合应用 |
| 10 | MOVE 指令 + 步序状态机 | ST | INT 步序变量、CASE 分支、TON 复位逻辑 |

### 综合实战
- **自动循环控制**（ST 语言）：正转(5s) → 暂停(2s) → 反转(5s) → 暂停(2s) 循环
  - 使用 CASE 步序状态机（iStep: 0=停止, 1=正转, 2=暂停, 3=反转, 4=暂停）
  - TON 定时器每步切换时先断开 IN 实现 ET 清零后重新计时
  - 启保停 + 步序驱动 + 定时器驱动 + 输出赋值
- **十字路口交通灯（12步序带左转）**（ST 语言）
  - 功能块：`FB_TrafficCross`
  - 4组灯位：东西直行、东西左转、南北直行、南北左转
  - 时序：东西直行绿(5s)→黄(2s)→全红(1s)→东西左转绿(5s)→黄(2s)→全红(1s)→南北直行绿(5s)→黄(2s)→全红(1s)→南北左转绿(5s)→黄(2s)→全红(1s) 循环
  - 12个独立 TON 定时器，每步一个，避免单定时器复位问题
  - 安全设计：6种危险场景检测（双绿/黄绿冲突），立即全红停机
  - 详细说明见 `traffic_light_notes.md`

### 功能块封装（阶段二）
- **FB_AutoCycle DFB**：将自动循环控制封装为可复用功能块
  - 接口设计：VAR_INPUT（iStart, iStop, tFwdTime, tRevTime, tPauseTime）+ VAR_OUTPUT（qFwd, qRev, qRunning）
  - 黑盒封装：内部变量（iStep, tStep）对外不可见
  - 实战级安全保护：
    - 启动前输出清零
    - 非法步序保护（CASE ELSE 分支）
    - 软件互锁（qFwd AND qRev 同时为 TRUE 时停机）
  - 主程序通过管脚赋值调用（:= 输入，=> 输出）
- **重构：四个独立计时器替换单 tStep**
  - 原设计：单个 TON 定时器 tStep 在步序切换时需断开 IN 清零 ET，逻辑复杂
  - 重构后：每个步序使用独立 TON（tFwd, tPause1, tRev, tPause2），无需切换时复位
  - 优势：代码更清晰，各计时器独立运行互不干扰，消除 ET 清零时序隐患
  - 对 DFB 内部代码和主程序调用代码均添加了完整注释

## 核心代码：FB_AutoCycle DFB（ST）

```st
FUNCTION_BLOCK FB_AutoCycle

VAR_INPUT
    iStart       : BOOL;     (* 启动按钮 *)
    iStop        : BOOL;     (* 停止按钮 *)
    tFwdTime     : TIME;     (* 正转持续时间 *)
    tRevTime     : TIME;     (* 反转持续时间 *)
    tPauseTime   : TIME;     (* 步间暂停时间 *)
END_VAR

VAR_OUTPUT
    qFwd         : BOOL;     (* 正转输出 *)
    qRev         : BOOL;     (* 反转输出 *)
    qRunning     : BOOL;     (* 运行中标志 *)
END_VAR

VAR
    iStep        : INT;      (* 步序: 0=停止, 1=正转, 2=暂停, 3=反转, 4=暂停 *)
    tStep        : TON;      (* 步序定时器 *)
END_VAR

(* 启保停控制 *)
IF iStart AND NOT iStop THEN
    qRunning := TRUE;
    IF iStep = 0 THEN
        qFwd := FALSE;
        qRev := FALSE;
        iStep := 1;
    END_IF;
END_IF;

IF iStop THEN
    qRunning := FALSE;
    qFwd := FALSE;
    qRev := FALSE;
    iStep := 0;
    tStep(IN := FALSE);
END_IF;

(* 步序状态机 *)
IF qRunning THEN
    CASE iStep OF
        1:  (* 正转 *)
            qFwd := TRUE;
            qRev := FALSE;
            tStep(IN := TRUE, PT := tFwdTime);
            IF tStep.Q THEN
                iStep := 2;
                tStep(IN := FALSE);
            END_IF

        2:  (* 暂停1 *)
            qFwd := FALSE;
            qRev := FALSE;
            tStep(IN := TRUE, PT := tPauseTime);
            IF tStep.Q THEN
                iStep := 3;
                tStep(IN := FALSE);
            END_IF

        3:  (* 反转 *)
            qFwd := FALSE;
            qRev := TRUE;
            tStep(IN := TRUE, PT := tRevTime);
            IF tStep.Q THEN
                iStep := 4;
                tStep(IN := FALSE);
            END_IF

        4:  (* 暂停2 *)
            qFwd := FALSE;
            qRev := FALSE;
            tStep(IN := TRUE, PT := tPauseTime);
            IF tStep.Q THEN
                iStep := 1;
                tStep(IN := FALSE);
            END_IF

        ELSE  (* 非法步序保护 *)
            qFwd := FALSE;
            qRev := FALSE;
            qRunning := FALSE;
            iStep := 0;
            tStep(IN := FALSE);
    END_CASE;
END_IF;

(* 软件互锁：绝不允许正反转同时输出 *)
IF qFwd AND qRev THEN
    qFwd := FALSE;
    qRev := FALSE;
    qRunning := FALSE;
    iStep := 0;
    tStep(IN := FALSE);
END_IF;

END_FUNCTION_BLOCK
```

## DFB 调用方式（主程序）

```st
PROGRAM Automatic_Cycle_Control
VAR
    fbCycle : FB_AutoCycle;     (* DFB 实例 *)
    bStart  : BOOL;             (* 模拟启动按钮 *)
    bStop   : BOOL;             (* 模拟停止按钮 *)
    bFwd    : BOOL;             (* 正转输出 *)
    bRev    : BOOL;             (* 反转输出 *)
    bRun    : BOOL;             (* 运行标志 *)
END_VAR

fbCycle(
    iStart     := bStart,
    iStop      := bStop,
    tFwdTime   := T#5S,
    tRevTime   := T#5S,
    tPauseTime := T#2S,
    qFwd       => bFwd,
    qRev       => bRev,
    qRunning   => bRun
);
```

- **I/O 物理地址绑定（POU 内 AT 关键字）**
  - 在 PRG 程序（call_chage_interface）的 VAR 区直接使用 `AT` 关键字绑定物理地址
  - 输入：`bStart AT %IX0.0`、`bStop AT %IX0.1`（%IX = 数字量输入）
  - 输出：`bFwd AT %QX0.0`、`bRev AT %QX0.1`、`bRun AT %QX0.2`（%QX = 数字量输出）
  - DFB 实例 `fbCycle` 也在同一 POU 中声明，通过管脚赋值将物理 I/O 变量连接到 DFB
  - `:=` 用于输入管脚赋值，`=>` 用于输出管脚赋值
  - 编译通过：0 errors, 5 warnings (C0139: .ET 无效果，不影响运行)
  - 仿真环境下已可在 Watch 窗口监控 DFB 实例变量状态
  - GVL 全局变量与 POU 内绑定的区别：GVL 是全局可见，POU 内绑定仅本 POU 可见，学习阶段先用 POU 内绑定
  - 注意事项：
    - Watch 窗口可在 DFB 内部查看变量值，但 DFB 实例的输入变量不能从外部直接强制修改
    - 要测试程序需通过 Login 下载到仿真器后观察运行状态
    - 施耐德建议使用符号寻址（symbolic addressing）而非直接地址，但学习阶段先用直接地址理解原理

## 文件说明
- `MyFirstProject.project`: Machine Expert 主项目文件（二进制格式，需安装 Machine Expert 打开）
- `.gitignore`: 忽略临时文件、仿真文件、用户配置

## 学习路线
- ✅ 阶段一：基础指令（启保停、互锁、定时器、计数器、比较、边沿、置复位、状态机）
- 🔄 阶段二：功能块封装(DFB) ✅ → I/O 地址绑定 ✅ → 交通灯（6步序）✅ → 交通灯（12步序+左转）✅
- ⬜ 阶段三：通信协议(Modbus/OPC UA) → HMI 触摸屏 → 变频器控制

## 更新日志
- 2026-07-01: 初始化项目，创建启保停逻辑
- 2026-07-02: 添加正反转互锁、TON/TOF 定时器练习、星三角启动方案
- 2026-07-05: 添加 CTU/CTD 计数器、比较指令、R_TRIG 边沿检测、SET/RESET 练习
- 2026-07-06: 添加单按钮启停练习
- 2026-07-14: 完成 MOVE 指令 + 步序状态机自动循环控制（ST 语言），含 TON 复位逻辑修复
- 2026-07-17: 更新 README.md，整理所有已完成练习文档
- 2026-07-17: 完成 FB_AutoCycle DFB 功能块封装，含实战级互锁保护（启动清零+非法步序+软件互锁）
- 2026-07-18: 重构 DFB 内部计时器，四个独立 TON 替换单 tStep，添加完整注释
- 2026-07-19: 完成 I/O 物理地址绑定（PRG 内 AT 关键字），编译通过，仿真环境 Watch 窗口可监控 DFB 实例变量
- 2026-07-20: 完成十字路口 6 步序交通灯，封装为 FB_TrafficCross DFB，新增 `traffic_light_notes.md` 详细说明
- 2026-07-20: 升级为 12 步序带左转交通灯，4组灯位（东西直行/左转、南北直行/左转），12个独立TON定时器
