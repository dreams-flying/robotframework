# Pywinauto + Swapy 快速参考卡

## 🚀 安装（3 步）

```bash
# 1. 安装 Pywinauto
pip install pywinauto

# 2. 下载 Swapy
https://github.com/pywinauto/SWAPY/releases

# 3. 运行 swapy.exe
```

---

## 📖 基础语法

### 启动应用

```python
from pywinauto import Application

# 启动新应用
app = Application(backend='uia').start('notepad.exe')

# 连接到已运行的应用
app = Application(backend='uia').connect(path='notepad.exe')
# 或
app = Application(backend='uia').connect(title_re='.*Notepad')
```

### 获取窗口

```python
# 通过标题
window = app.window(title='Untitled - Notepad')

# 通过正则表达式（推荐）
window = app.window(title_re='.*Notepad')

# 通过类名
window = app.window(class_name='Notepad')
```

### 查找元素

```python
# 通过 AutomationId（最稳定）
button = window.child_window(auto_id="btnSave")

# 通过类名
edit = window.child_window(class_name="Edit")

# 通过控件类型
button = window.child_window(control_type="Button")

# 通过标题
button = window.child_window(title="OK")

# 组合条件（推荐）
button = window.child_window(
    auto_id="btnSave",
    control_type="Button",
    class_name="Button"
)

# 多个相同元素时使用索引
first_edit = window.child_window(class_name="Edit", found_index=0)
second_edit = window.child_window(class_name="Edit", found_index=1)
```

---

## 🎮 常用操作

### 点击

```python
button.click()              # 普通点击
button.click_input()        # 使用鼠标坐标点击
button.double_click()       # 双击
button.right_click()        # 右键点击
```

### 输入文本

```python
# 方法 1：type_keys（模拟键盘）
edit.type_keys("Hello World")
edit.type_keys("Hello{ENTER}")  # 输入后按 Enter

# 方法 2：set_text（直接设置，推荐）
edit.set_text("Hello World")

# 清空
edit.set_text("")
```

### 菜单操作

```python
# 选择菜单项
window.menu_select("File->Save As")
window.menu_select("Edit->Find->Find Next")
```

### 获取文本

```python
# 获取窗口标题
title = window.window_text()

# 获取控件文本
text = edit.window_text()

# 或
text = edit.get_value()
```

### 选择下拉框

```python
combo = window.child_window(auto_id="cmbCity")

# 按索引选择
combo.select(0)

# 按文本选择
combo.select("北京")
```

### 复选框和单选按钮

```python
checkbox = window.child_window(auto_id="chkAgree")

# 勾选
checkbox.check()

# 取消勾选
checkbox.uncheck()

# 切换状态
checkbox.toggle()

# 检查状态
is_checked = checkbox.get_check_state()  # 0=未选中, 1=选中
```

---

## ⏱️ 等待

```python
# 等待窗口就绪
window.wait('ready', timeout=10)

# 等待元素可见
element.wait('visible', timeout=10)

# 等待元素启用
element.wait('enabled', timeout=10)

# 等待元素存在
element.wait('exists', timeout=10)

# 简单延时
import time
time.sleep(2)
```

---

## ⌨️ 键盘快捷键

```python
# 特殊键
edit.type_keys(
    "{ENTER}"       # Enter
    "{TAB}"         # Tab
    "{BACKSPACE}"   # Backspace
    "{DELETE}"      # Delete
    "{ESC}"         # Escape
    "{UP}"          # 上箭头
    "{DOWN}"        # 下箭头
    "{LEFT}"        # 左箭头
    "{RIGHT}"       # 右箭头
    "{HOME}"        # Home
    "{END}"         # End
    "{PGUP}"        # Page Up
    "{PGDN}"        # Page Down
    "{F1}"          # F1 (F1-F12)
)

# 组合键
edit.type_keys(
    "^a"            # Ctrl+A
    "^c"            # Ctrl+C
    "^v"            # Ctrl+V
    "^s"            # Ctrl+S
    "+{TAB}"        # Shift+Tab
    "%{F4}"         # Alt+F4
)

# 符号
# ^ = Ctrl
# + = Shift
# % = Alt

# 示例：全选并复制
edit.type_keys("^a")  # Ctrl+A 全选
edit.type_keys("^c")  # Ctrl+C 复制
```

---

## 🔍 调试技巧

### 查看所有控件

```python
# 打印控件树（超级有用！）
window.print_control_identifiers()

# 保存到文件
with open('controls.txt', 'w', encoding='utf-8') as f:
    window.print_control_identifiers(f)
```

