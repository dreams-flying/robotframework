# Windows 桌面自动化录制工具大全
## 类似 Playwright Codegen 的开源项目

---

## 🎯 概述

本文档列出了支持 **Windows 桌面应用自动化** 并具有 **录制和代码生成功能** 的开源工具，类似 Playwright Codegen 的体验。

---

## 🏆 推荐工具（按类型分类）

### 类型 1：基于 UI 元素识别（推荐）⭐⭐⭐⭐⭐

#### 1. **WinAppDriver + UI Recorder**（微软官方）

**★★★★★ 最推荐用于 Windows 桌面应用**

- **开发者**: Microsoft
- **GitHub**: https://github.com/microsoft/WinAppDriver
- **协议**: MIT License（开源）
- **支持平台**: Windows 10+
- **编程语言**: C#, Python, Java, JavaScript

**特点：**
- ✅ 微软官方支持
- ✅ 基于 Appium 协议（WebDriver 标准）
- ✅ **内置 UI Recorder**（类似 Codegen）
- ✅ 支持 UWP、WPF、Win32 应用
- ✅ 可生成 C# 代码
- ✅ 元素检查器（Inspect.exe）
- ✅ XPath 自动生成

**录制功能：**
```
WinAppDriver UI Recorder 可以：
1. 录制鼠标点击、键盘输入
2. 自动生成 XPath 定位器
3. 实时生成 C# 测试代码
4. 可视化元素属性查看
```

**安装：**
```bash
# 1. 下载 WinAppDriver
https://github.com/microsoft/WinAppDriver/releases

# 2. 下载 UI Recorder
https://github.com/microsoft/WinAppDriver/releases
# 查找 WinAppDriver.UIRecorder.zip

# 3. 安装 Python 客户端（可选）
pip install Appium-Python-Client
```

**示例代码（自动生成）：**
```csharp
// UI Recorder 自动生成的代码
var appCapabilities = new AppiumOptions();
appCapabilities.AddAdditionalCapability("app", "Microsoft.WindowsCalculator_8wekyb3d8bbwe!App");

var session = new WindowsDriver<WindowsElement>(new Uri("http://127.0.0.1:4723"), appCapabilities);
session.FindElementByAccessibilityId("num8Button").Click();
session.FindElementByAccessibilityId("plusButton").Click();
session.FindElementByAccessibilityId("num2Button").Click();
session.FindElementByAccessibilityId("equalButton").Click();
```

**优点：**
- ✅ 官方支持，稳定可靠
- ✅ 录制功能强大
- ✅ 社区活跃
- ✅ 文档齐全

**缺点：**
- ❌ 主要生成 C# 代码（Python 需要手动转换）
- ❌ 需要在开发者模式下运行
- ❌ 对某些老旧 Win32 应用支持有限

**使用教程：**
1. 启动 WinAppDriver.exe
2. 运行 WinAppDriver UI Recorder
3. 点击 "Record" 开始录制
4. 操作目标应用
5. 点击 "Generate Code" 生成 C# 代码

---

#### 2. **Pywinauto + Swapy**（Python 生态）

**★★★★☆ Python 开发者首选**

- **GitHub**: https://github.com/pywinauto/pywinauto
- **Swapy**: https://github.com/pywinauto/SWAPY
- **协议**: BSD License（开源）
- **编程语言**: Python

**特点：**
- ✅ 纯 Python 实现
- ✅ **Swapy 可视化录制器**
- ✅ 支持 Win32、.NET、WPF、Qt 应用
- ✅ 自动生成 Python 代码
- ✅ 元素检查和代码生成
- ✅ 活跃维护

**录制功能（Swapy）：**
```
Swapy 是 Pywinauto 的可视化工具：
1. 拖拽选择 UI 元素
2. 查看元素属性和层次结构
3. 自动生成 Pywinauto 代码
4. 支持代码片段复制
```

