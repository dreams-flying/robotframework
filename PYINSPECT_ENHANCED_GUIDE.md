# PyInspect Enhanced - 完整使用指南

## 🎯 简介

**PyInspect Enhanced** 是一个功能强大的 Windows UI 元素检查器，专为 Pywinauto 自动化开发设计。它结合了原版 PyInspect 的元素查看功能，并添加了类似 Swapy 的**自动代码生成**能力。

---

## ✨ 新增功能

### 相比原版的改进：

| 功能 | 原版 PyInspect | Enhanced 版本 |
|------|---------------|--------------|
| **控件树查看** | ✅ | ✅ |
| **属性查看** | ✅ | ✅ |
| **代码生成** | ❌ | ✅ **自动生成** |
| **代码复制** | ❌ | ✅ **一键复制** |
| **完整脚本** | ❌ | ✅ **可直接运行** |
| **操作选择** | ❌ | ✅ **click/type/set_text** |
| **右键菜单** | ❌ | ✅ |
| **三栏布局** | ❌ | ✅ **可调整大小** |
| **标签页代码** | ❌ | ✅ **定位/完整脚本** |

---

## 📦 安装

### 依赖

```bash
pip install pywinauto
pip install PyQt5
pip install pyperclip  # 用于复制到剪贴板
```

### 运行

```bash
python py_inspect_enhanced.py
```

---

## 🖥️ 界面布局

```
┌────────────────────────────────────────────────────────────────────┐
│ PyInspect Enhanced - Windows UI 元素检查器                         │
├────────────────────────────────────────────────────────────────────┤
│ Backend: [UIA ▼]                                  [❓ 帮助]        │
├──────────────────┬──────────────────┬─────────────────────────────┤
│                  │                  │                             │
│  📂 控件树       │  📋 元素属性     │  💻 生成的代码              │
│                  │                  │                             │
│  └─ Window       │  属性    | 值    │  [定位代码] [完整脚本]      │
│     ├─ Button    │  ──────┼────── │                             │
│     ├─ Edit      │  auto_id| btn1  │  element = window.child...  │
│     └─ Menu      │  class  | Button│                             │
│                  │  control| Button│                             │
│                  │  name   | Save  │                             │
│                  │                  │                             │
│                  │                  │  操作: [click ▼]            │
│                  │                  │  [📋 复制定位] [📋 复制脚本]│
├──────────────────┴──────────────────┴─────────────────────────────┤
│ ✓ 就绪 - 在左侧选择一个控件查看属性和生成代码                      │
└────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 快速开始（5 分钟）

### 步骤 1：启动工具

```bash
python py_inspect_enhanced.py
```

### 步骤 2：选择 Backend

```
默认是 UIA (推荐用于现代应用)
如果需要，可以切换到 Win32
```

### 步骤 3：浏览控件树

```
1. 工具会自动加载当前所有窗口
2. 在左侧控件树中展开应用
3. 点击任意控件
```

### 步骤 4：查看生成的代码

```
右侧会自动生成：
- Tab 1: 定位代码（4 种定位方法）
- Tab 2: 完整可运行脚本
```

### 步骤 5：复制代码

```
点击 "📋 复制定位代码" 或 "📋 复制完整脚本"
代码自动复制到剪贴板
粘贴到你的自动化脚本中
```

---

## 💻 生成的代码示例

### 定位代码（Tab 1）

当你选中一个按钮后，会生成：

```python
# ============================================================
# 元素定位代码
# ============================================================

# 方法 1：使用 AutomationId（推荐）⭐⭐⭐
element = window.child_window(auto_id="btnSave")

# 方法 2：使用类名
element = window.child_window(
    class_name="Button",
    control_type="Button"
)

# 方法 3：使用名称
element = window.child_window(title="Save")

# 方法 4：组合定位（最精确）⭐⭐⭐⭐⭐
element = window.child_window(
    auto_id="btnSave",
    control_type="Button",
    class_name="Button"
)
```

### 完整脚本（Tab 2）

```python
#!/usr/bin/env python3
"""
自动生成的 Pywinauto 脚本
Backend: uia
"""

from pywinauto import Application
import time

# ============================================================================
# 配置
# ============================================================================

APP_PATH = 'notepad.exe'  # 修改为你的应用路径
BACKEND = 'uia'

# ============================================================================
# 主函数
# ============================================================================

