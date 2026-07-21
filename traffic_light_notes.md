# 交通灯项目学习笔记

## 当前进度

- **日期**：2026-07-20
- **阶段**：阶段二 - 自动循环控制综合练习
- **目标**：完成十字路口交通灯顺序控制，理解顺序控制 + 定时器 + 安全互锁

---

## 版本1：6步序交通灯（已归档）

### 功能

十字路口交通灯顺序控制：东西向与南北向轮流放行，任何时刻仅允许一个方向绿灯。

### 时序表

| 步序 | 东西向 | 南北向 | 持续时间 |
|:----:|:------:|:------:|:--------:|
| 1 | 绿 | 红 | 5s |
| 2 | 黄 | 红 | 2s |
| 3 | 红 | 红 | 1s（全红缓冲）|
| 4 | 红 | 绿 | 5s |
| 5 | 红 | 黄 | 2s |
| 6 | 红 | 红 | 1s（全红缓冲）|

### 功能块：FB_TrafficCross

6 个输出（东西红绿黄 + 南北红绿黄），1 个 TON 定时器，CASE 步序切换。

---

## 版本2：12步序交通灯带左转（当前版本）

### 功能

十字路口交通灯顺序控制，增加左转灯位，4 组灯（东西直行、东西左转、南北直行、南北左转），12 步序循环。

### 时序表

| 步序 | 东西直行 | 东西左转 | 南北直行 | 南北左转 | 持续时间 | 说明 |
|:----:|:--------:|:--------:|:--------:|:--------:|:--------:|:-----|
| 1 | 绿 | 红 | 红 | 红 | tGreen | 东西直行放行 |
| 2 | 黄 | 红 | 红 | 红 | tYellow | 东西直行黄灯 |
| 3 | 红 | 红 | 红 | 红 | tAllRed | 全红缓冲 |
| 4 | 红 | 绿 | 红 | 红 | tGreen | 东西左转放行 |
| 5 | 红 | 黄 | 红 | 红 | tYellow | 东西左转黄灯 |
| 6 | 红 | 红 | 红 | 红 | tAllRed | 全红缓冲 |
| 7 | 红 | 红 | 绿 | 红 | tGreen | 南北直行放行 |
| 8 | 红 | 红 | 黄 | 红 | tYellow | 南北直行黄灯 |
| 9 | 红 | 红 | 红 | 红 | tAllRed | 全红缓冲 |
| 10 | 红 | 红 | 红 | 绿 | tGreen | 南北左转放行 |
| 11 | 红 | 红 | 红 | 黄 | tYellow | 南北左转黄灯 |
| 12 | 红 | 红 | 红 | 红 | tAllRed | 全红缓冲，循环回步序1 |

### 功能块：FB_TrafficCross（12步序版）

#### 接口

```iecst
FUNCTION_BLOCK FB_TrafficCross
VAR_INPUT
    iStart   : BOOL;     // 启动
    iStop    : BOOL;     // 停止/急停
    tGreen   : TIME := T#5S;   // 绿灯持续时间
    tYellow  : TIME := T#2S;   // 黄灯持续时间
    tAllRed  : TIME := T#1S;   // 全红缓冲时间
END_VAR

VAR_OUTPUT
    // 东西直行组
    qEast_Straight_Red    : BOOL;
    qEast_Straight_Green  : BOOL;
    qEast_Straight_Yellow : BOOL;
    // 东西左转组
    qEast_turnLeft_Red    : BOOL;
    qEast_turnLeft_Green  : BOOL;
    qEast_turnLeft_Yellow : BOOL;
    // 南北直行组
    qNorth_Straight_Red    : BOOL;
    qNorth_Straight_Green  : BOOL;
    qNorth_Straight_Yellow : BOOL;
    // 南北左转组
    qNorth_turnLeft_Red    : BOOL;
    qNorth_turnLeft_Green  : BOOL;
    qNorth_turnLeft_Yellow : BOOL;
END_VAR

VAR
    iStep      : INT := 0;     // 当前步序号
    oneStep    : TON;           // 步序1定时器
    twoStep    : TON;           // 步序2定时器
    thrStep    : TON;           // 步序3定时器
    fouStep    : TON;           // 步序4定时器
    fiveStep   : TON;           // 步序5定时器
    sixStep    : TON;           // 步序6定时器
    sevStep    : TON;           // 步序7定时器
    eigStep    : TON;           // 步序8定时器
    ninStep    : TON;           // 步序9定时器
    tenStep    : TON;           // 步序10定时器
    eleStep    : TON;           // 步序11定时器
    twlStep    : TON;           // 步序12定时器
END_VAR
```

