# 传送带分拣控制系统 — HMI 调试文档

| 项目 | 内容 |
|------|------|
| 环境 | CODESYS V3.5 SP22 Patch 3 |
| 仿真器 | CODESYS Control Win V3 x64 |
| HMI 类型 | WebVisu（浏览器可视化） |
| 页面 | VisuMain（主控）/ VisuMonitor（监控）/ VisuAlarm（报警） |
| 访问地址 | http://localhost:8080/webvisu.htm |
| 文档版本 | v1.1（2026-08-25） |

## 一、调试前准备

### 1.1 前提确认

- 三个页面（VisuMain / VisuMonitor / VisuAlarm）已创建并画好控件。
- 可视化管理器（Visualization Manager）已添加，且勾选了 "Use unicode strings"（中文支持）。
- WebVisu 起始页面已设为 VisuMain。
- GVL 变量齐全（15 个变量，见《HMI 制作指示文档》第三章映射总表）。

### 1.2 变量绑定总表（调试对照用）

| 变量 | 类型 | 控件绑定 | 期望行为 |
|------|------|----------|----------|
| GVL.iStart | BOOL | 启动按钮 OnMouseDown/Up | 点击→运行灯亮、皮带变色 |
| GVL.iStop | BOOL | 停止按钮 OnMouseDown/Up | 点击→运行灯灭、皮带变色 |
| GVL.qRunLight | BOOL | 运行灯 颜色变量 | TRUE=绿，FALSE=灰 |
| GVL.qAlarmLight | BOOL | 报警灯 颜色变量 | TRUE=红，FALSE=灰 |
| GVL.qBelt | BOOL | 皮带 颜色变量 | TRUE=绿（运行），FALSE=灰 |
| GVL.qPushA/B/C | BOOL | 推杆灯 颜色变量 | TRUE=绿（伸出），FALSE=灰 |
| GVL.iDetect | BOOL | 箱子 状态变量→Invisible | 绑 NOT GVL.iDetect，有件显示 |
| GVL.iColorCode | INT | 颜色代码 文本框 %s | 显示 0/1/2/3 |
| GVL.wCountRed/Blue/Green/Total | INT | 计数 文本框 %s | 实时显示数字 |
| GVL.bAlarmReset | BOOL | 报警复位按钮 | 点击→报警灯灭 |
| GVL.bCntReset | BOOL | 计数复位按钮 | 点击→四个计数归零 |

## 二、标准调试流程（口诀）

```
F11编译 → 启动仿真器 → Alt+F8登录 → 下载"是" → F5运行 → 浏览器开 8080
```

### 2.1 编译

1. 按 F11（生成代码，比 F7 彻底）。
2. 看消息窗口：0 error = 通过；有 C0xxx 错误双击跳转定位。

### 2.2 启动仿真器

1. 开始菜单 → CODESYS Control Win SysTray。
2. 系统托盘出现 C64 图标 = 仿真器已启动。
3. 没图标就先启动，否则登录扫不到设备。

### 2.3 登录与下载

1. Alt+F8 登录。
2. 弹窗"活动路径选择设备" → 选 CODESYS Control Win V3 x64。
3. 弹窗"扫描本机设备" → 点"是"，通信填 localhost。
4. 提示"程序与设备不一致" → 点"是"下载。
5. F5 运行。

### 2.4 浏览器打开 HMI

1. 打开 Edge / Chrome。
2. 地址栏输入 http://localhost:8080/webvisu.htm，回车。
3. 应看到 VisuMain 主控页。

> ⚠ 8080 打不开？检查：① 仿真器是否在运行（托盘 C64 图标）② 可视化管理器是否勾选 WebVisu ③ 是否已 F5 运行。

## 三、三页面功能测试清单

### 3.1 主控页 VisuMain

| # | 操作 | 预期结果 | 判定 |
|---|------|----------|------|
| 1 | 点"启动"按钮 | 运行灯变绿，皮带变绿 | □ 通过 |
| 2 | 松开"启动"按钮 | 运行灯/皮带保持绿（自锁生效） | □ 通过 |
| 3 | 点"停止"按钮 | 运行灯灭，皮带变灰 | □ 通过 |
| 4 | 点"分拣监控页"按钮 | 整页切换到监控页 | □ 通过 |
| 5 | 点"报警页"按钮 | 整页切换到报警页 | □ 通过 |

### 3.2 监控页 VisuMonitor

| # | 操作 | 预期结果 | 判定 |
|---|------|----------|------|
| 1 | 看颜色代码文本框 | 显示 0（初始） | □ 通过 |
| 2 | 看四个计数文本框 | 显示 0 | □ 通过 |
| 3 | 看推杆A/B/C状态灯 | 灰色（回位） | □ 通过 |
| 4 | 点"计数复位"按钮 | 计数仍 0（正常，无计数可清） | □ 通过 |
| 5 | 点"返回主控页"按钮 | 整页切回主控页 | □ 通过 |

### 3.3 报警页 VisuAlarm

