# 传送带分拣控制系统 — HMI 制作指示文档

| 项目 | 内容 |
|------|------|
| 环境 | CODESYS V3.5 SP22 Patch 3 |
| 仿真器 | CODESYS Control Win V3 x64 |
| HMI 类型 | WebVisu（浏览器可视化） |
| 页面数 | 3 页（主控 / 分拣监控 / 报警） |
| 设计原则 | 无自建逻辑，控件直接绑定 GVL 变量 |

## 一、概述与准备工作

**HMI 只做一件事：把 GVL 里的变量显示到屏幕上、把屏幕上的操作写回 GVL 变量。**

所有逻辑（启保停、分拣、报警、计数）已经写在 PLC 程序里，HMI 不写任何业务逻辑，只做"显示"和"输入"。

### 1.1 前提条件

- 工程已编译通过（F11，0 error）。
- GVL 变量已定义齐全（见下表）。
- 仿真器 CODESYS Control Win SysTray 已安装（阶段三已装好）。

### 1.2 GVL 变量清单（HMI 会用到这些）

| 变量名 | 类型 | 地址 | HMI 用途 |
|--------|------|------|----------|
| iStart | BOOL | %IX0.0 | 启动按钮（点击写值） |
| iStop | BOOL | %IX0.1 | 停止按钮（点击写值） |
| iColorCode | INT | %IW2 | 当前颜色代码显示 |
| qBelt | BOOL | %QX0.0 | 传送带动画 / 状态 |
| qPushA | BOOL | %QX0.1 | 推杆A状态灯 |
| qPushB | BOOL | %QX0.2 | 推杆B状态灯 |
| qPushC | BOOL | %QX0.3 | 推杆C状态灯 |
| qRunLight | BOOL | %QX0.4 | 运行指示灯 |
| qAlarmLight | BOOL | %QX0.5 | 报警指示灯 |
| wCountRed | INT | 内部 | 红色计数显示 |
| wCountBlue | INT | 内部 | 蓝色计数显示 |
| wCountGreen | INT | 内部 | 绿色计数显示 |
| wCountTotal | INT | 内部 | 总计数显示 |
| bAlarmReset | BOOL | 内部 | 报警复位按钮（点击写值） |
| bCntReset | BOOL | 内部 | 计数复位按钮（点击写值） |

> **注意**：iStart / iStop / bAlarmReset / bCntReset 是"写"变量（HMI 按钮 → PLC）；其余是"读"变量（PLC → HMI 显示）。

## 二、创建可视化对象

### 2.1 添加可视化管理器（Visualization Manager）

1. 左侧设备树 → 右键 Application → 添加对象 → 可视化管理器（Visualization Manager）。
2. 管理器属性中勾选 "Use unicode strings"（支持中文显示）。
3. 勾选 "支持 WebVisu" 相关选项（激活浏览器访问）。

管理器是 HMI 的"总开关"，必须有它才能让可视化跑起来。

### 2.2 添加 3 个可视化页面

| 页面名 | 作用 | 对应章节 |
|--------|------|----------|
| VisuMain | 主控页（启停/运行灯/传送带） | 第四章 |
| VisuMonitor | 分拣监控页（计数/颜色/推杆） | 第五章 |
| VisuAlarm | 报警页（报警灯/复位） | 第六章 |

1. 右键 Application → 添加对象 → 可视化（Visualization）。
2. 名称填 VisuMain，类型选 "Target visualization"（目标可视化）。
3. 重复以上两步，创建 VisuMonitor 和 VisuAlarm。

### 2.3 设置起始页面

1. 双击打开可视化管理器。
2. 在"WebVisu"标签页，把起始可视化（Start Visualization）设为 VisuMain。

这样浏览器打开 HMI 时，默认显示主控页。

## 三、变量映射总表（一图看懂全部控件）

下面这张表是本文档的核心，做完所有页面后回来逐条核对。

