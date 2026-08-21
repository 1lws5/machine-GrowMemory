# thesis 传送带分拣控制系统 — 源代码

> 环境：CODESYS V3.5 SP22 Patch 3  
> 语言：ST（结构化文本，IEC 61131-3）  
> 方案：按颜色分拣（1条传送带 + 1个颜色传感器 + 1个到位传感器 + 3个气缸推杆）

## 项目结构

| 文件 | 类型 | 作用 |
|------|------|------|
| GVL | 全局变量表 | I/O地址绑定 + 内部变量 |
| FB_Pusher | 功能块 | 推杆控制（伸出2秒→回位1秒） |
| FB_BeltControl | 功能块 | 传送带启保停 + 暂停 |
| FB_Sorter | 功能块 | 颜色识别 + CASE分拣 + 计数 + 报警 |
| PLC_PRG | 主程序 | 调用各功能块，串联数据流 |

---

## 1. GVL（全局变量表）

```iecst
{attribute 'qualified_only'}
VAR_GLOBAL
    // ===== 物理输入（AT 绑定，接真实硬件）=====
    iStart      AT %IX0.0 : BOOL;   // 启动按钮（常开）
    iStop       AT %IX0.1 : BOOL;   // 停止按钮（常闭，真实接线时取反）
    iDetect     AT %IX0.2 : BOOL;   // 到位传感器
    iColorCode  AT %IW2   : INT;    // 颜色代码 1=红 2=蓝 3=绿 0=未识别

    // ===== 物理输出（AT 绑定，接真实硬件）=====
    qBelt       AT %QX0.0 : BOOL;   // 传送带电机
    qPushA      AT %QX0.1 : BOOL;   // 推杆A（红色）
    qPushB      AT %QX0.2 : BOOL;   // 推杆B（蓝色）
    qPushC      AT %QX0.3 : BOOL;   // 推杆C（绿色）
    qRunLight   AT %QX0.4 : BOOL;   // 运行指示灯
    qAlarmLight AT %QX0.5 : BOOL;   // 报警灯

    // ===== 内部变量（仿真用，无 AT 绑定）=====
    bAlarmReset : BOOL;             // 报警复位按钮
    bCntReset   : BOOL;             // 计数复位按钮
    wCountRed   : INT;              // 红色计数
    wCountBlue  : INT;              // 蓝色计数
    wCountGreen : INT;              // 绿色计数
    wCountTotal : INT;              // 总计数
END_VAR
```

> 地址说明：`%IX0.0~0.7` = 字节0，`%IX1.0~1.7` = 字节1。  
> `%IW0` = 字节0+1，会与 `%IX0.x` 冲突，所以颜色代码用 `%IW2`（字节2+3）。

---

## 2. FB_Pusher（推杆功能块）

```iecst
FUNCTION_BLOCK FB_Pusher   // 用于推杆的推出和收回的逻辑判断
VAR_INPUT
    bTrigger  : BOOL;      // 触发推杆动作，相当于一个推杆触发按钮
END_VAR
VAR_OUTPUT
    qPush     : BOOL;      // 推杆输出：告诉外面推杆当前该推还是该回
    bDone     : BOOL;      // 动作完成（回位了），是否归位
END_VAR
VAR
    tPush     : TON;       // 推杆延时计时器
    tRetract  : TON;       // 回位延时计时器
    iStep     : INT := 0;  // 0=待机 1=伸出 2=回位
END_VAR

CASE iStep OF
    0: // 待机
        qPush := FALSE;
        bDone := FALSE;
        tPush(IN := FALSE);       // 复位
        tRetract(IN := FALSE);    // 复位
        IF bTrigger THEN
            iStep := 1;
        END_IF;

    1: // 伸出2秒
        qPush := TRUE;
        tPush(IN := TRUE, PT := T#2S);
        tRetract(IN := FALSE);    // 回位计时器保持复位
        IF tPush.Q THEN
            iStep := 2;
        END_IF;

    2: // 回位1秒
        qPush := FALSE;
        tPush(IN := FALSE);       // 伸出计时器复位
        tRetract(IN := TRUE, PT := T#1S);
        IF tRetract.Q THEN
            iStep := 0;
            bDone := TRUE;
        END_IF;
END_CASE;

// TON 在状态机里，每个状态都要显式喂 IN：
//   正在计时的传 IN:=TRUE，不用的传 IN:=FALSE。
//   绝不能"不调用"让它靠粘性值，否则 Q 和 ET 残留导致误触发。

// 实际项目应采用两个传感器判断推杆位置：
//   推到底 → 推杆传感器变 TRUE，保持一会儿后开始收回；
//   收回到位 → 归位传感器变 TRUE，即可进行下一次推杆。
```