| # | 操作 | 预期结果 | 判定 |
|---|------|----------|------|
| 1 | 看报警灯 | 正常时灭/灰 | □ 通过 |
| 2 | 看报警文字提示 | 隐藏（无报警） | □ 通过 |
| 3 | 点"报警复位"按钮 | 无变化（正常） | □ 通过 |
| 4 | 点"返回主控页"按钮 | 整页切回主控页 | □ 通过 |

## 四、监视列表最小配置（只填 HMI 控制不了的变量）

**原则：HMI 页面上能点的按钮，就不要放监视列表，直接在页面上点即可。监视列表只填 HMI 点不到的传感器信号。**

### 4.1 不用放监视列表（在 HMI 上点按钮即可）

这 4 个变量 HMI 上有对应按钮，调试时直接点页面按钮，无需切到监视列表。

| 变量 | 在哪里点 | 作用 |
|------|----------|------|
| GVL.iStart | 主控页"启动"按钮 | 启动传送带 |
| GVL.iStop | 主控页"停止"按钮 | 停止传送带 |
| GVL.bAlarmReset | 报警页"报警复位"按钮 | 清除报警 |
| GVL.bCntReset | 监控页"计数复位"按钮 | 清零计数 |

### 4.2 必填（HMI 点不到，需在监视列表强制，共 2 个）

这是两个传感器信号，HMI 上没有输入口，只能靠监视列表强制模拟。

| 变量 | 类型 | 强制什么值 | 模拟什么 |
|------|------|-----------|----------|
| GVL.iDetect | BOOL | TRUE / FALSE | 物体到位 / 离开 |
| GVL.iColorCode | INT | 0 / 1 / 2 / 3 | 颜色：0未识别 1红 2蓝 3绿 |

### 4.3 选填（只观察，别强制）

这些是程序算出来的输出，监视列表里敲进去只为"看"，别改值（强制了会被程序覆盖，还掩盖真实逻辑）。

```
GVL.qBelt        → 皮带
GVL.qRunLight    → 运行灯
GVL.qAlarmLight  → 报警灯
GVL.qPushA / qPushB / qPushC   → 推杆
GVL.wCountRed / wCountBlue / wCountGreen / wCountTotal   → 计数
```

### 4.4 怎么在监视列表里改值

1. 监视列表（默认标签"监视1"）的"表达式"栏，敲变量名回车，如 GVL.iColorCode。
2. 在"准备值"（Prepared value）列双击，输入新值（BOOL 可双击切换 TRUE/FALSE，INT 直接输数字）。
3. 按 Ctrl+F8 强制（持续锁住，程序覆盖不掉）。

> ⚠ 只改"准备值"不按 Ctrl+F8 没用；对传感器信号用"强制"而非"写入"（Ctrl+F7），否则下一周期会被读回。

## 五、模拟分拣全流程（端到端联调）

把 PLC 逻辑 + HMI 显示串起来跑一遍，是验收核心。

### 5.1 操作顺序（HMI 点按钮 + 监视列表强制传感器）

```
1) HMI 主控页点"启动"          → 皮带变绿（运行）
2) 监视列表强制 iColorCode := 1  → 先设颜色=红色
3) 监视列表强制 iDetect := TRUE  → 触发到位，分拣开始
   （关键！先设颜色，再触发到位，顺序不能反）
```

### 5.2 端到端观察点（对照 HMI）

| 步骤 | PLC 侧动作 | HMI 侧应看到 |
|------|-----------|--------------|
| 点启动 | iStart=TRUE，qBelt=TRUE，qRunLight=TRUE | 主控页：运行灯绿、皮带绿 |
| 设颜色=1 | iColorCode=1 | 监控页：颜色代码显示 1 |
| 触发到位 | iDetect=TRUE，bPause=TRUE，qBelt 停，qPushA 伸出 | 皮带变灰（暂停），推杆A变绿（伸出） |
| 等2秒回位 | qPushA 回 FALSE，bPause=FALSE，qBelt 恢复 | 推杆A变灰，皮带恢复绿 |
| 看计数 | wCountRed=1，wCountTotal=1 | 监控页：红色计数=1，总计数=1 |

### 5.3 报警流程（测试报警页）

1. 监视列表强制 iColorCode := 0（未识别）。
2. 强制 iDetect := TRUE。
3. 观察：qAlarmLight=TRUE，传送带锁停。
4. HMI 报警页：报警灯变红，文字提示出现。
5. 点报警页"报警复位"按钮。
6. 观察：报警灯灭，文字隐藏，恢复运行。

### 5.4 计数复位流程

1. 确认监控页计数已非 0（前面跑过分拣）。
2. 点监控页"计数复位"按钮。
3. 观察：四个计数归零。

## 六、一键重置（跑乱了怎么清）

仿真器进程一直跑，上次变量值/强制值残留。测试前先清干净：

```
口诀：解除强制 → 冷复位 → 重新下载 → F5运行
```

1. 在线 → 强制值 → 解除所有强制。
2. 在线 → 复位 → 冷复位（Cold Reset），清空所有变量。
3. 重新下载 + F5 运行。
4. 更彻底：托盘 C64 图标右键 → 退出，重启仿真器 → 登录 → 下载。

