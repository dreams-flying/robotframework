# Playwright 文件上传完整指南

## 1️⃣ Playwright 如何上传本地文件

### 方法一：使用 `set_input_files()` （推荐）

这是最简单、最常用的方法，适用于标准的 `<input type="file">` 元素。

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://example.com/upload")

    # ✅ 上传单个文件
    page.locator('input[type="file"]').set_input_files("path/to/file.pdf")

    # ✅ 或者使用更具体的定位器
    page.get_by_label("Upload file").set_input_files("document.pdf")

    # ✅ 上传多个文件（如果支持）
    page.locator('input[type="file"]').set_input_files([
        "file1.pdf",
        "file2.jpg",
        "file3.docx"
    ])

    # ✅ 清空已选择的文件
    page.locator('input[type="file"]').set_input_files([])

    browser.close()
```

### 方法二：使用 `expect_file_chooser()` 事件

适用于点击按钮后打开文件选择对话框的情况。

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://example.com/upload")

    # ✅ 监听文件选择器事件
    with page.expect_file_chooser() as fc_info:
        # 点击触发文件选择对话框的按钮
        page.get_by_role("button", name="Upload File").click()

    # 获取文件选择器对象
    file_chooser = fc_info.value

    # 设置要上传的文件
    file_chooser.set_files("path/to/file.pdf")

    # 或上传多个文件
    file_chooser.set_files([
        "file1.pdf",
        "file2.jpg"
    ])

    browser.close()
```

### 方法三：上传文件内容（不需要实际文件）

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://example.com/upload")

    # ✅ 直接提供文件内容
    page.locator('input[type="file"]').set_input_files({
        'name': 'test.txt',
        'mimeType': 'text/plain',
        'buffer': b'This is file content'
    })

    # ✅ 上传多个虚拟文件
    page.locator('input[type="file"]').set_input_files([
        {
            'name': 'file1.txt',
            'mimeType': 'text/plain',
            'buffer': b'Content 1'
        },
        {
            'name': 'file2.txt',
            'mimeType': 'text/plain',
            'buffer': b'Content 2'
        }
    ])

    browser.close()
```

---

## 2️⃣ 为什么 playwright codegen 无法生成上传文件的代码

### 原因分析

#### 原因 1: 系统文件对话框的限制 🚫

当你点击"上传文件"按钮时，浏览器会打开**操作系统原生的文件选择对话框**：

```
┌─────────────────────────────────────┐
│  浏览器窗口 (Playwright 可以记录)   │
│                                     │
│  ┌───────────────────────────────┐ │
│  │ [选择文件] 按钮  ← codegen 能记录这个点击 │
│  └───────────────────────────────┘ │
└─────────────────────────────────────┘

        ↓ 点击后打开

┌─────────────────────────────────────┐
│ Windows/Mac/Linux 文件对话框         │
│ (操作系统级别，不是浏览器)            │
│                                     │
│ ❌ Playwright codegen 无法记录这里   │
│ ❌ 无法看到你选择了哪个文件          │
│ ❌ 无法获取文件路径                 │
└─────────────────────────────────────┘
```

**关键问题**：
- 文件选择对话框是**操作系统级别的UI**，不是浏览器DOM
- Playwright codegen 只能记录**浏览器内部**的操作
- 它无法"看到"你在系统对话框中的操作

#### 原因 2: 文件路径的不确定性 📁

即使 codegen 能检测到文件上传，它也面临以下问题：

```python
# ❌ codegen 不知道你选择了哪个文件
# 你选择的可能是：
#   - C:\Users\Alice\Documents\report.pdf (Windows)
#   - /home/bob/documents/report.pdf (Linux)
#   - /Users/charlie/Downloads/report.pdf (Mac)

# ❌ 这个路径在其他机器上无效
page.set_input_files("C:\\Users\\Alice\\Documents\\report.pdf")
```

#### 原因 3: 安全限制 🔒

浏览器出于安全考虑，**不允许网页直接访问本地文件系统**：

- JavaScript 无法读取文件的真实路径
- 只能获得一个"假路径"（如 `C:\fakepath\file.pdf`）
- Playwright codegen 也受到同样的限制

---

## 3️⃣ 解决方案：手动添加上传代码

虽然 codegen 不能自动生成，但你可以很容易地手动添加：

### 步骤 1: 使用 codegen 记录其他操作

```bash
playwright codegen https://example.com/upload
```

**codegen 可能生成：**
```python
page.goto("https://example.com/upload")
page.get_by_role("button", name="Choose File").click()  # 只记录了点击
# ❌ 没有文件上传的代码
page.get_by_role("button", name="Submit").click()
```

### 步骤 2: 手动添加上传代码

```python
page.goto("https://example.com/upload")

# ✅ 删除或注释掉点击按钮的代码
# page.get_by_role("button", name="Choose File").click()

# ✅ 手动添加上传代码
page.locator('input[type="file"]').set_input_files("path/to/file.pdf")

page.get_by_role("button", name="Submit").click()
```

### 步骤 3: 找到正确的 input 元素

如果不确定定位器，可以使用开发者工具检查：

```python
# 方法1: 使用 CSS 选择器
page.locator('input[type="file"]').set_input_files("file.pdf")

# 方法2: 使用 id
page.locator('#file-upload').set_input_files("file.pdf")

# 方法3: 使用 name 属性
page.locator('input[name="upload"]').set_input_files("file.pdf")

