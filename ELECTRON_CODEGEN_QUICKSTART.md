# Electron Codegen 快速入门指南

## 🚀 5 分钟快速开始

### 步骤 1：安装依赖（如果还没安装）

```bash
pip install playwright
playwright install
```

### 步骤 2：运行录制脚本

```bash
python electron_codegen_recorder.py
```

### 步骤 3：开始录制

1. **脚本会自动查找并启动 VS Code**
2. **按 Enter 键打开 Playwright Inspector**
3. **点击 Inspector 中的红色 Record 按钮**
4. **在 VS Code 中执行您想录制的操作**
5. **从 Inspector 复制生成的代码**

---

## 📋 完整示例流程

### 示例：录制"创建新文件"操作

#### 1. 启动录制

```bash
$ python electron_codegen_recorder.py

╔═══════════════════════════════════════════════════════════════════════╗
║   Playwright Electron Codegen 录制工具                               ║
╚═══════════════════════════════════════════════════════════════════════╝

✓ 找到 VS Code: /usr/bin/code
正在启动 Electron 应用...
✓ Electron 应用已启动
✓ 已获取主窗口
✓ VS Code 已就绪

按 Enter 键打开 Playwright Inspector...
```

#### 2. 在 VS Code 中操作

Playwright Inspector 打开后：

1. 点击 **🔴 Record** 按钮
2. 在 VS Code 中：
   - 点击 File 菜单
   - 点击 New File
   - 输入一些文本
   - 按 Ctrl+S 保存

#### 3. Inspector 生成的代码（示例）

```python
page.get_by_role("menubar").get_by_text("File").click()
page.get_by_text("New File").click()
page.locator(".monaco-editor").click()
page.keyboard.type("Hello World")
page.keyboard.press("Control+S")
page.get_by_placeholder("File name").fill("test.txt")
page.get_by_role("button", name="Save").click()
```

#### 4. 复制代码并使用

创建您的自动化脚本：

```python
from playwright.sync_api import sync_playwright

def create_new_file():
    with sync_playwright() as p:
        electron = p._impl._electron
        app = electron.launch(
            executable_path="/usr/bin/code"
        )

        page = app.first_window()

        # 粘贴 Inspector 生成的代码
        page.get_by_role("menubar").get_by_text("File").click()
        page.get_by_text("New File").click()
        page.locator(".monaco-editor").click()
        page.keyboard.type("Hello World")

        # 等待查看结果
        page.wait_for_timeout(3000)

        app.close()

if __name__ == "__main__":
    create_new_file()
```

---

## ⚙️ 配置选项

### 选项 1：自动查找（推荐）

不需要任何配置，脚本会自动查找 VS Code：

```bash
python electron_codegen_recorder.py
```

### 选项 2：环境变量

```bash
# Linux/Mac
export VSCODE_PATH="/path/to/code"
python electron_codegen_recorder.py

# Windows
set VSCODE_PATH=C:\path\to\Code.exe
python electron_codegen_recorder.py
```

### 选项 3：在脚本中配置

编辑 `electron_codegen_recorder.py`，找到这一行：

```python
# CUSTOM_VSCODE_PATH = "/path/to/your/vscode"
```

取消注释并设置您的路径：

```python
CUSTOM_VSCODE_PATH = "/usr/bin/code"  # Linux
# 或
CUSTOM_VSCODE_PATH = "/Applications/Visual Studio Code.app/Contents/MacOS/Electron"  # Mac
# 或
CUSTOM_VSCODE_PATH = r"C:\Users\YourName\AppData\Local\Programs\Microsoft VS Code\Code.exe"  # Windows
```

---

## 🔧 常见问题解决

### 问题 1：找不到 VS Code

**错误信息：**
```
❌ 错误：找不到 VS Code 可执行文件
```

**解决方案：**

**Linux:**
```bash
# 查找 VS Code
which code

# 如果输出 /usr/bin/code，则设置：
export VSCODE_PATH="/usr/bin/code"
```

**Mac:**
```bash
# VS Code 通常在这里
ls "/Applications/Visual Studio Code.app/Contents/MacOS/Electron"

# 设置路径
export VSCODE_PATH="/Applications/Visual Studio Code.app/Contents/MacOS/Electron"
```

**Windows:**
```cmd
# 检查这些路径
dir "C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe"
dir "C:\Program Files\Microsoft VS Code\Code.exe"

# 设置找到的路径
set VSCODE_PATH=C:\Users\YourName\AppData\Local\Programs\Microsoft VS Code\Code.exe
```

---

### 问题 2：VS Code 启动但 Inspector 没打开

**原因：** 可能需要手动按 Enter

**解决方案：**
```bash
# 看到这个提示时
按 Enter 键打开 Playwright Inspector...

# 按下 Enter 键
```

---

### 问题 3：录制的代码有动态 ID

**示例问题代码：**
```python
page.locator("[id=\"142258285_tree\"]").click()  # ❌ ID 每次都变
```

**解决方案：**

查看项目中的修复文档：

```bash
# 查看速查表
cat CODEGEN_FIX_CHEATSHEET.md

# 或运行修复示例
python fix_dynamic_id_example.py
```

**快速修复：**
```python
# 方法 1：使用文本定位（推荐）
page.get_by_text("上海").first.click()

# 方法 2：使用 role
page.get_by_role("button", name="提交").click()

# 方法 3：部分匹配 ID
page.locator("[id$='_tree']").click()  # 匹配结尾
```

---

### 问题 4：超时错误

**错误信息：**
```
❌ 超时：20秒内未能检测到浏览器上下文
```

**解决方案：**