| 页面 | 控件 | 绑定变量 | 类型 | 操作 / 动画 |
|------|------|----------|------|-------------|
| 主控页 | 启动按钮 | GVL.iStart | BOOL | 按下写TRUE，松开写FALSE |
| 主控页 | 停止按钮 | GVL.iStop | BOOL | 按下写TRUE，松开写FALSE |
| 主控页 | 运行指示灯 | GVL.qRunLight | BOOL | 颜色动画（绿=运行） |
| 主控页 | 报警指示灯 | GVL.qAlarmLight | BOOL | 颜色动画（红=报警） |
| 主控页 | 传送带 | GVL.qBelt | BOOL | 颜色/显隐动画 |
| 主控页 | 跳转按钮×2 | — | — | 切换到监控页/报警页 |
| 监控页 | 颜色代码显示 | GVL.iColorCode | INT | 文本变量显示 |
| 监控页 | 红色计数 | GVL.wCountRed | INT | 文本变量显示 |
| 监控页 | 蓝色计数 | GVL.wCountBlue | INT | 文本变量显示 |
| 监控页 | 绿色计数 | GVL.wCountGreen | INT | 文本变量显示 |
| 监控页 | 总计数 | GVL.wCountTotal | INT | 文本变量显示 |
| 监控页 | 计数复位按钮 | GVL.bCntReset | BOOL | 按下写TRUE，松开写FALSE |
| 监控页 | 推杆A/B/C状态灯 | GVL.qPushA/B/C | BOOL | 颜色动画 |
| 监控页 | 返回主控页 | — | — | 切换回主控页 |
| 报警页 | 报警指示灯 | GVL.qAlarmLight | BOOL | 颜色动画 |
| 报警页 | 报警文字提示 | GVL.qAlarmLight | BOOL | 显隐动画 |
| 报警页 | 报警复位按钮 | GVL.bAlarmReset | BOOL | 按下写TRUE，松开写FALSE |
| 报警页 | 返回主控页 | — | — | 切换回主控页 |

> **绑定语法统一用 `GVL.变量名`**（因为 GVL 声明了 qualified_only，必须带前缀）。

## 四、主控页 VisuMain 制作

### 4.1 页面布局建议

```
┌─────────────────────────────────────────┐
│        传送带分拣控制系统（标题）        │
│                                          │
│   [运行指示灯]   [报警指示灯]            │
│                                          │
│   ══════ 传送带动画区域 ══════          │
│   ( 传送带 )                            │
│                                          │
│   [启动按钮]   [停止按钮]               │
│                                          │
│   [分拣监控页]   [报警页]  ← 跳转按钮   │
└─────────────────────────────────────────┘
```

### 4.2 标题文字

- 工具箱拖一个 Text field（文本框）到顶部。
- 文本内容填 "传送带分拣控制系统"，字号调大（如 28），加粗。
- 标题不绑变量，是静态文字。

### 4.3 启动 / 停止按钮

1. 工具箱拖一个 Button（按钮）到画布。
2. 双击按钮改文字为 "启动"。
3. 选中按钮 → 属性 → 输入配置（Input configuration）。
4. OnMouseDown 填：`GVL.iStart := TRUE;`
5. OnMouseUp 填：`GVL.iStart := FALSE;`

停止按钮同理，绑定 GVL.iStop。

> 为什么按下 TRUE 松开 FALSE：程序里 iStart 是"启动脉冲"，FB_BeltControl 靠它自锁（置 bRunning=TRUE 后保持），所以点一下松开即可，无需按住。

### 4.4 运行 / 报警指示灯

