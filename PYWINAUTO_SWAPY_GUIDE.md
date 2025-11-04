# Pywinauto + Swapy 完整使用指南

## 🎯 简介

**Pywinauto** 是 Python 中最强大的 Windows GUI 自动化库，**Swapy** 是它的可视化辅助工具，可以帮你快速查找元素并生成代码。

---

## 📦 安装

### 1. 安装 Pywinauto

```bash
# 基础安装
pip install pywinauto

# 可选依赖
pip install pillow          # 图像识别支持
pip install comtypes        # COM 支持
pip install pywin32         # Windows API 支持
```

### 2. 下载 Swapy

```bash
# Swapy 下载地址
https://github.com/pywinauto/SWAPY/releases

# 下载 swapy-0.5.4.zip（或最新版本）
# 解压后运行 swapy.exe
```

### 3. 验证安装

```python
# 测试 Pywinauto
python -c "from pywinauto import Application; print('✓ Pywinauto 可用')"
```

---

## 🚀 快速开始（5 分钟教程）

### 步骤 1：启动 Swapy

```bash
# 1. 解压 swapy-0.5.4.zip
# 2. 双击运行 swapy.exe
```

### 步骤 2：录制操作

#### 2.1 使用 Swapy 查找元素

```
1. 打开目标应用（如记事本）
2. 在 Swapy 中：
   - 点击 "File" -> "Launch Application"
   - 输入: notepad.exe
   - 点击 "OK"

3. Swapy 会显示应用的窗口树
4. 点击树中的元素查看属性
```

#### 2.2 自动生成代码

```
1. 在 Swapy 左侧窗口树中选择元素
2. 右侧会显示：
   - Element properties（元素属性）
   - Python code（自动生成的代码）

3. 复制右侧的 Python 代码到你的脚本
```

### 步骤 3：运行生成的代码

```python
# Swapy 自动生成的代码示例
from pywinauto import Application

# 启动应用
app = Application(backend='uia').start('notepad.exe')

# 获取主窗口
main_window = app.window(title='Untitled - Notepad')

# 在文本框输入
edit_box = main_window.child_window(class_name="Edit")
edit_box.type_keys("Hello from Swapy!")

# 保存文件
main_window.menu_select("File->Save As")
```

---

## 📖 详细教程

### 1. Swapy 界面说明

```
┌─────────────────────────────────────────────────────────────┐
│ Swapy - Object Inspector for Pywinauto                     │
├─────────────────────────────────────────────────────────────┤
│ File  Options  Help                                        │
├──────────────────┬──────────────────────────────────────────┤
│                  │                                          │
│  窗口树          │  元素属性                                │
│  (左侧面板)      │  (右侧上方)                              │
│                  │                                          │
│  ├─ Window       │  - AutomationId: "Button1"              │
│  │  ├─ Button    │  - ClassName: "Button"                  │
│  │  ├─ Edit      │  - ControlType: Button                  │
│  │  └─ Menu      │  - IsEnabled: True                      │
│                  │                                          │
│                  ├──────────────────────────────────────────┤
│                  │                                          │
│                  │  自动生成的代码                          │
│                  │  (右侧下方)                              │
│                  │                                          │
│                  │  button = window.child_window(          │
│                  │      auto_id="Button1",                 │
│                  │      control_type="Button"              │
│                  │  )                                       │
│                  │  button.click()                         │
│                  │                                          │
└──────────────────┴──────────────────────────────────────────┘
```

### 2. Swapy 核心功能

#### 2.1 启动应用

```
方法 1：从 Swapy 启动
- File -> Launch Application
- 输入程序路径或名称
- 点击 OK

方法 2：连接到已运行的应用
- File -> Attach to Running Application
- 从列表中选择进程
- 点击 OK
```

#### 2.2 查找元素

```
1. 在左侧窗口树中展开应用结构
2. 点击任意元素
3. 右侧显示：
   - 所有属性（AutomationId、ClassName 等）
   - 推荐的定位器
   - 自动生成的代码
```

#### 2.3 刷新窗口树

```
- 点击工具栏的 "Refresh" 按钮
- 或按 F5
- 用于更新动态变化的界面
```

#### 2.4 高亮显示元素

```
- 选中元素后，Swapy 会在屏幕上高亮显示
- 帮助确认你找到了正确的元素
```

---

## 💻 实战示例

### 示例 1：自动化记事本

#### 步骤 A：使用 Swapy 探索记事本

```
1. 打开 Swapy
2. File -> Launch Application -> notepad.exe
3. 在左侧树中查看结构：

   └─ Notepad
      ├─ Menu Bar
      ├─ Edit (文本框)
      └─ Status Bar
```