#### 核心逻辑

**安全互锁（6种危险场景检测）：**

```iecst
IF (qEast_Straight_Green AND qNorth_Straight_Green) OR       // 东西直行绿 + 南北直行绿
   (qEast_Straight_Yellow AND qNorth_Straight_Green) OR      // 东西直行黄 + 南北直行绿
   (qEast_Straight_Green AND qNorth_Straight_Yellow) OR     // 东西直行绿 + 南北直行黄
   (qNorth_Straight_Green AND qEast_turnLeft_Green) OR      // 南北直行绿 + 东西左转绿
   (qEast_turnLeft_Yellow AND qNorth_turnLeft_Green) OR     // 东西左转黄 + 南北左转绿
   (qNorth_turnLeft_Yellow AND qEast_Straight_Green)        // 南北左转黄 + 东西直行绿
THEN
    // 全红停机，归位
    iStep := 0;
    // ...所有红灯 TRUE，其他 FALSE...
    // 所有定时器 IN := FALSE
    RETURN;
END_IF
```

**12步序 CASE 状态机：**

每步流程：
1. 显式赋值所有 12 个输出（红/绿/黄）
2. 启动该步定时器 `IN := TRUE, PT := tXxx`
3. 定时到达 `IF xStep.Q THEN xStep(IN := FALSE); iStep := N+1; END_IF`

步序循环：1→2→3→4→5→6→7→8→9→10→11→12→1

### 调用主程序

```iecst
PROGRAM call_trafficCross
VAR
    fbTwelve : FB_TrafficCross;   // DFB 实例

    bStart : BOOL;                // 启动按钮
    bStop  : BOOL;                // 停止按钮

    // 东西直行组
    bEast_Straight_Red    : BOOL;
    bEast_Straight_Green  : BOOL;
    bEast_Straight_Yellow : BOOL;
    // 东西左转组
    bEast_turnLeft_Red    : BOOL;
    bEast_turnLeft_Green  : BOOL;
    bEast_turnLeft_Yellow : BOOL;
    // 南北直行组
    bNorth_Straight_Red    : BOOL;
    bNorth_Straight_Green  : BOOL;
    bNorth_Straight_Yellow : BOOL;
    // 南北左转组
    bNorth_turnLeft_Red    : BOOL;
    bNorth_turnLeft_Green  : BOOL;
    bNorth_turnLeft_Yellow : BOOL;
END_VAR

fbTwelve(
    iStart := bStart,
    iStop  := bStop,
    qEast_Straight_Red    => bEast_Straight_Red,
    qEast_Straight_Green  => bEast_Straight_Green,
    qEast_Straight_Yellow => bEast_Straight_Yellow,
    qEast_turnLeft_Red    => bEast_turnLeft_Red,
    qEast_turnLeft_Green  => bEast_turnLeft_Green,
    qEast_turnLeft_Yellow => bEast_turnLeft_Yellow,
    qNorth_Straight_Red    => bNorth_Straight_Red,
    qNorth_Straight_Green  => bNorth_Straight_Green,
    qNorth_Straight_Yellow => bNorth_Straight_Yellow,
    qNorth_turnLeft_Red    => bNorth_turnLeft_Red,
    qNorth_turnLeft_Green  => bNorth_turnLeft_Green,
    qNorth_turnLeft_Yellow => bNorth_turnLeft_Yellow
);
```

### 设计要点

1. **显式赋值**：每个步序对所有 12 个输出都重新赋值，不依赖上一步状态，避免脏状态。
2. **全红缓冲**：黄灯切换到另一方向绿灯之间，插入全红缓冲，符合真实交通灯标准。
3. **软件互锁**：6 种危险场景检测，任何异常组合直接全红停机。
4. **定时器复位**：每次步序切换时 `IN := FALSE` 先断开，下一步再 `IN := TRUE`，确保 TON 正确重新计时。
5. **12 个独立定时器**：每步使用独立 TON，避免单定时器来回切换的复位问题。

### 已知问题

- 停机和安全函数中漏了 `twlStep(IN := FALSE)` 复位（需修复）
- 时间参数在功能块内部预设，后续版本改为 VAR_INPUT 或 GVL 传入
- 实例名 `fbTwelve` 建议改为 `fbTraffic` 更直观
- 仅在仿真环境中验证，未连接真机
