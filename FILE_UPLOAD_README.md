# Playwright 文件上传 - 快速参考

## 🎯 两个核心问题的答案

### 1️⃣ Playwright 如何上传本地文件？

**最简单的方法**：
```python
page.locator('input[type="file"]').set_input_files("path/to/file.pdf")
```

### 2️⃣ 为什么 playwright codegen 无法生成上传文件的代码？

**原因**：
- 文件选择对话框是**操作系统级别的UI**，不是浏览器
- Playwright codegen 只能记录浏览器内的操作
- 无法获取你在系统对话框中选择的文件路径

**解决方案**：手动添加上传代码

---

## 📚 文件列表

| 文件 | 说明 |
|------|------|
| `PLAYWRIGHT_FILE_UPLOAD_GUIDE.md` | 详细指南（理论+实践） |
| `playwright_file_upload_examples.py` | 10个可运行的示例 |
| `FILE_UPLOAD_README.md` | 本文件（快速参考） |

---

## 🚀 快速开始

### 安装依赖

```bash
pip install playwright
playwright install chromium
```

### 运行示例

```bash
# 运行交互式示例
python playwright_file_upload_examples.py

# 查看详细文档
cat PLAYWRIGHT_FILE_UPLOAD_GUIDE.md
```

---

## 💡 常用代码片段

### 片段 1: 基本上传

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://example.com/upload")

    # 上传文件
    page.locator('input[type="file"]').set_input_files("document.pdf")

    # 提交
    page.get_by_role("button", name="Upload").click()

    browser.close()
```

### 片段 2: 使用 file_chooser

```python
with page.expect_file_chooser() as fc_info:
    page.get_by_text("Choose File").click()

file_chooser = fc_info.value
file_chooser.set_files("document.pdf")
```

### 片段 3: 上传多个文件

```python
page.locator('input[type="file"]').set_input_files([
    "file1.pdf",
    "file2.jpg",
    "file3.docx"
])
```

### 片段 4: 上传虚拟文件（不需要实际文件）

```python
page.locator('input[type="file"]').set_input_files({
    'name': 'test.txt',
    'mimeType': 'text/plain',
    'buffer': b'File content here'
})
```

---

## 🔧 常见问题

### Q: 元素隐藏怎么办？

```python
# set_input_files 自动处理隐藏元素，无需特殊处理
page.locator('input[type="file"]').set_input_files("file.pdf")
```

### Q: 找不到文件怎么办？

```python
import os

# 使用绝对路径
file_path = os.path.abspath("file.pdf")
page.locator('input[type="file"]').set_input_files(file_path)
```

### Q: 如何验证文件已选择？

```python
# 检查 files.length
file_count = page.evaluate("""
    document.querySelector('input[type="file"]').files.length
""")
print(f"已选择 {file_count} 个文件")
```

### Q: 如何清空已选择的文件？

```python
# 传入空列表
page.locator('input[type="file"]').set_input_files([])
```

---

## 📖 10个示例说明

| # | 示例名称 | 说明 |
|---|---------|------|
| 1 | 基本文件上传 | 最简单的上传方法 |
| 2 | file_chooser 事件 | 处理文件选择对话框 |
| 3 | 上传多个文件 | 一次选择多个文件 |
| 4 | 上传虚拟文件 | 不需要实际文件，直接传内容 |
| 5 | 使用绝对路径 | 推荐的路径处理方式 |
| 6 | 隐藏的 input | 处理 display:none 的元素 |
| 7 | 动态生成文件 | 临时文件的创建和上传 |
| 8 | 验证文件名 | 确认选择了正确的文件 |
| 9 | 清空文件 | 取消已选择的文件 |
| 10 | 使用辅助函数 | 封装可复用的上传逻辑 |

---

## 🎓 学习路径

1. **入门**：阅读 `PLAYWRIGHT_FILE_UPLOAD_GUIDE.md` 的第1、2节
2. **实践**：运行 `playwright_file_upload_examples.py` 的示例1-3
3. **进阶**：学习示例4-7的高级技巧
4. **封装**：参考示例10创建自己的辅助函数

---

## ⚠️ 重要提示

### ✅ DO（推荐）

- 使用绝对路径
- 检查文件是否存在
- 添加上传成功的验证
- 使用 Path 对象管理路径

### ❌ DON'T（避免）

- 依赖相对路径
- 硬编码特定机器的路径
- 忘记等待上传完成
- 不验证上传结果

---

## 🔗 相关资源

- [Playwright 官方文档](https://playwright.dev/python/docs/input#upload-files)
- [本项目文档](./PLAYWRIGHT_FILE_UPLOAD_GUIDE.md)
- [示例代码](./playwright_file_upload_examples.py)

---

## 📞 问题反馈

如有问题或建议，请查看详细文档 `PLAYWRIGHT_FILE_UPLOAD_GUIDE.md`。