# 方法4: 使用 label 关联
page.get_by_label("Upload file").set_input_files("file.pdf")
```

---

## 4️⃣ 实用示例

### 示例 1: 表单文件上传

```python
from playwright.sync_api import sync_playwright

def upload_form_example():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # 打开上传页面
        page.goto("https://example.com/upload-form")

        # 填写其他表单字段
        page.get_by_label("Name").fill("张三")
        page.get_by_label("Email").fill("zhangsan@example.com")

        # ✅ 上传文件
        page.locator('input[type="file"]').set_input_files("resume.pdf")

        # 提交表单
        page.get_by_role("button", name="Submit").click()

        # 等待上传成功
        page.wait_for_selector("text=Upload successful")

        browser.close()
```

### 示例 2: 拖拽上传

```python
def drag_drop_upload_example():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://example.com/drag-drop-upload")

        # 即使UI是拖拽上传，底层通常还是用 input[type="file"]
        # ✅ 直接使用 set_input_files
        page.locator('input[type="file"]').set_input_files("document.pdf")

        # 或者如果页面有隐藏的 input
        page.evaluate("""
            document.querySelector('input[type="file"]').style.display = 'block';
        """)
        page.locator('input[type="file"]').set_input_files("document.pdf")

        browser.close()
```

### 示例 3: 动态生成文件并上传

```python
import tempfile
import os

def upload_generated_file():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://example.com/upload")

        # ✅ 动态生成临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is dynamically generated content")
            temp_file_path = f.name

        try:
            # 上传临时文件
            page.locator('input[type="file"]').set_input_files(temp_file_path)
            page.get_by_role("button", name="Upload").click()
            page.wait_for_selector("text=Success")
        finally:
            # 清理临时文件
            os.unlink(temp_file_path)

        browser.close()
```

---

## 5️⃣ 常见问题和解决方案

### 问题 1: 找不到文件输入元素

```python
# ❌ 错误：元素不可见
page.locator('input[type="file"]').set_input_files("file.pdf")
# Error: Element is not visible

# ✅ 解决：强制设置，即使元素隐藏
page.locator('input[type="file"]').set_input_files("file.pdf", force=True)

# 或者使元素可见
page.evaluate("document.querySelector('input[type=\"file\"]').style.display = 'block'")
page.locator('input[type="file"]').set_input_files("file.pdf")
```

### 问题 2: 文件路径错误

```python
# ❌ 相对路径可能找不到
page.locator('input[type="file"]').set_input_files("file.pdf")

# ✅ 使用绝对路径
import os
file_path = os.path.abspath("file.pdf")
page.locator('input[type="file"]').set_input_files(file_path)

# ✅ 或者使用 Path
from pathlib import Path
file_path = Path(__file__).parent / "files" / "document.pdf"
page.locator('input[type="file"]').set_input_files(str(file_path))
```

### 问题 3: 上传后需要等待处理

```python
# ✅ 上传文件
page.locator('input[type="file"]').set_input_files("large_file.pdf")

# ✅ 等待上传完成（观察网络请求）
with page.expect_response(lambda response: "upload" in response.url) as response_info:
    page.get_by_role("button", name="Upload").click()

response = response_info.value
print(f"Upload status: {response.status}")

# 或等待UI反馈
page.wait_for_selector("text=Upload complete")
```

---

## 6️⃣ 最佳实践

### ✅ DO（推荐做法）

```python
# 1. 使用绝对路径
import os
file_path = os.path.abspath("test.pdf")
page.set_input_files(file_path)

# 2. 检查文件是否存在
if os.path.exists(file_path):
    page.set_input_files(file_path)
else:
    raise FileNotFoundError(f"File not found: {file_path}")

# 3. 使用 Path 对象
from pathlib import Path
file_path = Path(__file__).parent / "fixtures" / "test.pdf"
page.set_input_files(str(file_path))

# 4. 添加等待和验证
page.set_input_files("file.pdf")
page.wait_for_function("document.querySelector('input[type=\"file\"]').files.length > 0")
```

### ❌ DON'T（避免）

```python
# 1. 不要依赖相对路径
page.set_input_files("../../../file.pdf")  # ❌

# 2. 不要忘记等待上传完成
page.set_input_files("large_file.zip")
page.click("button")  # ❌ 可能还没上传完

# 3. 不要硬编码路径
page.set_input_files("C:\\Users\\Alice\\file.pdf")  # ❌ 其他机器无效
```

---

## 7️⃣ 总结

| 问题 | 解决方案 |
|------|---------|
| **如何上传文件？** | 使用 `set_input_files()` 方法 |
| **codegen 为什么不生成？** | 系统文件对话框不在浏览器控制范围内 |
| **如何找到 input 元素？** | 使用开发者工具检查，或用 `input[type="file"]` |
| **支持多文件上传吗？** | 支持，传入文件路径列表 |
| **可以上传虚拟文件吗？** | 可以，使用 buffer 参数 |
| **隐藏的 input 怎么办？** | 使用 `force=True` 或先使其可见 |

---

## 🔗 参考资源

- [Playwright 官方文档 - 文件上传](https://playwright.dev/python/docs/input#upload-files)
- [Playwright API - set_input_files](https://playwright.dev/python/docs/api/class-locator#locator-set-input-files)
- [Playwright API - expect_file_chooser](https://playwright.dev/python/docs/api/class-page#page-expect-file-chooser)