**安装：**
```bash
pip install pywinauto
pip install pillow  # 用于图像识别

# 下载 Swapy（可视化工具）
# https://github.com/pywinauto/SWAPY/releases
```

**示例代码（Swapy 生成）：**
```python
# Swapy 自动生成的代码
from pywinauto import Application

app = Application().start("notepad.exe")
app.Notepad.menu_select("File -> Open")
app.Open.Edit.set_text("test.txt")
app.Open.Button.click()
```

**优点：**
- ✅ Python 原生支持
- ✅ Swapy 可视化工具直观
- ✅ 文档详细
- ✅ 社区支持好

**缺点：**
- ❌ Swapy 更新较慢
- ❌ 对 UWP 应用支持有限
- ❌ 录制功能不如 WinAppDriver 强大

---

### 类型 2：基于图像识别（跨平台）⭐⭐⭐⭐

#### 3. **UI.Vision RPA**（开源 RPA）

**★★★★★ 最佳跨平台选择**

- **官网**: https://ui.vision/
- **GitHub**: https://github.com/A9T9/RPA
- **协议**: AGPLv3（开源）
- **支持平台**: Windows, macOS, Linux

**特点：**
- ✅ **完整的录制和回放功能**
- ✅ 图像识别 + OCR 文本识别
- ✅ 桌面 + 浏览器自动化
- ✅ 可视化编辑器
- ✅ 生成可执行脚本
- ✅ 免费且开源
- ✅ 活跃维护（2024/2025）

**录制功能：**
```
UI.Vision 提供：
1. 录制鼠标和键盘操作
2. 自动截图生成图像定位器
3. OCR 文本识别
4. 可视化脚本编辑
5. 导出为 JSON 格式
```

**安装：**
```bash
# 方式 1：浏览器扩展（推荐）
# Chrome/Edge/Firefox 商店搜索 "UI.Vision RPA"

# 方式 2：桌面版
# 下载地址：https://ui.vision/rpa/x/download
```

**示例脚本（自动生成）：**
```json
{
  "Name": "AutomateCalculator",
  "Commands": [
    {
      "Command": "click",
      "Target": "calculator_button.png",
      "Value": ""
    },
    {
      "Command": "XClick",
      "Target": "100,200",
      "Value": ""
    },
    {
      "Command": "OCRClick",
      "Target": "Calculate",
      "Value": ""
    }
  ]
}
```

**优点：**
- ✅ 跨平台（Windows/Mac/Linux）
- ✅ 录制功能强大
- ✅ 图像识别 + 坐标 + OCR 三种方式
- ✅ 免费且活跃维护
- ✅ 适合桌面和 Web 混合自动化

**缺点：**
- ❌ 基于图像识别，可能不如元素识别精确
- ❌ 脚本格式是 JSON，不是传统编程语言
- ❌ 图像变化时需要更新截图

---

#### 4. **SikuliX**（图像识别经典）

**★★★★☆ 经典的图像识别工具**

- **官网**: http://sikulix.com/
- **GitHub**: https://github.com/RaiMan/SikuliX1
- **协议**: MIT License（开源）
- **编程语言**: Python, Java, Ruby

**特点：**
- ✅ 强大的图像识别（OpenCV）
- ✅ 支持多种编程语言
- ✅ **内置 IDE 和录制器**
- ✅ OCR 文本识别（Tesseract）
- ✅ 跨平台

**录制功能：**
```
SikuliX IDE 提供：
1. 截图工具（Ctrl+Shift+2）
2. 代码自动补全
3. 图像管理
4. 脚本录制（部分支持）
```

**安装：**
```bash
# 下载 SikuliX JAR
https://raiman.github.io/SikuliX1/downloads.html

# 运行（需要 Java）
java -jar sikulix.jar
```

**示例代码：**
```python
# SikuliX Python 脚本
click("calculator_icon.png")
wait(1)
click("button_8.png")
click("button_plus.png")
click("button_2.png")
click("button_equals.png")

# OCR 文本识别
text = Screen().text()
print(text)
```