#### 步骤 B：生成代码

```python
# Swapy 自动生成的完整代码
from pywinauto import Application
import time

# 1. 启动应用
app = Application(backend='uia').start('notepad.exe')
time.sleep(1)

# 2. 获取主窗口
# 在 Swapy 中点击主窗口，复制属性
main_window = app.window(title_re='.*Notepad')

# 3. 获取文本框
# 在 Swapy 中点击 Edit 控件，复制属性
edit = main_window.child_window(class_name="Edit", control_type="Edit")

# 4. 输入文本
edit.type_keys("Hello World!{ENTER}")
edit.type_keys("This is line 2.{ENTER}")

# 5. 保存文件
# 通过菜单保存
main_window.menu_select("File->Save As")
time.sleep(1)

# 6. 填写文件名
save_dialog = app.window(title_re='Save As')
filename_box = save_dialog.child_window(class_name="Edit", found_index=0)
filename_box.set_text("my_file.txt")

# 7. 点击保存按钮
save_button = save_dialog.child_window(title="Save", class_name="Button")
save_button.click()

# 8. 关闭应用
time.sleep(1)
main_window.close()
```

---

### 示例 2：自动化计算器

#### Swapy 查找步骤：

```
1. 启动计算器: calc.exe
2. 在 Swapy 中连接
3. 查找数字按钮的 AutomationId:
   - 数字 8: auto_id="num8Button"
   - 加号: auto_id="plusButton"
   - 数字 2: auto_id="num2Button"
   - 等号: auto_id="equalButton"
   - 结果显示: auto_id="CalculatorResults"
```

#### 生成的代码：

```python
from pywinauto import Application
import time

# 启动计算器
app = Application(backend='uia').start('calc.exe')
time.sleep(2)

# 获取计算器窗口
calc = app.window(class_name='ApplicationFrameWindow')

# 执行计算: 8 + 2
calc.child_window(auto_id="num8Button", control_type="Button").click()
time.sleep(0.3)

calc.child_window(auto_id="plusButton", control_type="Button").click()
time.sleep(0.3)

calc.child_window(auto_id="num2Button", control_type="Button").click()
time.sleep(0.3)

calc.child_window(auto_id="equalButton", control_type="Button").click()
time.sleep(0.3)

# 读取结果
result = calc.child_window(auto_id="CalculatorResults").window_text()
print(f"结果: {result}")

# 关闭
calc.close()
```

---

### 示例 3：企业应用自动化

#### 场景：自动化一个内部 ERP 系统

```python
from pywinauto import Application
import time

# 1. 启动 ERP 应用
app = Application(backend='uia').start('C:\\Program Files\\MyERP\\erp.exe')
time.sleep(3)

# 2. 登录（使用 Swapy 找到的 AutomationId）
login_window = app.window(title='ERP Login')

# 用户名输入框
username_box = login_window.child_window(auto_id="txtUsername")
username_box.set_text("admin")

# 密码输入框
password_box = login_window.child_window(auto_id="txtPassword")
password_box.set_text("password123")

# 登录按钮
login_btn = login_window.child_window(auto_id="btnLogin")
login_btn.click()

time.sleep(2)

# 3. 导航到订单页面
main_window = app.window(title='ERP - Main')

# 点击菜单
main_window.child_window(auto_id="menuOrders").click()
time.sleep(1)

# 点击"新建订单"
main_window.child_window(auto_id="btnNewOrder").click()
time.sleep(1)

# 4. 填写订单信息
order_window = app.window(title='New Order')

order_window.child_window(auto_id="txtCustomerName").set_text("张三")
order_window.child_window(auto_id="txtProduct").set_text("笔记本电脑")
order_window.child_window(auto_id="txtQuantity").set_text("5")
order_window.child_window(auto_id="txtPrice").set_text("5000")

# 5. 保存订单
order_window.child_window(auto_id="btnSave").click()

print("✓ 订单创建成功！")
```

---

## 🔧 高级技巧

### 1. 处理动态元素

```python
# 问题：元素 ID 每次都变化
# 解决：使用多个属性组合定位

# ❌ 不好（单一属性，可能变化）
button = window.child_window(auto_id="Button_12345")

# ✅ 好（多个属性组合）
button = window.child_window(
    class_name="Button",
    control_type="Button",
    title="确定"
)
```

### 2. 等待元素出现

```python
from pywinauto.timings import wait_until

# 方法 1：使用 wait
element.wait('visible', timeout=10)  # 等待最多 10 秒

# 方法 2：使用 wait_until
def element_exists():
    try:
        window.child_window(auto_id="btnSave").exists()
        return True
    except:
        return False

wait_until(10, 0.5, element_exists)  # 每 0.5 秒检查一次，最多 10 秒
```

