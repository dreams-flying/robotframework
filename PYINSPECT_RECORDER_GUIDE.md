# PyInspect Recorder 使用指南

## 📖 简介

**PyInspect Recorder** 是一个类似 Playwright Codegen 的 Windows 桌面自动化录制工具，能够**一边操作应用程序，一边自动生成 Pywinauto 代码**。

### 🎯 核心功能

- ✅ **实时录制** - 在任意 Windows 应用上操作时自动捕获
- ✅ **自动识别元素** - 使用 UI Automation 识别点击的元素
- ✅ **智能代码生成** - 自动生成可执行的 Pywinauto 脚本
- ✅ **支持多种操作** - 点击、输入、按键
- ✅ **一键复制** - 直接复制生成的代码到剪贴板

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install pywinauto PyQt5 pynput pyperclip
```

### 2. 运行工具

```bash
python py_inspect_recorder.py
```

### 3. 基本使用流程

```
1️⃣ 点击「开始录制」按钮
     ↓
2️⃣ 切换到目标应用程序（如记事本、计算器）
     ↓
3️⃣ 进行操作（点击、输入）
     ↓
4️⃣ 回到 Recorder 窗口，点击「停止录制」
     ↓
5️⃣ 查看生成的代码，点击「复制代码」
     ↓
6️⃣ 粘贴到你的 Python 文件并运行
```

---

## 🎮 实际示例

### 示例 1：录制记事本操作

#### 操作步骤：

1. 运行 `py_inspect_recorder.py`
2. 点击「开始录制」
3. 打开记事本（`notepad.exe`）
4. 在记事本中：
   - 输入 "Hello World"
   - 点击「文件」菜单
   - 点击「另存为」
5. 回到 Recorder，点击「停止录制」

#### 生成的代码：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 自动生成的 Pywinauto 脚本

from pywinauto import Application
import time

def main():
    # 连接到应用程序
    app = Application(backend='uia').connect(process=12345)
    window = app.window(title_re='.*无标题 - 记事本.*')
    window.wait('visible', timeout=10)

    # 执行操作

    # 操作 1: click
    element = window.child_window(class_name="Edit", control_type="Edit")
    element.wait('visible', timeout=10)
    element.click()
    time.sleep(0.5)  # 等待操作完成

    # 操作 2: type
    element = window.child_window(class_name="Edit", control_type="Edit")
    element.wait('visible', timeout=10)
    element.type_keys("Hello World")
    time.sleep(0.5)  # 等待操作完成

    # 操作 3: click
    element = window.child_window(title="文件")
    element.wait('visible', timeout=10)
    element.click()
    time.sleep(0.5)  # 等待操作完成

    # 操作 4: click
    element = window.child_window(title="另存为...")
    element.wait('visible', timeout=10)
    element.click()
    time.sleep(0.5)  # 等待操作完成

    print('✅ 操作执行完成')

if __name__ == '__main__':
    main()
```

---

### 示例 2：录制计算器操作

#### 操作步骤：

1. 开始录制
2. 打开计算器（Windows 10/11）
3. 点击：8 → + → 2 → =
4. 停止录制

#### 生成的代码：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pywinauto import Application
import time

def main():
    app = Application(backend='uia').connect(process=45678)
    window = app.window(title_re='.*计算器.*')
    window.wait('visible', timeout=10)

    # 操作 1: click - 数字 8
    element = window.child_window(auto_id="num8Button")
    element.wait('visible', timeout=10)
    element.click()
    time.sleep(0.5)

    # 操作 2: click - 加号
    element = window.child_window(auto_id="plusButton")
    element.wait('visible', timeout=10)
    element.click()
    time.sleep(0.5)

    # 操作 3: click - 数字 2
    element = window.child_window(auto_id="num2Button")
    element.wait('visible', timeout=10)
    element.click()
    time.sleep(0.5)

    # 操作 4: click - 等号
    element = window.child_window(auto_id="equalButton")
    element.wait('visible', timeout=10)
    element.click()
    time.sleep(0.5)

    print('✅ 操作执行完成')

if __name__ == '__main__':
    main()