def main():
    # 1. 启动应用（或连接到已运行的应用）
    print("启动应用...")
    app = Application(backend=BACKEND).start(APP_PATH)
    # 或连接到已运行的应用：
    # app = Application(backend=BACKEND).connect(path=APP_PATH)

    time.sleep(2)

    # 2. 获取主窗口
    print("连接到主窗口...")
    main_window = app.window(title_re='.*')  # 修改为实际窗口标题

    # 3. 定位元素
    print("定位元素...")

    # 使用 AutomationId 定位（推荐）
    element = main_window.child_window(auto_id="btnSave")

    # 4. 等待元素可用
    element.wait('visible', timeout=10)

    # 5. 执行操作
    print("执行操作...")
    element.click()

    print("✓ 操作完成！")

    # 6. 清理
    time.sleep(2)
    # main_window.close()

if __name__ == "__main__":
    main()
```

**这个脚本可以直接运行！** 只需修改 `APP_PATH` 为你的应用路径。

---

## 🎮 功能详解

### 1. Backend 选择

```
UIA (UI Automation) - 推荐
  ✅ 支持 UWP、WPF、.NET 应用
  ✅ 提供 automation_id（最稳定的定位方式）
  ✅ Windows 10/11 首选

Win32 - 老旧应用
  ✅ 支持 Win32、VB6 应用
  ✅ 速度快
  ❌ 不支持现代应用
```

### 2. 操作类型选择

```python
# click - 点击操作
element.click()

# type - 键盘输入（模拟键盘）
element.type_keys("Hello World!")

# set_text - 直接设置文本（推荐）
element.set_text("Hello World!")

# get_text - 获取文本
text = element.window_text()
print(f"文本内容: {text}")
```

### 3. 右键菜单

在控件树中右键点击：

```
🔄 刷新 - 重新加载控件树
📋 复制元素名称 - 复制选中元素的名称
```

### 4. 属性查看

显示元素的所有属性：

**通用属性：**
- `control_id` - 控件 ID
- `class_name` - 类名
- `enabled` - 是否启用
- `handle` - 窗口句柄
- `name` - 控件名称
- `rectangle` - 位置和大小
- `visible` - 是否可见

**UIA 专有属性：**
- `automation_id` - 自动化 ID ⭐**最重要**
- `control_type` - 控件类型
- `framework_id` - 框架 ID
- `runtime_id` - 运行时 ID

---

## 📖 实战示例

### 示例 1：自动化记事本

#### 1. 启动 PyInspect Enhanced

```bash
python py_inspect_enhanced.py
```

#### 2. 打开记事本

```bash
# 在另一个终端
notepad.exe
```

#### 3. 在 PyInspect 中查找元素

```
1. 在控件树中展开 Notepad 窗口
2. 找到 Edit 控件（文本框）
3. 点击选中
```

#### 4. 查看生成的代码

右侧会显示：

```python
# 方法 1：使用 AutomationId（推荐）⭐⭐⭐
element = window.child_window(auto_id="15")  # 注意：记事本的 Edit 可能没有明确的 automation_id

# 方法 2：使用类名
element = window.child_window(
    class_name="Edit",
    control_type="Edit"
)
```

#### 5. 复制并使用代码

```python
from pywinauto import Application

app = Application(backend='uia').start('notepad.exe')
window = app.window(title_re='.*Notepad')

# 粘贴生成的代码
edit = window.child_window(class_name="Edit")
edit.set_text("Hello from PyInspect!")
```

---

### 示例 2：自动化计算器

#### 1. 启动计算器

```bash
calc.exe
```

#### 2. 在 PyInspect 中查找 "8" 按钮

```
1. 展开 Calculator 窗口
2. 找到数字 "8" 按钮
3. 点击选中
```

#### 3. 查看 automation_id

```
右侧属性表显示：
automation_id: "num8Button"  ⭐
control_type: "Button"
name: "Eight"
```

#### 4. 生成的代码

```python
# 方法 1：使用 AutomationId（推荐）⭐⭐⭐
element = window.child_window(auto_id="num8Button")

# 方法 4：组合定位（最精确）⭐⭐⭐⭐⭐
element = window.child_window(
    auto_id="num8Button",
    control_type="Button",
    class_name="Button"
)
```

#### 5. 完整脚本

点击"完整脚本" Tab，复制代码：

```python
from pywinauto import Application
import time

app = Application(backend='uia').start('calc.exe')
time.sleep(2)

calc = app.window(class_name='ApplicationFrameWindow')

# 使用 AutomationId 定位
element = calc.child_window(auto_id="num8Button")
element.wait('visible', timeout=10)
element.click()