1. **增加超时时间**：

   编辑 `electron_codegen_recorder.py`，找到：
   ```python
   timeout = 20  # 秒
   ```
   改为：
   ```python
   timeout = 60  # 增加到 60 秒
   ```

2. **关闭 VS Code 启动页面**：

   VS Code 启动时可能显示欢迎页或更新提示，手动关闭这些弹窗。

3. **清理 VS Code 配置**：
   ```bash
   # 备份并重置设置（谨慎操作）
   mv ~/.config/Code ~/.config/Code.backup
   ```

---

### 问题 5：Playwright 版本太旧

**错误信息：**
```
⚠️  当前 Playwright 版本可能不支持 _electron API
```

**解决方案：**
```bash
# 更新 Playwright
pip install --upgrade playwright
playwright install

# 检查版本
pip show playwright
# 应该是 1.40+ 或更高
```

---

## 💡 最佳实践

### 1. 录制前的准备

✅ **关闭不必要的弹窗**
   - 欢迎页面
   - 更新提示
   - 扩展推荐

✅ **使用简洁的工作区**
   - 关闭多余的面板
   - 只保留需要操作的部分

✅ **确保界面语言一致**
   - 如果生成英文代码，使用英文界面
   - 如果生成中文代码，使用中文界面

### 2. 录制时的技巧

✅ **点击文本而不是图标**
```python
# ✅ 好
page.get_by_text("File").click()

# ❌ 不好
page.locator("div.icon-file").click()
```

✅ **使用搜索功能**
```python
# ✅ 更稳定
page.get_by_placeholder("Search").fill("settings")
page.get_by_text("Preferences: Open Settings").click()

# ❌ 直接点击菜单（可能位置变化）
page.get_by_role("menubar").click()
```

✅ **添加等待**
```python
# ✅ 等待元素出现
page.get_by_text("Save").wait_for(state="visible")
page.get_by_text("Save").click()
```

### 3. 录制后的优化

✅ **移除不必要的操作**
```python
# Codegen 可能录制了多余的点击
page.locator(".editor").click()  # ← 可能不需要
page.keyboard.type("Hello")
```

✅ **合并相似操作**
```python
# ❌ Codegen 生成
page.keyboard.press("Control")
page.keyboard.press("S")

# ✅ 优化后
page.keyboard.press("Control+S")
```

✅ **添加验证**
```python
# 操作后验证结果
page.get_by_text("Save").click()

# 验证文件已保存
assert page.get_by_text("Saved successfully").is_visible()
```

---

## 📚 进阶使用

### 录制复杂操作

#### 示例 1：安装扩展

```python
def install_extension(extension_id: str):
    with sync_playwright() as p:
        app = p._impl._electron.launch(executable_path="/usr/bin/code")
        page = app.first_window()

        # 打开扩展面板
        page.get_by_role("tab", name="Extensions").click()

        # 搜索扩展
        page.get_by_placeholder("Search Extensions").fill(extension_id)
        page.keyboard.press("Enter")

        # 等待结果
        page.wait_for_selector(f"[data-extension-id='{extension_id}']")

        # 点击安装
        page.locator(f"[data-extension-id='{extension_id}']").get_by_text("Install").click()

        # 等待安装完成
        page.wait_for_selector(f"[data-extension-id='{extension_id}'] >> text=Installed")

        app.close()
```

#### 示例 2：调试代码

```python
def debug_python_file():
    with sync_playwright() as p:
        app = p._impl._electron.launch(executable_path="/usr/bin/code")
        page = app.first_window()

        # 打开文件
        page.keyboard.press("Control+P")
        page.keyboard.type("main.py")
        page.keyboard.press("Enter")

        # 设置断点（点击行号）
        page.locator(".line-numbers").nth(10).click()

        # 开始调试
        page.keyboard.press("F5")

        # 等待调试工具栏出现
        page.wait_for_selector(".debug-toolbar")

        # 单步执行
        page.get_by_title("Step Over").click()

        app.close()
```

---

## 🎯 下一步

录制完成后，您可以：

1. **优化生成的代码**
   - 参考 `CODEGEN_FIX_CHEATSHEET.md`
   - 修复动态 ID
   - 改进定位器稳定性

2. **创建完整的测试套件**
   ```python
   import pytest
   from playwright.sync_api import sync_playwright

   @pytest.fixture
   def vscode_app():
       with sync_playwright() as p:
           app = p._impl._electron.launch(executable_path="/usr/bin/code")
           yield app
           app.close()

   def test_create_file(vscode_app):
       page = vscode_app.first_window()
       # 您的录制代码...
       assert page.get_by_text("Untitled-1").is_visible()
   ```

3. **集成 CI/CD**
   ```yaml
   # .github/workflows/test.yml
   name: VS Code Automation Tests
   on: [push]
   jobs:
     test:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         - uses: actions/setup-python@v2
         - run: pip install playwright
         - run: playwright install
         - run: python your_test.py
   ```

---

## 📖 相关文档

- **修复 Codegen 问题**: `CODEGEN_FIX_CHEATSHEET.md`
- **动态 ID 解决方案**: `fix_dynamic_id_example.py`
- **详细修复说明**: `ELECTRON_CODEGEN_FIXES.md`
- **Playwright 官方文档**: https://playwright.dev/python/

---

## 🆘 需要帮助？

如果遇到问题：

1. **查看错误日志**：脚本会输出详细的错误信息
2. **检查路径配置**：确保 VS Code 路径正确
3. **更新依赖**：`pip install --upgrade playwright`
4. **查看示例**：运行项目中的示例脚本

---

**祝录制愉快！** 🎉