**优点：**
- ✅ 图像识别非常强大
- ✅ 支持多种语言
- ✅ 跨平台
- ✅ 久经考验

**缺点：**
- ❌ 需要 Java 环境
- ❌ 录制功能不如专业工具
- ❌ 维护更新较慢
- ❌ 基于图像，稳定性一般

---

### 类型 3：宏录制器（简单快速）⭐⭐⭐

#### 5. **Pulover's Macro Creator**（AutoHotkey）

**★★★★☆ 最易用的宏录制器**

- **官网**: https://www.macrocreator.com/
- **GitHub**: https://github.com/Pulover/PuloversMacroCreator
- **协议**: GPL v2（开源）
- **基于**: AutoHotkey

**特点：**
- ✅ **完整的录制和回放功能**
- ✅ 可视化编辑器
- ✅ 生成 AutoHotkey 脚本
- ✅ 支持键盘、鼠标、窗口操作
- ✅ 易于使用，无需编程知识
- ✅ 免费开源

**录制功能：**
```
Pulover's Macro Creator 可以：
1. 录制所有鼠标和键盘操作
2. 可视化编辑录制的步骤
3. 导出为 .exe 可执行文件
4. 导出为 AutoHotkey 脚本
5. 支持图像识别（可选）
```

**安装：**
```bash
# 下载安装包
https://www.macrocreator.com/download/

# 或使用 Chocolatey
choco install pulover-macro-creator
```

**生成的代码（AutoHotkey）：**
```ahk
; Pulover's Macro Creator 生成的脚本
WinActivate, Calculator
Sleep, 500
Click, 100, 200
SendInput, 8{+}2{=}
```

**优点：**
- ✅ 最易用，零门槛
- ✅ 可视化编辑器直观
- ✅ 可导出独立 .exe
- ✅ 免费开源

**缺点：**
- ❌ 基于坐标和图像，不如元素识别精确
- ❌ 只支持 Windows
- ❌ 对复杂应用支持有限

---

#### 6. **AutoHotkey**（脚本语言）

**★★★★☆ 最强大的 Windows 自动化脚本**

- **官网**: https://www.autohotkey.com/
- **GitHub**: https://github.com/AutoHotkey/AutoHotkey
- **协议**: GPL v2（开源）

**特点：**
- ✅ 强大的脚本语言
- ✅ 完全免费开源
- ✅ 社区庞大
- ✅ 支持热键、宏、GUI 自动化
- ✅ 可编译为 .exe

**录制功能：**
```
AutoHotkey 本身没有录制器，但可以配合：
1. Pulover's Macro Creator（推荐）
2. AutoScriptWriter（第三方）
3. MacroRecorder（第三方）
```

**安装：**
```bash
# 下载安装
https://www.autohotkey.com/download/

# 或使用 Chocolatey
choco install autohotkey
```

**示例代码：**
```ahk
; AutoHotkey 脚本
#SingleInstance Force

; Win+C 启动计算器
#c::
Run, calc.exe
WinWait, Calculator
Sleep, 1000
Send, 8{+}2{=}
return
```

**优点：**
- ✅ 功能强大，灵活性高
- ✅ 社区资源丰富
- ✅ 完全免费
- ✅ 可编译为独立程序

**缺点：**
- ❌ 需要学习脚本语言
- ❌ 没有内置录制器
- ❌ 基于坐标和热键

---

### 类型 4：Python RPA 框架⭐⭐⭐⭐

#### 7. **TagUI（RPA for Python）**

**★★★★☆ 开源 RPA 框架**

- **GitHub**: https://github.com/aisingapore/TagUI
- **Python 包**: https://github.com/tebelorg/rpa-python
- **协议**: Apache 2.0（开源）

