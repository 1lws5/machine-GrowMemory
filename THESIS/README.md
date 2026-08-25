# 传送带分拣控制系统（Conveyor Sorting System）

基于 **CODESYS V3.5 SP22 Patch 3** + **CODESYS Control Win V3 x64 仿真器** 的 PLC 毕业设计项目，ST（结构化文本）语言实现，纯仿真验证（无真实硬件）。

## 项目概述

传送带运送物体经过颜色传感器，识别颜色（1=红 / 2=蓝 / 3=绿 / 0=未识别）后，用 3 个气缸推杆把物体推到对应轨道，未识别物体触发报警。

## 系统架构

| 组件 | 说明 |
|------|------|
| 主控 | PLC_PRG（启保停 + 编排） |
| 传送带控制 | FB_BeltControl（运行/暂停/自锁） |
| 推杆控制 | FB_Pusher（CASE 状态机：待机→伸出2秒→回位1秒），实例化 3 个 |
| 分拣逻辑 | FB_Sorter（颜色判定 + 推杆触发 + 报警锁存 + 计数） |
| 全局变量 | GVL（I/O 绑定 + 计数 + 复位信号） |
| HMI | WebVisu 三页面（主控 / 分拣监控 / 报警） |

## 目录结构

```
THESIS/
├── thesis.project          # CODESYS 工程文件（权威，含 HMI）
├── thesis代码.md            # GVL/程序结构（与工程一致）
├── thesis需求文档.md        # 需求 + 进阶版（物体跟踪/卡料超时/IO-Link 等 10 条）
├── thesis调试文档.md        # 仿真/强制变量调试流程
├── thesis框架思路.md        # 框架搭建思路
├── thesis-HMI制作指示.md    # HMI 三页面制作步骤（变量映射/动画/按钮配置）
├── thesis-HMI调试文档.md    # HMI 调试流程 + 监视列表最小配置 + FAQ 坑点
└── hmi/
    ├── visu_main.png       # 主控页截图
    ├── visu_monitor.png    # 分拣监控页截图
    ├── visu_alarm.png      # 报警页截图
    └── hmi_demo.mp4        # HMI 操作演示录屏
```

## HMI 界面预览

### 主控页（VisuMain）
![主控页](hmi/visu_main.png)

启动/停止按钮、运行灯、报警灯、传送带动画、页面跳转。

### 分拣监控页（VisuMonitor）
![分拣监控页](hmi/visu_monitor.png)

红/蓝/绿计数、总计数、当前颜色代码、推杆状态灯、计数复位。

### 报警页（VisuAlarm）
![报警页](hmi/visu_alarm.png)

报警指示灯、报警文字提示、报警复位。

### 操作演示
[▶ 观看 HMI 操作演示视频](hmi/hmi_demo.mp4)

> 💾 **一键下载全部素材（截图 + 视频打包）**：[HMI_showcase.zip](hmi/HMI_showcase.zip)
> 说明：视频文件约 35MB，超过 GitHub 网页 10MB 预览上限，网页上点开只会下载、不能在线播。建议下载 zip 到本地解压观看。

## I/O 点表

| 变量名 | 类型 | 地址 | 方向 | 说明 |
|--------|------|------|------|------|
| iStart | BOOL | %IX0.0 | 输入 | 启动按钮（常开） |
| iStop | BOOL | %IX0.1 | 输入 | 停止按钮（常闭，真实接线取反） |
| iDetect | BOOL | %IX0.2 | 输入 | 到位检测传感器 |
| iColorCode | INT | %IW2 | 输入 | 颜色代码（1红/2蓝/3绿/0未识别） |
| qBelt | BOOL | %QX0.0 | 输出 | 传送带电机 |
| qPushA | BOOL | %QX0.1 | 输出 | 推杆A（红） |
| qPushB | BOOL | %QX0.2 | 输出 | 推杆B（蓝） |
| qPushC | BOOL | %QX0.3 | 输出 | 推杆C（绿） |
| qRunLight | BOOL | %QX0.4 | 输出 | 运行指示灯 |
| qAlarmLight | BOOL | %QX0.5 | 输出 | 报警指示灯 |

## 运行方式

1. 安装 CODESYS V3.5 SP22 Patch 3 + CODESYS Control Win V3 x64。
2. 打开 `thesis.project`，启动仿真器，登录 localhost，下载运行。
3. 浏览器打开 `http://localhost:8080/webvisu.htm` 访问 HMI。
4. 传感器信号（iDetect / iColorCode）在监视列表中强制模拟。

> 详细步骤见 `thesis-HMI调试文档.md`。

## 项目状态

- ✅ 阶段一：PLC 基础指令（启保停/定时器/计数/比较/边沿检测/SET-RESET）
- ✅ 阶段二：DFB 封装 + I/O 绑定 + 12 步序交通灯
- ✅ 阶段三：Codesys 迁移 + 综合项目核心方案 + 调试 + HMI（本仓库）
- ⬜ 阶段四：Modbus TCP 通信（未开始）
- ⬜ 阶段五：电气图绘制