1. 拖一个 Rectangle（矩形）或 Lamp（灯）控件。
2. 运行灯：属性 → 颜色变量（Color variables）→ 填充颜色。
3. 添加变量 GVL.qRunLight。
4. 配置：FALSE = 灰色(#C0C0C0)，TRUE = 绿色(#00C000)。

报警灯同理，绑定 GVL.qAlarmLight，TRUE = 红色(#C00000)。

### 4.5 传送带怎么画（没有现成控件，自己拼）

**重要说明：Codesys 可视化工具箱里【没有】现成的"传送带"图形。工具箱只有两类元素：**

- 基础图形：Rectangle（矩形）、Ellipse（椭圆）、Line（线）、Polygon（多边形）、Rounded Rectangle（圆角矩形）。
- 常用控件：Button（按钮）、Lamp（灯）、Text field（文本框）、Image（图片）等。

工业设备图（传送带、气缸、电机）都要用基础图形拼装，或用 Image 控件导入图片。下面讲用矩形拼的最简画法。

#### 4.5.1 用矩形拼传送带（5 步）

1. **框架/底座**：拖一个 Rectangle（长方形），约 400×30，填充深灰 #808080。静态装饰，不绑变量。
2. **两端滚筒**：各拖一个小 Rectangle 或 Ellipse（约 20×36 竖着），深灰，表示滚筒。静态装饰。
3. **皮带**：在底座上再叠一个稍窄的 Rectangle（约 380×16），这一层绑定 GVL.qBelt。
4. **物体/箱子**：拖一个小正方形 Rectangle（约 24×24），橙色，表示待分拣工件。
5. **推杆/气缸**：拖一个小 Rectangle 表示推杆，绑定 GVL.qPushA/B/C（见 5.4）。

> **关键：只有"皮带"那一层绑 qBelt 变量，框架和滚筒是静态背景，不绑。**

#### 4.5.2 皮带绑定颜色动画

1. 选中皮带那个 Rectangle → 属性 → 颜色变量（Color variables）→ 填充颜色。
2. 添加变量 GVL.qBelt。
3. 配置：FALSE = 灰色 #C0C0C0（停止），TRUE = 绿色 #00C000（运行中）。

简化版用颜色变化表示"运行/停止"，无需自建滚动变量，符合"无自建逻辑"原则。

#### 4.5.3 备选：用 Image 导入传送带图片

1. 找一个传送带的 .svg 或 .png 图片（可网上搜 "conveyor belt svg"）。
2. CODESYS 菜单 → 可视化 → 图像池（Image Pool）→ 添加图片。
3. 工具箱拖一个 Image 控件，图像源选刚导入的图片。
4. Image 同样可以绑颜色变量 GVL.qBelt 做变色，或绑显隐。

> 注：图片是死的，做"运行/停止"只能用变色/换图，不能做滚动动画。滚动动画需用基础图形+移动动画（见 7.3）。

### 4.6 跳转按钮

1. 拖两个 Button，文字分别为 "分拣监控页"、"报警页"。
2. 选中按钮 → 属性 → 输入配置 → 选择 "Change displayed visualization"（切换显示的可视化）。
3. 目标分别选 VisuMonitor 和 VisuAlarm。

## 五、分拣监控页 VisuMonitor 制作

### 5.1 页面布局建议

```
┌─────────────────────────────────────────┐
│        分拣监控页                        │
│                                          │
│  当前颜色代码：[ 0 ]  (0未识别/1红/2蓝/3绿)│
│                                          │
│  红色计数：[ 0 ]   蓝色计数：[ 0 ]       │
│  绿色计数：[ 0 ]   总计数：[ 0 ]         │
│                                          │
│  推杆A：[●] 推杆B：[●] 推杆C：[●]        │
│                                          │
│  [计数复位按钮]      [返回主控页]        │
└─────────────────────────────────────────┘
```

### 5.2 计数 / 颜色代码显示（文本变量）

1. 拖一个 Text field，文本内容先写一个占位符 `%s`。
2. 选中 → 属性 → 文本变量（Text variables）→ 添加变量 GVL.wCountRed。
3. 这样文本框会实时显示红色计数的数值。

其余 wCountBlue / wCountGreen / wCountTotal / iColorCode 同理，各拖一个文本框绑定。

### 5.3 颜色代码的文字映射（可选优化）

- 直接显示数字 0/1/2/3 不够直观，可在旁边加一段静态说明文字 "0=未识别 1=红 2=蓝 3=绿"。
- 进阶：用显隐动画让 "红色/蓝色/绿色/未识别" 四个文字标签根据 iColorCode 值分别显示（见 7.2）。

### 5.4 推杆状态灯

1. 拖三个 Rectangle 或 Lamp，标注 "推杆A/B/C"。
2. 分别绑定 GVL.qPushA / GVL.qPushB / GVL.qPushC。
3. 颜色动画：TRUE = 绿色（伸出中），FALSE = 灰色（回位）。

### 5.5 计数复位按钮

- 拖 Button，文字 "计数复位"。
- OnMouseDown：`GVL.bCntReset := TRUE;`
- OnMouseUp：`GVL.bCntReset := FALSE;`

程序里 bCntReset 用 R_TRIG 上升沿检测，按下这一下就会清零四个计数。

## 六、报警页 VisuAlarm 制作

### 6.1 页面布局建议

```
┌─────────────────────────────────────────┐
│           报警页                         │
│                                          │
│   [报警指示灯]   （红=报警，灭=正常）     │
│                                          │
│   提示：检测到颜色未识别（iColorCode=0） │
│                                          │
│   [报警复位按钮]      [返回主控页]        │
└─────────────────────────────────────────┘
```

### 6.2 报警指示灯

- 拖 Rectangle，颜色变量绑定 GVL.qAlarmLight。
- TRUE = 红色（报警），FALSE = 绿色/灰色（正常）。

### 6.3 报警文字提示（显隐动画）

1. 拖 Text field，文字 "⚠ 颜色未识别，请检查传感器或物品"。
2. 选中 → 属性 → 可见性（Visibility / 显示变量）。
3. 绑定 GVL.qAlarmLight，TRUE = 显示，FALSE = 隐藏。

这样只有报警时文字才出现，正常时干净。

### 6.4 报警复位按钮

- 拖 Button，文字 "报警复位"。
- OnMouseDown：`GVL.bAlarmReset := TRUE;`
- OnMouseUp：`GVL.bAlarmReset := FALSE;`

程序里 bAlarmReset 用 R_TRIG 上升沿检测，点击一次清除报警锁存。

## 七、动画配置详解

### 7.1 颜色动画（Color variables）—— 最常用

用途：让指示灯、传送带、推杆状态随 BOOL 变量变色。

1. 选中控件 → 属性面板 → 找到 "颜色变量"（Color variables）。
2. 点 "填充颜色"（Fill color）旁的编辑按钮。
3. 添加变量 GVL.xxx，出现一行条件配置。
4. 分别设置 FALSE 和 TRUE 对应的颜色。

| 控件 | FALSE 颜色 | TRUE 颜色 |
|------|-----------|-----------|
| 运行灯 qRunLight | 灰 #C0C0C0 | 绿 #00C000 |
| 报警灯 qAlarmLight | 灰 #C0C0C0 | 红 #C00000 |
| 推杆 qPushA/B/C | 灰 #C0C0C0 | 绿 #00C000 |
| 传送带 qBelt | 灰 #C0C0C0 | 绿 #00C000 |

### 7.2 显隐动画（Visibility）

用途：根据 BOOL 变量让文字/图形出现或消失。

- 选中控件 → 属性 → 显示变量（Visibility / Display variable）。
- 绑定 GVL.qAlarmLight 等 BOOL 变量。
- 配置：TRUE = 显示，FALSE = 隐藏。

报警文字提示、颜色文字标签都可用这个实现。

### 7.3 移动动画（Absolute movement）—— 进阶可选

用途：让传送带条纹真正"滚动"，更逼真。

> **注意：需要一个不断递增的整数变量，而当前 GVL 没有，属于"自建逻辑"，与已确认方案冲突。**

如需实现（可选，不做不影响验收）：

1. GVL 增加一个内部变量：`wBeltAnim : INT := 0;`
2. PLC_PRG 末尾加一句：`GVL.wBeltAnim := GVL.wBeltAnim + 1;`（每周期+1，溢出后自动回绕）。
3. 传送带条纹 → 属性 → 绝对移动（Absolute movement）→ X 方向绑定 GVL.wBeltAnim。
4. 配置移动范围，条纹循环滚动，模拟传送带前进。

> 结论：本项目用简化版（颜色动画）即可，进阶滚动留作课后兴趣。

## 八、按钮输入配置详解

Codesys 按钮写变量的标准做法是"输入配置"（Input configuration）。

### 8.1 瞬时按钮（推荐）

```
OnMouseDown:  GVL.iStart := TRUE;
OnMouseUp:    GVL.iStart := FALSE;
```

效果：按住=TRUE，松开=FALSE，模拟真实的自复位按钮。

### 8.2 四种写值按钮对照

| 按钮 | OnMouseDown | OnMouseUp | 说明 |
|------|-------------|-----------|------|
| 启动 | GVL.iStart := TRUE | GVL.iStart := FALSE | 启动脉冲，程序自锁 |
| 停止 | GVL.iStop := TRUE | GVL.iStop := FALSE | 停止脉冲 |
| 报警复位 | GVL.bAlarmReset := TRUE | GVL.bAlarmReset := FALSE | R_TRIG 上升沿 |
| 计数复位 | GVL.bCntReset := TRUE | GVL.bCntReset := FALSE | R_TRIG 上升沿 |

### 8.3 页面跳转按钮

不是写变量，而是切换显示页面：

1. 选中按钮 → 属性 → 输入配置。
2. 动作类型选 "Change displayed visualization"（切换显示的可视化）。
3. 目标选要跳转的页面（如 VisuMonitor）。

## 九、WebVisu 测试流程

### 9.1 启动仿真器

1. 开始菜单 → CODESYS Control Win SysTray（系统托盘出现 C64 图标）。
2. 回到 CODESYS，F11 编译（0 error）。
3. Alt+F8 登录（选 CODESYS Control Win V3 x64，通信填 localhost）。
4. 下载"是" → F5 运行。

### 9.2 浏览器打开 HMI

1. 打开浏览器（Edge/Chrome 均可）。
2. 地址栏输入：`http://localhost:8080/webvisu.htm`
3. 回车，应看到 VisuMain 主控页。

如果 8080 打不开，检查仿真器是否在运行、可视化管理器是否勾选 WebVisu。

### 9.3 功能测试清单（逐条验收）

| # | 操作 | 预期结果 |
|---|------|----------|
| 1 | 点"启动"按钮 | 运行灯变绿，传送带变绿（运行） |
| 2 | 切到监控页，看颜色代码 | 显示 0（初始未识别） |
| 3 | 回主控页，点"停止" | 运行灯灭，传送带变灰（停止） |
| 4 | 在监控页点"计数复位" | 四个计数归零（若已有计数） |
| 5 | 切到报警页 | 报警灯正常时灭、文字隐藏 |
| 6 | （联调）触发未识别后 | 报警灯红、文字出现；点复位后清除 |

> **注意：HMI 按钮直接写 GVL.iStart 在仿真器中可跑（%I 无硬件驱动，可写）。真实接 PLC 硬件时，需加 hmiStart/hmiStop 中间变量分离（见第十章）。**

## 十、常见问题与注意事项

### 10.1 中文显示乱码

可视化管理器里必须勾选 "Use unicode strings"，否则中文乱码或方框。

### 10.2 按钮写不进去 / 写无效

- 仿真阶段：%I 输入变量无硬件驱动，按钮可写，一般能跑。
- 真实硬件：物理输入 %IX 由硬件刷新，HMI 写不进去，需要中间变量。

### 10.3 真实系统的 hmiStart/hmiStop 分离（预留）

接真机时，物理按钮和 HMI 按钮要分开：

```
GVL 增加：
  hmiStart : BOOL;   // HMI 启动按钮
  hmiStop  : BOOL;   // HMI 停止按钮

PLC_PRG 里合并：
  fbBelt.iStart := GVL.iStart OR GVL.hmiStart;
  fbBelt.iStop  := GVL.iStop  OR GVL.hmiStop;
```

当前仿真阶段暂不实现，等接真机时再加。

### 10.4 变量绑定语法

- 必须带 GVL. 前缀（qualified_only 强制），如 GVL.iStart、GVL.wCountRed。
- 写错变量名会编译报错，双击错误可跳转定位。

### 10.5 页面跳转失效

- 确认按钮的输入配置选的是 "Change displayed visualization" 而非写变量。
- 确认目标页面名拼写正确（区分大小写）。

### 10.6 计数显示不更新

- 确认文本框用了 "文本变量"（Text variables），不是直接填死的数字。
- 确认仿真器已 F5 运行（不是停在断点）。

---

相关文档：《thesis代码.md》（GVL/程序结构）、《thesis调试文档.md》（仿真/强制变量流程）、《thesis需求文档.md》（HMI 界面需求）。