### 3. 处理多个相同元素

```python
# 当有多个相同类型的元素时，使用 found_index

# 获取第一个 Edit 控件
first_edit = window.child_window(class_name="Edit", found_index=0)

# 获取第二个 Edit 控件
second_edit = window.child_window(class_name="Edit", found_index=1)

# 或者使用更精确的定位
username_edit = window.child_window(
    class_name="Edit",
    preceding_sibling="用户名:"  # 前面有"用户名:"标签的 Edit
)
```

### 4. 键盘快捷键

```python
# Pywinauto 支持的特殊键
edit.type_keys(
    "Hello{ENTER}"      # Enter 键
    "World{TAB}"        # Tab 键
    "{BACKSPACE 5}"     # 删除 5 个字符
    "^a"                # Ctrl+A（全选）
    "^c"                # Ctrl+C（复制）
    "^v"                # Ctrl+V（粘贴）
    "+{TAB}"            # Shift+Tab
    "%{F4}"             # Alt+F4
)

# 完整列表
"""
{ENTER} - Enter
{TAB} - Tab
{BACKSPACE} - Backspace
{DELETE} - Delete
{HOME} - Home
{END} - End
{UP} - 上箭头
{DOWN} - 下箭头
{LEFT} - 左箭头
{RIGHT} - 右箭头
{PGUP} - Page Up
{PGDN} - Page Down
{ESC} - Escape
{F1}-{F12} - 功能键

^ - Ctrl
+ - Shift
% - Alt
"""
```

### 5. 截图和日志

```python
# 截图
window.capture_as_image().save('screenshot.png')

# 打印控件树（用于调试）
window.print_control_identifiers()

# 打印到文件
with open('controls.txt', 'w', encoding='utf-8') as f:
    window.print_control_identifiers(f)
```

---

## 🐛 常见问题

### 问题 1：找不到元素

**症状：**
```python
ElementNotFoundError: Could not find 'Button'
```

**解决方案：**

```python
# 1. 使用 print_control_identifiers 查看所有元素
window.print_control_identifiers()

# 2. 在 Swapy 中刷新窗口树
# 点击 Refresh 按钮或按 F5

# 3. 等待元素加载
import time
time.sleep(2)  # 简单等待

# 或使用智能等待
element.wait('exists', timeout=10)

# 4. 检查 backend
# 尝试切换 backend
app = Application(backend='win32')  # 或 'uia'
```

### 问题 2：元素不可点击

**症状：**
```python
# 点击没反应或报错
button.click()
```

**解决方案：**

```python
# 1. 确保元素可见和启用
button.wait('visible', timeout=10)
button.wait('enabled', timeout=10)

# 2. 使用 click_input 代替 click
button.click_input()  # 使用鼠标坐标点击

# 3. 先激活窗口
window.set_focus()
button.click()

# 4. 使用键盘模拟
button.type_keys("{ENTER}")
```

### 问题 3：中文乱码

**症状：**
```python
# 输入中文显示乱码
```

**解决方案：**

```python
# 方法 1：使用 set_text（推荐）
edit.set_text("中文测试")

# 方法 2：设置编码
edit.type_keys("中文测试", with_spaces=True, pause=0.1)

# 方法 3：使用剪贴板
import pyperclip
pyperclip.copy("中文测试")
edit.type_keys("^v")  # Ctrl+V 粘贴
```

### 问题 4：Backend 选择

**UIA vs Win32：**

```python
# UIA (UI Automation) - 推荐用于现代应用
app = Application(backend='uia')
# 优点：支持 UWP、WPF、.NET 应用
# 缺点：较慢

# Win32 - 用于老旧应用
app = Application(backend='win32')
# 优点：速度快
# 缺点：不支持现代应用

# 如何选择？
# 1. 先试 'uia'
# 2. 如果不行或太慢，试 'win32'
# 3. 对于 Win32 老应用（如 VB6），必须用 'win32'
```

---

## 📊 Swapy vs Inspect.exe 对比

| 特性 | Swapy | Inspect.exe |
|------|-------|-------------|
| **开发者** | Pywinauto 社区 | Microsoft |
| **安装** | 独立下载 | Windows SDK |
| **界面** | 友好直观 | 专业但复杂 |
| **代码生成** | ✅ 自动生成 Python | ❌ 无 |
| **高亮显示** | ✅ | ✅ |
| **窗口树** | ✅ 清晰 | ✅ 详细 |
| **实时刷新** | ✅ | ✅ |
| **推荐度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

**结论：**
- **Swapy** - 适合快速开发和学习
- **Inspect.exe** - 适合深度调试

---

## 🎓 学习路径

