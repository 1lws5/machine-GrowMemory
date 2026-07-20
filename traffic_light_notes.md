# 交通灯项目学习笔记

## 当前进度

- **日期**：2026-07-20
- **阶段**：阶段二 - 自动循环控制综合练习
- **目标**：完成十字路口 6 步序交通灯，理解顺序控制 + 定时器 + 安全互锁

---

## 功能块 `FB_TrafficCross`

### 功能

十字路口交通灯顺序控制：东西向与南北向轮流放行，任何时刻仅允许一个方向绿灯。

### 接口

```iecst
FUNCTION_BLOCK FB_TrafficCross
VAR_INPUT
    iStart : BOOL;   // 启动
    iStop  : BOOL;   // 停止/急停
END_VAR

VAR_OUTPUT
    qEastRed    : BOOL;   // 东西向红灯
    qEastGreen  : BOOL;   // 东西向绿灯
    qEastYellow : BOOL;   // 东西向黄灯
    qNorthRed    : BOOL;  // 南北向红灯
    qNorthGreen  : BOOL;  // 南北向绿灯
    qNorthYellow : BOOL;  // 南北向黄灯
END_VAR

VAR
    iStep   : INT  := 0;      // 当前步序号
    tStep   : TON;            // 步序切换定时器
    tGreen  : TIME := T#5S;   // 绿灯持续时间
    tYellow : TIME := T#2S;   // 黄灯持续时间
    tAllRed : TIME := T#1S;   // 全红缓冲时间
END_VAR
```

> 注：当前时间参数在功能块内部预设，便于快速验证。后续版本将改为 `VAR_INPUT` 或从 GVL 传入，提高复用性。

---

## 核心逻辑

### 安全互锁

```iecst
// 危险场景检测：同时检测到两个绿灯或黄绿冲突，立即全红停机
IF (qEastGreen AND qNorthGreen) OR
   (qEastYellow AND qNorthGreen) OR
   (qEastGreen AND qNorthYellow) THEN
    iStep := 0;
    qEastRed := TRUE;  qEastGreen := FALSE; qEastYellow := FALSE;
    qNorthRed := TRUE; qNorthGreen := FALSE; qNorthYellow := FALSE;
    tStep(IN := FALSE);
    RETURN;
END_IF
```

### 停止逻辑

```iecst
IF iStop THEN
    iStep := 0;
    qEastRed := TRUE;  qEastGreen := FALSE; qEastYellow := FALSE;
    qNorthRed := TRUE; qNorthGreen := FALSE; qNorthYellow := FALSE;
    tStep(IN := FALSE);
    RETURN;
END_IF
```

### 启动逻辑

```iecst
IF iStart AND iStep = 0 THEN
    iStep := 1;
END_IF;
```

### 6 步序状态机

