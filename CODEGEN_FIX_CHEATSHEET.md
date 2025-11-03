# Playwright Codegen 定位器失败速查表

## 🚨 快速诊断

### 步骤 1：确定失败类型

运行您的代码，查看错误信息：

| 错误信息 | 失败类型 | 跳转到 |
|---------|---------|-------|
| `Timeout 30000ms exceeded` <br> `waiting for locator...` | 找不到元素 | [类型1](#类型1找不到元素) |
| `Error: strict mode violation` <br> `locator resolved to X elements` | 匹配多个元素 | [类型2](#类型2匹配多个元素) |
| `Element is not visible` | 元素不可见 | [类型3](#类型3元素不可见) |
| `Element is outside of the viewport` | 元素在视口外 | [类型4](#类型4元素在视口外) |
| `Other element would receive the click` | 元素被遮挡 | [类型5](#类型5元素被遮挡) |

---

## 类型1：找不到元素

### 原因 A：动态 ID（最常见）⭐⭐⭐

#### ❌ Codegen 生成：
```python
page.locator("[id=\"142258285_tree\"]").click()
```

#### ✅ 快速修复：
```python
# 方法1：部分匹配（如果 ID 有固定模式）
page.locator("[id$='_tree']").click()  # 匹配结尾
page.locator("[id^='tree_']").click()  # 匹配开头
page.locator("[id*='tree']").click()   # 包含

# 方法2：动态获取（推荐）
trigger = page.get_by_placeholder("Name/名称")
tree_id = trigger.get_attribute("data-target")
page.locator(f"#{tree_id}").click()

# 方法3：避免使用 ID（最佳）
page.get_by_text("上海").first.click()
```

---

### 原因 B：元素在 iframe 中

#### ❌ Codegen 生成：
```python
page.locator("#button").click()  # 找不到
```

#### ✅ 快速修复：
```python
# 诊断：检查是否有 iframe
frame_count = len(page.frames)
print(f"框架数: {frame_count}")  # >1 说明有 iframe

# 修复：使用 frame_locator
iframe = page.frame_locator("iframe[name='contentFrame']")
iframe.locator("#button").click()
```

---

### 原因 C：元素还未加载

#### ❌ Codegen 生成：
```python
page.goto("https://url.com")
page.locator("#button").click()  # 太快，元素还没出现
```

#### ✅ 快速修复：
```python
page.goto("https://url.com")

# 方法1：等待页面加载完成
page.wait_for_load_state("networkidle")
page.locator("#button").click()

# 方法2：等待元素出现
page.wait_for_selector("#button", state="visible")
page.locator("#button").click()

# 方法3：增加超时（Playwright 默认等待）
page.locator("#button").click(timeout=10000)  # 等待 10 秒
```

---

## 类型2：匹配多个元素

#### ❌ Codegen 生成：
```python
page.get_by_text("上海").click()
# 错误: strict mode violation: locator resolved to 5 elements
```

#### ✅ 快速修复：
```python
# 方法1：指定第几个
page.get_by_text("上海").first.click()   # 第一个
page.get_by_text("上海").nth(2).click()  # 第三个（索引从0开始）
page.get_by_text("上海").last.click()    # 最后一个

# 方法2：增加上下文（推荐）
page.locator("div.city-selector").get_by_text("上海").click()

# 方法3：遍历选择可见的
elements = page.get_by_text("上海").all()
for el in elements:
    if el.is_visible():
        el.click()
        break
```

---

## 类型3：元素不可见

#### ❌ Codegen 生成：
```python
page.locator("button").click()
# 错误: Element is not visible
```

#### ✅ 快速修复：
```python
# 方法1：等待可见
page.locator("button").wait_for(state="visible")
page.locator("button").click()

# 方法2：检查是否在隐藏的容器中
# 可能需要先展开父元素
page.locator(".dropdown-toggle").click()  # 展开下拉
page.locator("button").click()

# 方法3：检查是否在未激活的 tab 中
page.locator("a[data-tab='settings']").click()  # 切换 tab
page.locator("button").click()
```

---

## 类型4：元素在视口外

#### ❌ Codegen 生成：
```python
page.locator("button.footer-submit").click()
# 错误: Element is outside of the viewport
```

#### ✅ 快速修复：
```python
# 方法1：滚动到元素
button = page.locator("button.footer-submit")
button.scroll_into_view_if_needed()
button.click()

# 方法2：Playwright 自动滚动（默认行为）
# 如果失败，尝试增加等待
page.wait_for_timeout(500)
page.locator("button.footer-submit").click()
```

---

## 类型5：元素被遮挡

#### ❌ Codegen 生成：
```python
page.locator("button").click()
# 错误: Other element would receive the click
# (例如被 loading 遮罩遮挡)
```

#### ✅ 快速修复：
```python
# 方法1：等待遮挡元素消失（推荐）
page.locator(".loading-overlay").wait_for(state="hidden")
page.locator("button").click()

# 方法2：强制点击（跳过检查）
page.locator("button").click(force=True)
# ⚠️ 注意：force=True 会跳过所有可操作性检查

# 方法3：JavaScript 点击（最后手段）
page.locator("button").evaluate("el => el.click()")
```

---

## 🎯 定位器优先级（推荐顺序）

### 1. Role + Name（最优先）✅✅✅
```python
page.get_by_role("button", name="提交")
page.get_by_role("textbox", name="用户名")
```
- ✅ 最稳定，抗 HTML 变化
- ✅ 符合无障碍标准
- ❌ 需要元素有正确的 role

### 2. Text（次优先）✅✅
```python
page.get_by_text("员工自助")
page.get_by_text("登录", exact=True)  # 精确匹配
```
- ✅ 直观易懂
- ✅ 用户视角
- ❌ 文本改变会失效

### 3. Label（表单专用）✅✅
```python
page.get_by_label("用户名")
page.get_by_label("密码")
```
- ✅ 表单元素首选
- ✅ 语义化
- ❌ 仅适用于表单

### 4. Placeholder（搜索框）✅
```python
page.get_by_placeholder("请输入关键字")
```
- ✅ 适合搜索框
- ❌ 可能重复

### 5. Test ID（专为测试设计）✅✅✅
```python
page.get_by_test_id("submit-button")
```
- ✅ 最可靠（如果有）
- ❌ 需要开发添加 `data-testid`

### 6. CSS Selector（备用）⚠️
```python
page.locator("button.submit-btn")
page.locator("#username")
```
- ✅ 灵活
- ❌ 依赖样式，可能变化

### 7. XPath（最后手段）❌
```python
page.locator("xpath=//button[text()='提交']")
```
- ❌ 性能差
- ❌ 可读性差
- ✅ 仅在其他方法都不行时使用

---

## 🛠️ 通用修复模板

```python
from playwright.sync_api import sync_playwright, Page

def robust_click(page: Page, selector: str, strategy: str = "auto"):
    """
    健壮的点击方法，自动处理各种失败情况

    Args:
        page: Playwright Page 对象
        selector: 选择器字符串
        strategy: 策略 ("auto", "force", "js")
    """

    locator = page.locator(selector)

    try:
        # 步骤1：等待元素可见
        locator.wait_for(state="visible", timeout=10000)

        # 步骤2：滚动到可见区域
        locator.scroll_into_view_if_needed()

        # 步骤3：等待任何遮挡元素消失
        page.wait_for_timeout(500)

        # 步骤4：尝试点击
        if strategy == "force":
            locator.click(force=True)
        elif strategy == "js":
            locator.evaluate("el => el.click()")
        else:
            locator.click()

        print(f"✓ 成功点击: {selector}")
        return True

    except Exception as e:
        print(f"❌ 点击失败: {selector}")
        print(f"   错误: {str(e)}")

        # 诊断信息
        try:
            count = locator.count()
            print(f"   匹配元素数: {count}")
            if count > 0:
                print(f"   第一个元素可见: {locator.first.is_visible()}")
        except:
            pass

        return False


def robust_fill(page: Page, selector: str, text: str):
    """
    健壮的填充方法
    """
    locator = page.locator(selector)

    try:
        # 等待可见
        locator.wait_for(state="visible", timeout=10000)

        # 清空并填充
        locator.clear()
        locator.fill(text)

        # 验证
        value = locator.input_value()
        assert text in value, f"填充失败：期望 '{text}'，实际 '{value}'"

        print(f"✓ 成功填充: {selector} = {text}")
        return True

    except Exception as e:
        print(f"❌ 填充失败: {selector}")
        print(f"   错误: {str(e)}")
        return False


# 使用示例
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto("https://your-url.com")

    # 使用健壮方法
    robust_fill(page, "input[name='username']", "admin")
    robust_click(page, "button.submit")

    browser.close()
```

---

## 📊 常见场景速查

### 场景1：登录表单
```python
# ✅ 推荐
page.get_by_label("用户名").fill("admin")
page.get_by_label("密码").fill("password")
page.get_by_role("button", name="登录").click()
```

### 场景2：下拉选择
```python
# ✅ 推荐
page.locator("select[name='city']").select_option("上海")

# 或使用 role
page.get_by_role("combobox", name="城市").select_option("上海")
```

### 场景3：复选框
```python
# ✅ 推荐
page.get_by_role("checkbox", name="记住我").check()
page.get_by_role("checkbox", name="同意条款").check()
```

### 场景4：日期选择
```python
# ✅ 直接填充（如果支持）
page.locator("input[type='date']").fill("2024-01-01")

# ✅ 如果是自定义日期控件
page.locator(".date-picker-trigger").click()
page.get_by_text("15").click()  # 选择日期
```

### 场景5：文件上传
```python
# ✅ 推荐
page.get_by_label("上传文件").set_input_files("/path/to/file.pdf")

# 多个文件
page.locator("input[type='file']").set_input_files([
    "/path/to/file1.pdf",
    "/path/to/file2.pdf"
])
```

### 场景6：弹窗确认
```python
# ✅ 处理 JavaScript 对话框
page.on("dialog", lambda dialog: dialog.accept())
page.locator("button.delete").click()  # 触发确认对话框

# ✅ 处理自定义模态框
page.locator("button.open-modal").click()
page.locator(".modal").wait_for(state="visible")
page.locator(".modal button.confirm").click()
```

---

## 🔍 调试技巧

### 1. 截图调试
```python
# 失败时自动截图
try:
    page.locator("button").click()
except Exception as e:
    page.screenshot(path="error.png")
    print(f"错误截图已保存: {e}")
```

### 2. 慢动作模式
```python
# 启动时设置慢动作
browser = p.chromium.launch(
    headless=False,
    slow_mo=1000  # 每个操作延迟 1 秒
)
```

### 3. Playwright Inspector
```bash
# 以调试模式运行
PWDEBUG=1 python your_script.py

# 或在代码中暂停
page.pause()  # 打开 Inspector
```

### 4. 打印元素信息
```python
def inspect_element(page: Page, selector: str):
    """检查元素详细信息"""
    locator = page.locator(selector)

    print(f"\n检查: {selector}")
    print(f"  数量: {locator.count()}")

    if locator.count() > 0:
        first = locator.first
        print(f"  可见: {first.is_visible()}")
        print(f"  启用: {first.is_enabled()}")
        print(f"  文本: {first.inner_text()}")
        print(f"  ID: {first.get_attribute('id')}")
        print(f"  Class: {first.get_attribute('class')}")
```

### 5. 等待调试
```python
# 手动暂停查看页面状态
import time
page.locator("button").click()
time.sleep(5)  # 暂停 5 秒，手动检查页面
```

---

## 📚 完整示例：修复 Codegen 代码

### ❌ Codegen 原始代码（多处问题）
```python
def test_travel_application(page: Page):
    page.goto("https://portal.com")
    page.get_by_text("员工自助").click()
    page.get_by_text("出差申请").click()
    page.locator("[id=\"142258285_tree\"]").get_by_text("上海").click()
    page.locator("#submitBtn").click()
```

### ✅ 修复后代码（健壮稳定）
```python
def test_travel_application(page: Page):
    """出差申请自动化 - 修复后"""

    # 1. 导航并等待加载
    page.goto("https://portal.com")
    page.wait_for_load_state("networkidle")

    # 2. 点击员工自助（使用更稳定的定位器）
    employee_tab = page.get_by_role("link", name="员工自助")
    employee_tab.wait_for(state="visible", timeout=10000)
    employee_tab.click()

    # 3. 点击出差申请
    page.get_by_role("link", name="出差申请").click()
    page.wait_for_load_state("domcontentloaded")

    # 4. 选择城市（动态 ID 处理）
    # 点击城市输入框触发
    city_input = page.get_by_placeholder("Name/名称")
    city_input.click()
    city_input.fill("上海")

    # 动态获取树 ID
    tree_id = city_input.get_attribute("data-target")

    if tree_id:
        # 使用动态 ID
        tree = page.locator(f"#{tree_id}")
        tree.wait_for(state="visible")
        tree.get_by_text("上海", exact=True).first.click()
    else:
        # 后备方案：直接点击可见的选项
        page.get_by_text("上海", exact=True).first.click()

    # 5. 提交（使用更精确的定位器）
    submit_btn = page.get_by_role("button", name="提交")
    # 或者如果没有 role：
    # submit_btn = page.locator("button#submitBtn, button.submit-btn")

    submit_btn.wait_for(state="visible")
    submit_btn.scroll_into_view_if_needed()
    submit_btn.click()

    # 6. 验证结果
    success_msg = page.locator(".success-message, .alert-success")
    success_msg.wait_for(state="visible", timeout=10000)

    text = success_msg.inner_text()
    assert "成功" in text, f"提交失败: {text}"

    print("✓ 出差申请提交成功")
```

---

## ⚡ 一键诊断命令

在您的项目目录运行：

```bash
# 运行诊断工具
python debug_locators.py

# 查看所有修复方案
python fix_codegen_locators.py

# 使用 Playwright Inspector 调试
PWDEBUG=1 python your_script.py
```

---

## 📞 需要帮助？

如果仍然无法解决，请提供：

1. **完整错误信息**
   ```
   Error: Timeout 30000ms exceeded.
   =========================== logs ===========================
   waiting for locator('button')
   ```

2. **失败的代码**
   ```python
   page.locator("button").click()  # 这行失败
   ```

3. **目标元素的 HTML**
   ```html
   <button id="submit-btn" class="btn btn-primary">提交</button>
   ```

4. **页面 URL**（如果可以提供）

有了这些信息，可以提供更精确的解决方案！