### 截图

```python
# 窗口截图
window.capture_as_image().save('screenshot.png')
```

### 检查元素状态

```python
# 是否存在
exists = element.exists()

# 是否可见
visible = element.is_visible()

# 是否启用
enabled = element.is_enabled()

# 是否激活
active = element.is_active()

# 获取矩形坐标
rect = element.rectangle()  # (left, top, right, bottom)
```

---

## 🐛 常见问题速查

### 找不到元素？

```python
# 1. 打印所有控件
window.print_control_identifiers()

# 2. 增加等待
element.wait('exists', timeout=10)

# 3. 尝试切换 backend
app = Application(backend='win32')  # 或 'uia'

# 4. 检查窗口是否激活
window.set_focus()
```

### 点击无效？

```python
# 1. 确保可见和启用
element.wait('visible')
element.wait('enabled')

# 2. 使用 click_input
element.click_input()

# 3. 先激活窗口
window.set_focus()
element.click()
```

### 中文乱码？

```python
# 使用 set_text 而不是 type_keys
edit.set_text("中文测试")

# 或使用剪贴板
import pyperclip
pyperclip.copy("中文测试")
edit.type_keys("^v")
```

---

## 📝 完整示例模板

```python
from pywinauto import Application
import time

def automate_app():
    """应用自动化模板"""

    try:
        # 1. 启动应用
        print("启动应用...")
        app = Application(backend='uia').start('app.exe')
        time.sleep(2)

        # 2. 获取主窗口
        print("连接主窗口...")
        main_window = app.window(title_re='.*App')
        main_window.wait('ready', timeout=10)

        # 3. 执行操作
        print("执行操作...")

        # 输入文本
        edit = main_window.child_window(auto_id="txtInput")
        edit.wait('visible', timeout=5)
        edit.set_text("Hello")

        # 点击按钮
        button = main_window.child_window(auto_id="btnSubmit")
        button.wait('enabled', timeout=5)
        button.click()

        # 4. 验证结果
        print("验证结果...")
        result = main_window.child_window(auto_id="lblResult").window_text()
        print(f"结果: {result}")

        # 5. 清理
        time.sleep(2)
        main_window.close()

        print("✓ 完成！")
        return True

    except Exception as e:
        print(f"✗ 错误: {e}")

        # 截图用于调试
        try:
            main_window.capture_as_image().save('error.png')
            print("  错误截图已保存: error.png")
        except:
            pass

        return False

if __name__ == "__main__":
    automate_app()
```

---

## 🎯 Swapy 使用流程

### 1. 启动 Swapy

```
1. 运行 swapy.exe
2. File -> Launch Application
3. 输入: notepad.exe
4. 点击 OK
```

### 2. 查找元素

```
1. 在左侧窗口树中展开应用
2. 点击目标元素
3. 右侧显示属性：
   - AutomationId
   - ClassName
   - ControlType
   - Name
```

### 3. 复制代码

```
右侧下方会自动生成代码：

button = window.child_window(
    auto_id="btnSave",
    control_type="Button"
)
button.click()

直接复制到你的脚本中！
```

---

## 📊 Backend 选择

| Backend | 适用场景 | 速度 | 兼容性 |
|---------|---------|------|--------|
| **uia** | UWP, WPF, .NET, 现代应用 | 慢 | 广 |
| **win32** | Win32, VB6, 老旧应用 | 快 | 窄 |

**建议：** 先试 `uia`，不行再用 `win32`

```python
# 尝试 uia
app = Application(backend='uia')

# 如果不行，尝试 win32
app = Application(backend='win32')
```

---

## 🔗 资源链接

- 📖 [完整教程](./PYWINAUTO_SWAPY_GUIDE.md)
- 💻 [代码示例](./pywinauto_swapy_examples.py)
- 🌐 [官方文档](https://pywinauto.readthedocs.io/)
- 📥 [Swapy 下载](https://github.com/pywinauto/SWAPY/releases)

---

## ✅ 快速检查清单

开始自动化前，确保：

- [ ] 已安装 Pywinauto: `pip install pywinauto`
- [ ] 已下载 Swapy
- [ ] 确定使用的 backend (`uia` 或 `win32`)
- [ ] 使用 Swapy 查找了所有需要的元素
- [ ] 记录了 AutomationId 或其他定位属性
- [ ] 添加了适当的等待
- [ ] 添加了错误处理

---

**Happy Automating!** 🚀