**特点：**
- ✅ 命令行 RPA 工具
- ✅ 集成 SikuliX（图像识别）
- ✅ 支持桌面和 Web 自动化
- ✅ Python 和 JavaScript 接口
- ✅ OCR 文本识别

**录制功能：**
```
TagUI 提供：
1. 录制浏览器操作（Chrome 扩展）
2. 图像识别（通过 SikuliX）
3. 自然语言脚本
```

**安装：**
```bash
# Python 包
pip install rpa

# 或命令行版本
https://github.com/aisingapore/TagUI
```

**示例代码：**
```python
# TagUI Python
import rpa as r

r.init()
r.run('notepad')
r.wait(2)
r.keyboard('Hello World')
r.close()
```

**优点：**
- ✅ 简单易用
- ✅ Python 友好
- ✅ 支持图像和文本识别
- ✅ 开源免费

**缺点：**
- ❌ 录制功能有限
- ❌ 主要面向 Web 自动化
- ❌ 文档不够详细

---

#### 8. **Repeat**（跨平台宏工具）

**★★★☆☆ 程序员友好的宏工具**

- **GitHub**: https://github.com/repeats/Repeat
- **协议**: Apache 2.0（开源）
- **支持平台**: Windows, macOS, Linux

**特点：**
- ✅ **录制和回放功能**
- ✅ 支持 Python、Java、C# 脚本
- ✅ 跨平台
- ✅ 图形界面

**录制功能：**
```
Repeat 提供：
1. 录制鼠标和键盘操作
2. 支持多种编程语言编辑
3. 热键触发
4. 任务调度
```

**安装：**
```bash
# 下载
https://github.com/repeats/Repeat/releases
```

**优点：**
- ✅ 跨平台
- ✅ 支持真正的编程语言
- ✅ 开源免费

**缺点：**
- ❌ 界面较老旧
- ❌ 社区不够活跃
- ❌ 文档有限

---

## 📊 工具对比表

| 工具 | 录制功能 | 代码生成 | 元素识别 | 图像识别 | 易用性 | 推荐度 |
|------|---------|---------|---------|---------|-------|-------|
| **WinAppDriver + UI Recorder** | ✅✅✅ | C# | ✅ | ❌ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Pywinauto + Swapy** | ✅✅ | Python | ✅ | ❌ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **UI.Vision RPA** | ✅✅✅ | JSON | ❌ | ✅ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **SikuliX** | ✅✅ | Python/Java | ❌ | ✅ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Pulover's Macro Creator** | ✅✅✅ | AHK | ❌ | ✅ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **AutoHotkey** | ❌ | AHK | ❌ | ❌ | ⭐⭐⭐ | ⭐⭐⭐ |
| **TagUI** | ✅ | Python | ❌ | ✅ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Repeat** | ✅✅ | 多语言 | ❌ | ❌ | ⭐⭐⭐ | ⭐⭐⭐ |

---

## 🎯 选择建议

### 根据您的需求选择：

#### 1. **专业 Windows 应用自动化**
👉 **WinAppDriver + UI Recorder**
- 适合：企业级 Windows 应用测试
- 优点：微软官方，最稳定
- 缺点：需要 C# 知识

#### 2. **Python 开发者**
👉 **Pywinauto + Swapy**
- 适合：Python 项目集成
- 优点：纯 Python，易集成
- 缺点：Swapy 更新较慢

#### 3. **跨平台 + 易用性**
👉 **UI.Vision RPA**
- 适合：快速自动化任务
- 优点：最易用，录制功能强
- 缺点：基于图像，不够精确

#### 4. **简单宏录制**
👉 **Pulover's Macro Creator**
- 适合：零编程基础用户
- 优点：超级简单
- 缺点：功能有限

#### 5. **复杂自动化脚本**
👉 **AutoHotkey**
- 适合：有编程经验的高级用户
- 优点：功能最强大
- 缺点：需要学习脚本语言

---

## 🚀 快速开始示例