---

## 3. FB_BeltControl（传送带控制功能块）

```iecst
FUNCTION_BLOCK FB_BeltControl   // 传送带启保停 + 暂停
VAR_INPUT
    iStart    : BOOL;     // 启动按钮
    iStop     : BOOL;     // 停止按钮
    iPause    : BOOL;     // 暂停信号（来自分拣）
END_VAR
VAR_OUTPUT
    qBelt     : BOOL;     // 传送带电机
    qRunLight : BOOL;     // 运行灯
    bRunning  : BOOL;     // 运行状态（供分拣判断）
END_VAR
VAR
    bRunState : BOOL;     // 运行状态记忆
    rTrigStart: R_TRIG;   // 启动上升沿
    rTrigStop : R_TRIG;   // 停止上升沿
END_VAR

// 启动上升沿
rTrigStart(CLK := iStart);
IF rTrigStart.Q THEN
    bRunState := TRUE;
END_IF;

// 停止上升沿
rTrigStop(CLK := iStop);
IF rTrigStop.Q THEN
    bRunState := FALSE;
END_IF;

// 运行状态 AND NOT 暂停
qBelt     := bRunState AND NOT iPause;
qRunLight := bRunState AND NOT iPause;
bRunning  := bRunState AND NOT iPause;
```

> 设计说明：`bRunState` 记忆运行状态，启动置 TRUE、停止置 FALSE。  
> 暂停只影响输出，不改 bRunState——所以暂停解除后自动恢复运行，不用重新按启动。

---

## 4. FB_Sorter（分拣功能块）

```iecst
FUNCTION_BLOCK FB_Sorter   // 根据不同颜色推不同的杆，分拣判断逻辑
VAR_INPUT
    iDetect    : BOOL;     // 到位传感器
    iColorCode : INT;      // 颜色代码
    bRunning   : BOOL;     // 传送带运行中
    bAlarmReset: BOOL;     // 报警复位
    bCntReset  : BOOL;     // 计数复位按钮
END_VAR
VAR_OUTPUT
    qPushA     : BOOL;     // 推杆A触发
    qPushB     : BOOL;     // 推杆B触发
    qPushC     : BOOL;     // 推杆C触发
    qAlarmLight: BOOL;     // 报警灯
    wCountRed  : INT;      // 红色计数
    wCountBlue : INT;      // 蓝色计数
    wCountGreen: INT;      // 绿色计数
    wCountTotal: INT;      // 总计数
    bPause     : BOOL;     // 暂停传送带
    bSortDone  : BOOL;     // 本工件分拣完成（单周期脉冲，供上层/HMI使用）
END_VAR
VAR
    rTrigDetect: R_TRIG;   // 到位上升沿
    rTrigReset : R_TRIG;   // 报警复位上升沿
    rTrigCntRst: R_TRIG;   // 计数复位上升沿
    rDone      : R_TRIG;   // 完成脉冲生成
    fbPushA    : FB_Pusher; // 推杆A实例
    fbPushB    : FB_Pusher; // 推杆B实例
    fbPushC    : FB_Pusher; // 推杆C实例
    bSorting   : BOOL;     // 正在分拣（锁存标记）
    bDoneLatch : BOOL;     // 完成锁存（生成脉冲用）
END_VAR

// 到位传感器上升沿检测
rTrigDetect(CLK := iDetect);
IF rTrigDetect.Q AND bRunning AND NOT bSorting THEN
    bSorting := TRUE;   // 锁住判断，防止二次触发
    bPause := TRUE;     // 暂停传送带，开始分拣

    // 颜色分拣
    CASE iColorCode OF
        1: // 红色
            qPushA := TRUE;
            wCountRed := wCountRed + 1;
        2: // 蓝色
            qPushB := TRUE;
            wCountBlue := wCountBlue + 1;
        3: // 绿色
            qPushC := TRUE;
            wCountGreen := wCountGreen + 1;
        ELSE // 未识别
            qAlarmLight := TRUE;  // 报警锁存：置位后保持，需人工复位解锁
    END_CASE;
    wCountTotal := wCountTotal + 1;  // 不管推了啥，总计数+1
END_IF;

// 调用推杆功能块
fbPushA(bTrigger := qPushA);
fbPushB(bTrigger := qPushB);
fbPushC(bTrigger := qPushC);

// 推杆完成后清除触发
IF fbPushA.bDone THEN qPushA := FALSE; END_IF;
IF fbPushB.bDone THEN qPushB := FALSE; END_IF;
IF fbPushC.bDone THEN qPushC := FALSE; END_IF;

// 所有推杆回位后恢复传送带
IF bSorting AND NOT qPushA AND NOT qPushB AND NOT qPushC AND NOT qAlarmLight THEN
    bSorting := FALSE;
    bPause := FALSE;
    bDoneLatch := TRUE;     // 置锁存
ELSE
    bDoneLatch := FALSE;    // 清锁存：但凡有一个还在工作，就是没完成
END_IF;

// 用 R_TRIG 显式生成 bSortDone 单周期脉冲
rDone(CLK := bDoneLatch);
bSortDone := rDone.Q;

// 报警复位（上升沿触发）
rTrigReset(CLK := bAlarmReset);
IF rTrigReset.Q THEN
    qAlarmLight := FALSE;
END_IF;

// 计数复位（上升沿触发）
rTrigCntRst(CLK := bCntReset);
IF rTrigCntRst.Q THEN
    wCountRed := 0; wCountBlue := 0;
    wCountGreen := 0; wCountTotal := 0;
END_IF;
```