### 初级（1-2 天）

1. ✅ 安装 Pywinauto 和 Swapy
2. ✅ 运行记事本示例
3. ✅ 学习基本元素定位
4. ✅ 了解 type_keys 和 click

### 中级（3-5 天）

1. ✅ 使用 Swapy 探索复杂应用
2. ✅ 学习错误处理
3. ✅ 掌握等待机制
4. ✅ 处理对话框和弹窗

### 高级（1-2 周）

1. ✅ 封装可复用函数
2. ✅ 图像识别集成
3. ✅ 性能优化
4. ✅ 企业级框架设计

---

## 📚 资源

### 官方文档
- [Pywinauto 文档](https://pywinauto.readthedocs.io/)
- [Pywinauto GitHub](https://github.com/pywinauto/pywinauto)
- [Swapy GitHub](https://github.com/pywinauto/SWAPY)

### 教程和示例
- [Pywinauto 入门教程](https://pywinauto.readthedocs.io/en/latest/getting_started.html)
- [示例代码集](https://github.com/pywinauto/pywinauto/tree/master/examples)

### 社区
- [Google Group](https://groups.google.com/g/pywinauto)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/pywinauto)

---

## ✅ 完整工作流程

### 从零开始的完整项目

#### 1. 需求分析
```
任务：自动化一个订单录入系统
- 打开应用
- 登录
- 填写订单表单
- 保存并验证
```

#### 2. 使用 Swapy 探索应用
```
1. 启动 Swapy
2. 连接到目标应用
3. 记录所有需要的元素：
   - 登录页面：用户名、密码、登录按钮
   - 主页面：菜单、工具栏
   - 订单页面：各个输入框、保存按钮
```

#### 3. 编写代码框架
```python
from pywinauto import Application
import time

class OrderAutomation:
    def __init__(self, app_path):
        self.app = Application(backend='uia').start(app_path)
        self.main_window = None

    def login(self, username, password):
        """登录"""
        # Swapy 生成的代码
        pass

    def create_order(self, order_data):
        """创建订单"""
        # Swapy 生成的代码
        pass

    def verify_order(self, order_id):
        """验证订单"""
        # Swapy 生成的代码
        pass

    def close(self):
        """关闭应用"""
        self.main_window.close()

# 使用
automation = OrderAutomation('C:\\App\\orders.exe')
automation.login('admin', 'password')
automation.create_order({
    'customer': '张三',
    'product': '笔记本',
    'quantity': 5
})
automation.verify_order('ORD-001')
automation.close()
```

#### 4. 填充 Swapy 生成的代码

```python
def login(self, username, password):
    """登录 - 使用 Swapy 找到的元素"""
    login_window = self.app.window(title='Login')

    # 从 Swapy 复制的代码
    login_window.child_window(auto_id="txtUser").set_text(username)
    login_window.child_window(auto_id="txtPass").set_text(password)
    login_window.child_window(auto_id="btnLogin").click()

    time.sleep(2)
    self.main_window = self.app.window(title='Main Window')
```

#### 5. 添加错误处理

```python
def login(self, username, password):
    """登录 - 带错误处理"""
    try:
        login_window = self.app.window(title='Login')
        login_window.wait('ready', timeout=10)

        login_window.child_window(auto_id="txtUser").set_text(username)
        login_window.child_window(auto_id="txtPass").set_text(password)
        login_window.child_window(auto_id="btnLogin").click()

        # 等待主窗口
        self.main_window = self.app.window(title='Main Window')
        self.main_window.wait('visible', timeout=10)

        print("✓ 登录成功")
        return True

    except Exception as e:
        print(f"✗ 登录失败: {e}")
        return False
```

#### 6. 测试和调试

```python
if __name__ == "__main__":
    automation = OrderAutomation('C:\\App\\orders.exe')

    if automation.login('admin', 'password'):
        print("开始创建订单...")
        # ...
```

---

## 🎉 总结

### Pywinauto + Swapy 的优势

✅ **Python 原生** - 无缝集成到 Python 项目
✅ **Swapy 可视化** - 快速找到元素
✅ **代码生成** - 自动生成定位代码
✅ **开源免费** - 完全免费
✅ **活跃维护** - 社区支持好
✅ **文档齐全** - 学习资源丰富

### 最佳实践

1. 📝 **先用 Swapy 探索**，再写代码
2. 🔍 **使用多个属性**组合定位元素
3. ⏱️ **添加适当等待**，避免速度问题
4. 🛡️ **错误处理必不可少**
5. 📊 **记录日志**，方便调试
6. 🧪 **充分测试**，确保稳定性

---

**开始您的 Windows 自动化之旅吧！** 🚀