## 七、常见问题排查（FAQ）

| 症状 | 原因 | 解决 |
|------|------|------|
| 浏览器 8080 打不开 | 仿真器没跑 / 没勾 WebVisu / 没运行 | 启动仿真器→勾 WebVisu→F5 运行 |
| 中文乱码/方框 | 可视化管理器没勾 unicode strings | 管理器属性勾选后重新下载 |
| 按钮点了没反应 | ① 没 F5 运行 ② 输入配置没设对 | 确认运行 + 检查 OnMouseDown/Up 配置 |
| 文本框显示写死的字 | Text 静态文本没放 %s 占位符 | Text 改成 %s 或 "标签：%s" |
| 计数不更新 | 文本框没绑"文本变量" | 用文本变量绑 GVL.wCountXxx |
| 箱子始终显示/始终隐藏 | Invisible 没加 NOT | 绑 NOT GVL.iDetect |
| 箱子抽一下不动 | 用了 Relative movement 绑 qBelt | 改 Absolute movement + 计数器（或去掉移动） |
| 跳转按钮变画中画 | 从工具箱拖了页面（Frame） | 改用 Button + Change displayed visualization |
| 报警文字该显没显 | 绑了 qRunLight 而非 qAlarmLight | 绑 NOT GVL.qAlarmLight |
| 变量写不进 | 真实硬件 %IX 由硬件刷新 | 仿真可写；真机需 hmiStart/hmiStop 中间变量 |

## 八、调试记录坑点（血泪总结）

### 8.1 Relative vs Absolute movement（概念）

**Relative movement 是"变量值变化一次 → 跳一格"，绑 BOOL 只会抽一下，不会持续滚动。**

想要持续滚动：Absolute movement + 递增计数器（GVL 加 wBeltAnim:INT，PLC_PRG 每周期 +1）。

但注意：本项目是"暂停分拣"，分拣时传送带停，工件本不该移动。滚动动画纯属视觉特效，非真实逻辑。

### 8.2 Invisible 加 NOT（方向）

**Invisible 语义 = TRUE 时隐藏；iDetect 语义 = TRUE 时有件，方向相反，必须绑 NOT GVL.iDetect。**

### 8.3 Frame ≠ 跳转按钮

**从工具箱"当前工程"拖页面到画布 = Frame 嵌入（画中画常驻）；点按钮切整页 = Button + Change displayed visualization。做跳转走后者。**

### 8.4 监视列表 ≠ HMI 页面

监视列表（监视1）是程序员调试后视镜，表达式栏敲变量名看值；HMI 页面是给用户看的前挡风玻璃，用文本框绑文本变量。别混。

### 8.5 文本框要放 %s 占位符

Text 静态文本 = 模板，%s = 挖的洞，文本变量 = 填进洞的值。不放 %s，变量值无处安放，永远显示写死的字。

### 8.6 报警文字绑 qAlarmLight 而非 qRunLight

报警文字提示跟报警灯走（NOT GVL.qAlarmLight）。报警时运行灯可能还亮着（只锁停传送带、没清 bRunning），绑 qRunLight 会藏反。

### 8.7 传送带没有现成控件

工具箱只有基础图形（矩形/椭圆/线/多边形）+ 常用控件（按钮/灯/文本框）。工业设备图自己拼矩形，或用 Image 导入图片。

## 九、GitHub 展示 HMI 的方案（附）

关于"怎么让别人不用打开项目就能看到 HMI"，核心结论：

- CODESYS WebVisu 不是可独立托管的静态网页，必须靠 CODESYS 运行时（仿真器/PLC）在后台提供变量服务，浏览器只是前端。
- 因此访客没有 CODESYS 环境时，无法"打开网页就交互操作真 HMI"。
- 标准做法：截图（三页 PNG）+ 录屏（GIF），放 GitHub，README 引用。

### 9.1 截图放 GitHub（必做，最低成本）

1. 浏览器打开 http://localhost:8080/webvisu.htm，跑起来。
2. Win + Shift + S 截取三个页面，分别存 PNG。
3. 上传到仓库（如 docs/hmi/ 目录）。
4. README 里用 Markdown 图片语法引用。

### 9.2 录屏 GIF（加分，展示动态）

1. 录一段 15-30 秒操作：点启动 → 皮带变绿 → 触发分拣 → 计数 +1。
2. 转成 GIF（ScreenToGif 等免费工具）。
3. 放 GitHub，README 引用，访客能看到动画效果。

### 9.3 HTML 模拟演示页（可选，重工）

手写 HTML+CSS+JS 仿真页面，能点能动画，可放 GitHub Pages 让访客交互。但这是"演示"，不是真 HMI，逻辑是手写模拟的。

**结论：GitHub 展示工业 HMI 的通行做法 = 截图 + 录屏，无"不装环境就在线交互跑真 HMI"的免费方案。**

---

相关文档：《HMI 制作指示文档》（变量映射/三页制作步骤）、《thesis代码.md》（GVL/程序结构）、《thesis调试文档.md》（仿真/强制变量流程）。