---

## 5. PLC_PRG（主程序）

> PLC_PRG 是**编排层（Orchestration）**：职责只有三件事——实例化功能块、给管脚接线、搬运数据。
> 业务逻辑全在功能块里，主程序一行业务逻辑（IF/CASE/计时器）都不写。

```iecst
PROGRAM PLC_PRG
VAR
    fbBelt  : FB_BeltControl;
    fbSort  : FB_Sorter;
END_VAR

// ===== PLC_PRG：编排层，只做"造实例 + 接线 + 搬运数据" =====

// 调用传送带控制
fbBelt(
    iStart := GVL.iStart,          // 绑定物理输入（启动按钮）
    iStop  := GVL.iStop,           // 绑定物理输入（停止按钮）
    iPause := fbSort.bPause        // 分拣时 fbSort 输出的暂停信号，让传送带停下等推杆动作
);

// 传送带输出 → 绑定物理输出
GVL.qBelt     := fbBelt.qBelt;     // 传送带电机
GVL.qRunLight := fbBelt.qRunLight; // 运行指示灯

// 调用分拣逻辑
fbSort(
    iDetect     := GVL.iDetect,      // 绑定物理输入（到位传感器）
    iColorCode  := GVL.iColorCode,   // 绑定物理输入（颜色传感器）
    bRunning    := fbBelt.bRunning,  // 读取传送带运行状态
    bAlarmReset := GVL.bAlarmReset,  // 无IO绑定，HMI操作，报警复位信号
    bCntReset   := GVL.bCntReset     // 无IO绑定，HMI操作，计数复位信号
);

// 推杆输出 → 绑定物理输出
GVL.qPushA      := fbSort.qPushA;      // 推杆A
GVL.qPushB      := fbSort.qPushB;      // 推杆B
GVL.qPushC      := fbSort.qPushC;      // 推杆C
GVL.qAlarmLight := fbSort.qAlarmLight; // 报警指示灯

// 计数 → 供 HMI 显示
GVL.wCountRed   := fbSort.wCountRed;   // 红色计数
GVL.wCountBlue  := fbSort.wCountBlue;  // 蓝色计数
GVL.wCountGreen := fbSort.wCountGreen; // 绿色计数
GVL.wCountTotal := fbSort.wCountTotal; // 总计数
```

---

## 核心知识点备忘

1. **TON 计时两个必要条件**：每个扫描周期都被调用 + IN 持续 TRUE。
2. **状态机里定时器要显式喂 IN**：正在计时的传 `IN:=TRUE`，不用的传 `IN:=FALSE`，不能靠"不调用"粘性值。
3. **CASE 状态机**：单个整数 `iStep` 表达多状态，比多个布尔标志更清晰、更不易出 bug。
4. **`AT` 地址绑定**：物理 I/O 用 `AT %IX/%QX` 绑定；内部变量（复位、计数）不绑定，仿真靠监视窗口强制。
5. **`{attribute 'qualified_only'}`**：全局变量必须用 `GVL.xxx` 限定名访问，避免重名冲突。

详细调试步骤见《thesis调试文档.md》。