```

---

## 🖥️ 界面说明

### 控制面板

```
┌─────────────────────────────────────────────────────┐
│ ⚙️ 控制面板                                          │
│ Backend: [UIA ▼]  🔴 开始录制  ⏸️ 停止录制  ❓ 帮助  │
└─────────────────────────────────────────────────────┘
```

- **Backend**: 选择自动化后端
  - `UIA` (推荐) - 适用于现代应用（Windows 10/11）
  - `Win32` - 适用于老旧应用

- **开始录制**: 启动录制模式
- **停止录制**: 停止录制并提交所有操作
- **帮助**: 显示帮助信息

### 操作列表面板

```
┌──────────────────────────────────┐
│ 📋 录制的操作                     │
│                                  │
│ [1] 点击: Edit (窗口: 记事本)     │
│ [2] 输入: "Hello World"          │
│ [3] 点击: 文件 (窗口: 记事本)     │
│ [4] 点击: 另存为... (窗口: 记事本)│
│                                  │
└──────────────────────────────────┘
```

实时显示录制的每个操作。

### 代码生成面板

```
┌─────────────────────────────────────────────┐
│ 💻 生成的代码                                │
│                                             │
│ #!/usr/bin/env python3                     │
│ from pywinauto import Application          │
│ ...                                        │
│                                             │
│ [📋 复制代码]  [🗑️ 清空]                     │
└─────────────────────────────────────────────┘
```

自动生成的完整可执行脚本，点击「复制代码」一键复制。

---

## 🎯 支持的操作类型

### 1. 鼠标点击

**触发条件**: 鼠标左键点击任意元素

**生成代码**:
```python
element = window.child_window(auto_id="btnSave")
element.click()
```

### 2. 文本输入

**触发条件**: 在点击元素后输入文字，按 Enter 或点击其他元素提交

**生成代码**:
```python
element = window.child_window(class_name="Edit")
element.type_keys("Hello World")
```

### 3. 特殊按键

**支持的按键**: Tab, Enter, Esc

**生成代码**:
```python
element.type_keys("{TAB}")
element.type_keys("{ENTER}")
```

---

## ⚙️ 高级特性

### 1. 元素定位策略

工具会按优先级自动选择最佳定位方式：

#### 优先级 1：AutomationId（最稳定）
```python
element = window.child_window(auto_id="num8Button")
```

#### 优先级 2：Name/Title
```python
element = window.child_window(title="保存")
```

#### 优先级 3：Class + Control Type
```python
element = window.child_window(class_name="Button", control_type="Button")
```

#### 优先级 4：仅 Control Type
```python
element = window.child_window(control_type="Edit")
```

### 2. 防抖机制

工具内置 0.5 秒防抖，避免录制重复点击。

### 3. 智能文本累积

在同一元素上连续输入时，会累积所有文本直到：
- 按下 Enter 键
- 点击其他元素
- 停止录制

---

## 🔧 故障排查

### 问题 1: 元素识别失败

**症状**: 点击后显示 "⚠️ 元素识别失败"

**原因**:
- 某些应用不支持 UI Automation
- Backend 选择不正确

**解决方案**:
```python
# 尝试切换 Backend
UIA ←→ Win32
```

### 问题 2: 无法捕获输入

**症状**: 输入文字后没有生成代码

**原因**: 文本输入未提交

**解决方案**:
- 输入后按 Enter 键
- 或点击其他元素
- 或点击「停止录制」

### 问题 3: 生成的代码运行失败

**症状**: 复制代码后运行报错

**常见原因**:
- Process ID 已失效（应用已关闭）
- 元素属性动态变化

**解决方案**:
```python
# 修改连接方式：从 connect 改为 start
# ❌ 原代码
app = Application(backend='uia').connect(process=12345)

# ✅ 修改后
app = Application(backend='uia').start('notepad.exe')
# 或
app = Application(backend='uia').connect(title_re='.*记事本.*')
```

### 问题 4: 录制了不需要的操作

**解决方案**: 点击「清空」按钮，重新开始录制

---

## 💡 最佳实践

### 1. 录制前准备

```bash
# 确保目标应用已启动
# 最小化干扰窗口
# 明确操作流程
```

### 2. 录制时注意

- ⏱️ 避免过快连续点击
- 🎯 每个操作间留 0.5-1 秒间隔
- 📝 输入完成后按 Enter 或点击其他元素

### 3. 录制后优化

生成的代码可能需要手动调整：

```python
# 优化 1: 修改连接方式
# 从 connect(process=xxx) 改为 start() 或 connect(title=xxx)

# 优化 2: 调整等待时间
time.sleep(0.5)  # 可根据实际情况调整

# 优化 3: 添加错误处理
try:
    element.click()
except Exception as e:
    print(f"操作失败: {e}")