```iecst
CASE iStep OF
    // 步序控制器：iStep 为当前步序号，每步通过 tStep 定时切换

    1:  // 东西绿，南北红
        qEastRed := FALSE; qEastGreen := TRUE;  qEastYellow := FALSE;
        qNorthRed := TRUE; qNorthGreen := FALSE; qNorthYellow := FALSE;
        tStep(IN := TRUE, PT := tGreen);
        IF tStep.Q THEN tStep(IN := FALSE); iStep := 2; END_IF

    2:  // 东西黄，南北红
        qEastRed := FALSE; qEastGreen := FALSE; qEastYellow := TRUE;
        qNorthRed := TRUE; qNorthGreen := FALSE; qNorthYellow := FALSE;
        tStep(IN := TRUE, PT := tYellow);
        IF tStep.Q THEN tStep(IN := FALSE); iStep := 3; END_IF

    3:  // 全红缓冲
        qEastRed := TRUE; qEastGreen := FALSE; qEastYellow := FALSE;
        qNorthRed := TRUE; qNorthGreen := FALSE; qNorthYellow := FALSE;
        tStep(IN := TRUE, PT := tAllRed);
        IF tStep.Q THEN tStep(IN := FALSE); iStep := 4; END_IF

    4:  // 东西红，南北绿
        qEastRed := TRUE; qEastGreen := FALSE; qEastYellow := FALSE;
        qNorthRed := FALSE; qNorthGreen := TRUE;  qNorthYellow := FALSE;
        tStep(IN := TRUE, PT := tGreen);
        IF tStep.Q THEN tStep(IN := FALSE); iStep := 5; END_IF

    5:  // 东西红，南北黄
        qEastRed := TRUE; qEastGreen := FALSE; qEastYellow := FALSE;
        qNorthRed := FALSE; qNorthGreen := FALSE; qNorthYellow := TRUE;
        tStep(IN := TRUE, PT := tYellow);
        IF tStep.Q THEN tStep(IN := FALSE); iStep := 6; END_IF

    6:  // 全红缓冲
        qEastRed := TRUE; qEastGreen := FALSE; qEastYellow := FALSE;
        qNorthRed := TRUE; qNorthGreen := FALSE; qNorthYellow := FALSE;
        tStep(IN := TRUE, PT := tAllRed);
        IF tStep.Q THEN tStep(IN := FALSE); iStep := 1; END_IF

ELSE
    iStep := 0;
END_CASE
```

### 设计要点

1. **显式赋值**：每个步序对所有 6 个输出都重新赋值，不依赖上一步状态，避免脏状态。
2. **全红缓冲**：黄灯切换到另一方向绿灯之间，插入 1 秒全红缓冲，符合真实交通灯标准。
3. **软件互锁**：除状态机本身保证外，开头再加一层安全检测，任何异常组合直接全红停机。
4. **定时器复位**：每次步序切换时 `tStep(IN := FALSE)` 先断开通路，下一步再 `IN := TRUE`，确保 TON 正确重新计时。

---

## 调用主程序 `call_trafficCross`

```iecst
PROGRAM call_trafficCross
VAR
    fbLight : FB_TrafficCross;  // DFB 实例

    bStart : BOOL;   // 启动按钮
    bStop  : BOOL;   // 停止按钮

    bEastRed    : BOOL;   // 东西红灯输出
    bEastGreen  : BOOL;   // 东西绿灯输出
    bEastYellow : BOOL;   // 东西黄灯输出
    bNorthRed    : BOOL;  // 南北红灯输出
    bNorthGreen  : BOOL;  // 南北绿灯输出
    bNorthYellow : BOOL;  // 南北黄灯输出
END_VAR

fbLight(
    iStart      := bStart,
    iStop       := bStop,
    qEastRed    => bEastRed,
    qEastGreen  => bEastGreen,
    qEastYellow => bEastYellow,
    qNorthRed    => bNorthRed,
    qNorthGreen  => bNorthGreen,
    qNorthYellow => bNorthYellow
);
```

> 说明：输入管脚使用 `:=` 赋值，输出管脚使用 `=>` 连接。

---

## 时序表

| 步序 | 东西向 | 南北向 | 持续时间 |
|:----:|:------:|:------:|:--------:|
| 1 | 绿 | 红 | 5s |
| 2 | 黄 | 红 | 2s |
| 3 | 红 | 红 | 1s（全红缓冲）|
| 4 | 红 | 绿 | 5s |
| 5 | 红 | 黄 | 2s |
| 6 | 红 | 红 | 1s（全红缓冲）|

循环回到步序 1。

---

## 已知问题

- 功能块内部时间参数写死，复用性不够。后续版本将改为 `VAR_INPUT` 或 GVL 传入。
- 当前只在仿真环境中验证，尚未连接真机。

---

## 下一步计划

- 扩展为 10 步序交通灯，加入左转、右转灯位
- 每个状态使用独立 TON 定时器，避免单一定时器来回切换的复位问题
- 贴近真实交通灯国家标准（左转、直行、右转分离控制）