print("✓ 操作完成！")
```

---

## 🔧 高级技巧

### 1. 快速查找特定控件

```
1. 展开控件树
2. 使用 Ctrl+F 在树中搜索（如果 PyQt 支持）
3. 或者在右键菜单中使用"复制元素名称"
```

### 2. 对比不同 Backend

```
有些应用在 UIA 下显示的属性更详细
有些老应用只能用 Win32

建议：
1. 先用 UIA 试试
2. 如果元素找不到或属性不全，切换到 Win32
```

### 3. 处理动态 ID

```
如果 automation_id 每次都变化：
- 使用 class_name + control_type 组合
- 使用 name（如果稳定）
- 使用层级定位（parent -> child）
```

### 4. 生成的代码优化

```python
# 生成的代码可能包含多余的属性
# 你可以简化：

# 原始（生成的）
element = window.child_window(
    auto_id="btnSave",
    control_type="Button",
    class_name="Button"
)

# 简化（如果 auto_id 唯一）
element = window.child_window(auto_id="btnSave")
```

---

## 📊 与其他工具对比

| 工具 | 代码生成 | 易用性 | 功能 | 推荐度 |
|------|---------|-------|------|-------|
| **PyInspect Enhanced** | ✅ 自动 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **⭐⭐⭐⭐⭐** |
| **Swapy** | ✅ 自动 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Inspect.exe** | ❌ 无 | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **原版 PyInspect** | ❌ 无 | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |

**PyInspect Enhanced 优势：**
- ✅ 自动生成代码（类似 Swapy）
- ✅ 完整可运行脚本
- ✅ 多种定位方法
- ✅ 一键复制
- ✅ 开源免费

---

## 🐛 常见问题

### Q1: 找不到应用的窗口？

**A:**
```
1. 确保应用已经打开
2. 点击右键菜单中的"刷新"
3. 尝试切换 Backend (UIA <-> Win32)
```

### Q2: automation_id 显示 None？

**A:**
```
有些控件没有 automation_id，这时候：
- 使用 class_name
- 使用 control_type + name
- 使用组合定位
```

### Q3: 生成的代码运行报错？

**A:**
```
1. 检查 APP_PATH 是否正确
2. 检查窗口标题是否正确（修改 title_re）
3. 确保元素已加载（增加 time.sleep）
4. 检查 backend 类型是否匹配
```

### Q4: 复制按钮没反应？

**A:**
```
确保安装了 pyperclip:
pip install pyperclip

如果还不行，手动选中代码并复制（Ctrl+C）
```

---

## 🎓 最佳实践

### 1. 定位器优先级

```
1. ✅ automation_id（如果有）
2. ✅ class_name + control_type
3. ✅ name（如果稳定）
4. ⚠️ 坐标（不推荐）
```

### 2. 代码复用

```python
# 创建一个定位器字典
LOCATORS = {
    'save_button': {'auto_id': 'btnSave'},
    'text_box': {'class_name': 'Edit'},
    'menu': {'control_type': 'Menu'}
}

# 在代码中使用
save_btn = window.child_window(**LOCATORS['save_button'])
```

### 3. 错误处理

```python
# 总是添加等待和错误处理
try:
    element = window.child_window(auto_id="btnSave")
    element.wait('visible', timeout=10)
    element.click()
except Exception as e:
    print(f"错误: {e}")
    # 截图用于调试
    window.capture_as_image().save('error.png')
```

---

## 📚 相关资源

- [Pywinauto 完整教程](./PYWINAUTO_SWAPY_GUIDE.md)
- [Pywinauto 快速参考](./PYWINAUTO_QUICK_REFERENCE.md)
- [代码示例](./pywinauto_swapy_examples.py)
- [Pywinauto 官方文档](https://pywinauto.readthedocs.io/)

---

## ✅ 总结

**PyInspect Enhanced** 是一个强大的 Pywinauto 开发辅助工具：

✅ **自动生成代码** - 类似 Swapy，但完全开源
✅ **完整脚本** - 生成可直接运行的脚本
✅ **多种定位方法** - 4 种定位方式任选
✅ **一键复制** - 快速复制到剪贴板
✅ **可调整布局** - 三栏布局可自由调整
✅ **右键菜单** - 快捷操作
✅ **跨平台** - Windows/Linux (atspi)

**开始使用：**
```bash
pip install pywinauto PyQt5 pyperclip
python py_inspect_enhanced.py
```

**Happy Automating!** 🚀