# 优化 4: 使用更精确的定位
# 结合多个属性
element = window.child_window(
    auto_id="btnSave",
    class_name="Button"
)
```

---

## 📊 与其他工具对比

| 功能 | PyInspect Recorder | Swapy | Playwright Codegen |
|------|-------------------|-------|--------------------|
| 实时录制 | ✅ | ❌ | ✅ |
| 自动生成代码 | ✅ | ✅ (手动) | ✅ |
| Windows 桌面 | ✅ | ✅ | ❌ (仅 Web) |
| Web 应用 | ❌ | ❌ | ✅ |
| 文本输入录制 | ✅ | ❌ | ✅ |
| 一键复制 | ✅ | ⚠️ 手动 | ✅ |
| 元素检查 | ⚠️ 基础 | ✅ 详细 | ✅ 详细 |

### 推荐组合使用

```
PyInspect Recorder (录制)
    ↓
生成初始代码
    ↓
PyInspect Enhanced (调试优化)
    ↓
检查元素属性，优化定位器
    ↓
最终代码
```

---

## 🎓 完整工作流示例

### 场景：自动化 ERP 系统登录和数据录入

#### 第 1 步：录制操作

```bash
python py_inspect_recorder.py
# 点击「开始录制」
```

#### 第 2 步：执行操作

1. 打开 ERP 系统
2. 输入用户名
3. 输入密码
4. 点击登录
5. 点击「员工管理」
6. 点击「新建员工」
7. 填写员工信息

#### 第 3 步：停止并复制代码

点击「停止录制」→「复制代码」

#### 第 4 步：优化代码

```python
#!/usr/bin/env python3
from pywinauto import Application
import time

def login_erp(username, password):
    """登录 ERP 系统"""
    app = Application(backend='uia').start('erp.exe')
    window = app.window(title_re='.*ERP.*')
    window.wait('visible', timeout=10)

    # 输入用户名
    username_field = window.child_window(auto_id="txtUsername")
    username_field.set_text(username)

    # 输入密码
    password_field = window.child_window(auto_id="txtPassword")
    password_field.set_text(password)

    # 点击登录
    login_btn = window.child_window(auto_id="btnLogin")
    login_btn.click()
    time.sleep(2)  # 等待登录完成

    return app

def create_employee(app, employee_data):
    """创建新员工"""
    window = app.window(title_re='.*ERP.*')

    # 点击员工管理
    window.child_window(title="员工管理").click()
    time.sleep(1)

    # 点击新建员工
    window.child_window(auto_id="btnNewEmployee").click()
    time.sleep(1)

    # 填写员工信息
    dialog = app.window(title_re='.*新建员工.*')
    dialog.child_window(auto_id="txtName").set_text(employee_data['name'])
    dialog.child_window(auto_id="txtEmail").set_text(employee_data['email'])
    dialog.child_window(auto_id="btnSave").click()

    print(f"✅ 员工 {employee_data['name']} 创建成功")

if __name__ == '__main__':
    # 登录
    app = login_erp('admin', 'password123')

    # 创建员工
    employees = [
        {'name': '张三', 'email': 'zhangsan@company.com'},
        {'name': '李四', 'email': 'lisi@company.com'}
    ]

    for emp in employees:
        create_employee(app, emp)
```

#### 第 5 步：运行自动化脚本

```bash
python my_erp_automation.py
```

---

## 📚 相关资源

- **PyInspect Enhanced** - 元素检查和代码生成工具（静态）
- **Pywinauto 官方文档** - https://pywinauto.readthedocs.io/
- **UI Automation 文档** - https://docs.microsoft.com/en-us/windows/win32/winauto/

---

## 🐛 已知限制

1. **不支持拖拽操作** - 只支持点击和输入
2. **不支持右键菜单** - 只捕获左键点击
3. **不支持鼠标悬停** - 无法录制 hover 事件
4. **某些应用无法识别** - 部分特殊应用（如游戏）不支持 UI Automation
5. **Process ID 会失效** - 生成的代码需要修改连接方式

---

## 🔮 后续改进计划

- [ ] 支持拖拽操作
- [ ] 支持右键菜单
- [ ] 支持窗口切换跟踪
- [ ] 支持断言生成（验证操作结果）
- [ ] 支持更智能的等待策略
- [ ] 支持代码编辑和调试

---

**🎉 现在你可以像使用 Playwright Codegen 一样，一边操作 Windows 应用，一边生成自动化代码了！**