### WinAppDriver + UI Recorder 完整教程

#### 步骤 1：安装 WinAppDriver

```bash
# 1. 下载
https://github.com/microsoft/WinAppDriver/releases

# 2. 安装 WinAppDriver.msi

# 3. 启用 Windows 开发者模式
# 设置 -> 更新和安全 -> 开发者选项 -> 开发人员模式
```

#### 步骤 2：下载 UI Recorder

```bash
# 下载 WinAppDriver.UIRecorder.zip
https://github.com/microsoft/WinAppDriver/releases

# 解压并运行 WinAppDriverUIRecorder.exe
```

#### 步骤 3：录制操作

```
1. 启动 WinAppDriver.exe（双击运行）
2. 启动 WinAppDriverUIRecorder.exe
3. 点击 "Record" 按钮
4. 操作目标应用（如计算器）
5. 点击 "Stop" 停止录制
6. 点击 "Generate C# Code" 生成代码
```

#### 步骤 4：使用生成的代码

```csharp
// 自动生成的 C# 代码
using OpenQA.Selenium.Appium.Windows;
using OpenQA.Selenium.Remote;

// ...

var appCapabilities = new DesiredCapabilities();
appCapabilities.SetCapability("app", "Microsoft.WindowsCalculator_8wekyb3d8bbwe!App");

var session = new WindowsDriver<WindowsElement>(
    new Uri("http://127.0.0.1:4723"),
    appCapabilities
);

// 录制的操作
session.FindElementByAccessibilityId("num8Button").Click();
session.FindElementByAccessibilityId("plusButton").Click();
session.FindElementByAccessibilityId("num2Button").Click();
session.FindElementByAccessibilityId("equalButton").Click();
```

#### 步骤 5：Python 版本（手动转换）

```python
from appium import webdriver

capabilities = {
    "app": "Microsoft.WindowsCalculator_8wekyb3d8bbwe!App"
}

driver = webdriver.Remote(
    command_executor='http://127.0.0.1:4723',
    desired_capabilities=capabilities
)

# 执行操作
driver.find_element_by_accessibility_id("num8Button").click()
driver.find_element_by_accessibility_id("plusButton").click()
driver.find_element_by_accessibility_id("num2Button").click()
driver.find_element_by_accessibility_id("equalButton").click()

driver.quit()
```

---

## 📚 资源链接

### 官方文档
- [WinAppDriver 文档](https://github.com/microsoft/WinAppDriver)
- [Pywinauto 文档](https://pywinauto.readthedocs.io/)
- [UI.Vision 文档](https://ui.vision/rpa/docs)
- [SikuliX 文档](http://sikulix-2014.readthedocs.io/)
- [AutoHotkey 文档](https://www.autohotkey.com/docs/)

### 视频教程
- [WinAppDriver 入门](https://www.youtube.com/results?search_query=winappdriver+tutorial)
- [UI.Vision RPA 教程](https://www.youtube.com/results?search_query=ui.vision+rpa)

### 社区
- [WinAppDriver Issues](https://github.com/microsoft/WinAppDriver/issues)
- [Pywinauto Google Group](https://groups.google.com/g/pywinauto)
- [UI.Vision Forum](https://forum.ui.vision/)

---

## ✅ 总结

### 最佳选择（综合推荐）：

1. **专业用途** → **WinAppDriver + UI Recorder**
   - 微软官方，最可靠
   - 录制功能完善
   - 适合企业应用

2. **Python 项目** → **Pywinauto + Swapy**
   - Python 原生支持
   - 易于集成
   - 代码简洁

3. **快速上手** → **UI.Vision RPA**
   - 零门槛
   - 录制功能强大
   - 跨平台

4. **简单任务** → **Pulover's Macro Creator**
   - 超级简单
   - 可视化编辑
   - 适合非程序员

所有这些工具都是 **开源且免费** 的，您可以根据具体需求选择最合适的工具！
