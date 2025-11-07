# 日历选择器代码转换工具

## 📋 概述

这是一套完整的工具，用于将 Playwright codegen 生成的日期和时间选择代码转换为更智能、更鲁棒的辅助函数调用。

## 🎯 核心功能

### ✅ 解决的问题

1. **多日历组件冲突** - 页面存在多个日历时，精确定位到当前可见的日历
2. **重复日期数字** - 正确区分上月/当月/下月的相同日期（如"6"号）
3. **月份翻页导航** - 自动翻页到目标月份，支持跨年
4. **中文月份解析** - 正确解析"十一月"、"十二月"等长月份名
5. **时间选择简化** - 统一时间选择逻辑

## 📦 文件清单

```
calendar_converter.py       # 代码转换器主程序
calendar_helpers.py         # 日历和时间选择辅助函数
example_calendar_usage.py   # 使用指南和示例
test_original.py            # 测试用例（转换前）
test_converted.py           # 测试用例（转换后）
CALENDAR_CONVERTER_README.md # 本文档
```

## 🚀 快速开始

### 步骤1：运行测试

```bash
# 测试转换器
python calendar_converter.py
```

### 步骤2：转换您的代码

```bash
# 将原始代码转换为优化版本
python calendar_converter.py your_original.py your_converted.py
```

### 步骤3：查看使用指南

```bash
# 显示详细的使用说明
python example_calendar_usage.py
```

## 📖 转换示例

### 转换前（Playwright codegen 原始输出）

```python
def fill_form(page2, start_date_day, start_time):
    # 选择开始日期
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.SDATE").get_by_placeholder("YYYYMMDD").click()
    page2.get_by_role("cell", name=start_date_day, exact=True).first.click()

    # 选择开始时间
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.STIME").get_by_label("").click()
    page2.get_by_role("option", name=start_time).click()
```

### 转换后（智能辅助函数）

```python
from calendar_helpers import select_calendar_date, select_calendar_time

def fill_form(page2, start_date_day, start_time):
    # 选择开始日期
    select_calendar_date(
        page2,
        page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.SDATE").get_by_placeholder("YYYYMMDD"),
        target_day=start_date_day
    )

    # 选择开始时间
    select_calendar_time(
        page2,
        page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.STIME").get_by_label(""),
        start_time
    )
```

## 🔧 辅助函数详解

### `select_calendar_date()` - 智能日期选择

#### 基本用法：选择当前月日期

```python
# 选择当前月的5号
select_calendar_date(
    page2,
    page2.get_by_placeholder("YYYYMMDD"),
    target_day=5
)
```

#### 高级用法：指定月份和年份

```python
# 选择2025年11月6号
select_calendar_date(
    page2,
    page2.get_by_placeholder("YYYYMMDD"),
    target_day=6,
    target_month=11,
    target_year=2025
)
```

#### 核心优势

1. **自动去重** - 使用 CSS 选择器 `:not(.old):not(.new)` 过滤非当前月日期
2. **智能翻页** - 自动计算翻页方向，支持向前/向后导航
3. **跨年支持** - 正确处理年份转换
4. **多日历支持** - 限定到当前可见的日历组件
5. **备用策略** - 失败时自动降级到简单点击

### `select_calendar_time()` - 时间选择

```python
# 选择时间 09:00
select_calendar_time(
    page2,
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.STIME").get_by_label(""),
    "09:00"
)
```

## 🔍 技术细节

### 问题1：多日历组件冲突

**错误日志：**
```
Error: strict mode violation: locator(...) resolved to 4 elements
```

**解决方案：**
```python
# ✅ 限定到可见的日历
visible_calendar = page.locator('.datetimepicker:visible').first

# ✅ 在该日历作用域内操作
visible_calendar.locator('.day:not(.old):not(.new):text-is("5")')
```

### 问题2：中文月份解析错误

**错误示例：**
- "十一月" 被误解析为 "一月" (1月)
- "十二月" 被误解析为 "二月" (2月)

**解决方案：**
```python
# ✅ 长月份名在前，避免子串误匹配
month_patterns = [
    ('十二月', 12),  # 先检查
    ('十一月', 11),  # 先检查
    ('十月', 10),
    # ...
    ('二月', 2),     # 后检查
    ('一月', 1),     # 后检查
]
```

### 问题3：翻页后日历未更新

**错误现象：**
```
📅 当前: 2025年1月 → 点击下一月
📅 当前: 2025年2月 → 点击下一月  # ❌ 循环跳动
📅 当前: 2026年1月 → 点击上一月
```

**解决方案：**
```python
# ✅ 记录旧值
old_header_text = header_text

# 点击翻页
visible_calendar.locator('.next').click()

# ✅ 等待实际更新
for _ in range(10):
    page.wait_for_timeout(100)
    new_header_text = visible_calendar.locator('.switch').text_content()
    if new_header_text != old_header_text:
        break  # 已更新
```

## 📊 转换模式识别

转换器识别以下两种模式：

### 模式1：日期选择

**特征：**
- 第1行：`.get_by_placeholder("YYYYMMDD").click()`
- 第2行：`.get_by_role("cell", name=变量, exact=True).first.click()`

**转换：**
```python
select_calendar_date(page, 定位器, target_day=变量)
```

### 模式2：时间选择

**特征：**
- 第1行：`输入框.click()`
- 第2行：`.get_by_role("option", name=变量).click()`

**转换：**
```python
select_calendar_time(page, 定位器, 变量)
```

## 🧪 测试

### 运行内置测试

```bash
# 测试转换器逻辑
python calendar_converter.py

# 输出：
# ✅ 测试通过!
```

### 测试实际转换

```bash
# 转换测试文件
python calendar_converter.py test_original.py test_converted.py

# 对比结果
diff test_original.py test_converted.py
```

## 🎨 输出示例

### 日期选择日志

```
📅 当前日历显示: 2025年1月 (原文:一月)，目标: 2025年11月
→ 点击下一月
   ✓ 日历已更新: 一月 2025 → 二月 2025
📅 当前日历显示: 2025年2月 (原文:二月)，目标: 2025年11月
→ 点击下一月
   ✓ 日历已更新: 二月 2025 → 三月 2025
...
📅 当前日历显示: 2025年11月 (原文:十一月)，目标: 2025年11月
✅ 成功选择日期: 2025年11月6日
```

### 时间选择日志

```
✅ 成功选择时间: 09:00
```

## 🛡️ 错误处理

### 多层防护机制

1. **首选策略** - 精确 CSS 选择器
2. **备用策略** - 简单 `.first` 点击
3. **超时保护** - 最大翻页次数限制
4. **详细日志** - 便于调试

### 错误示例

```python
try:
    # 尝试精确选择
    day_locator.click()
except Exception as e:
    print(f"⚠️ 选择失败: {e}")
    # 降级到备用策略
    visible_calendar.get_by_role("cell", name=str(target_day), exact=True).first.click()
```

## 🔄 工作流程

```
原始 Playwright 代码
        ↓
calendar_converter.py (自动转换)
        ↓
优化后的代码 (使用 calendar_helpers)
        ↓
更鲁棒的自动化测试
```

## 📚 API 参考

### `select_calendar_date()`

**参数：**
- `page` (Page) - Playwright Page 对象
- `date_field_locator` (Locator) - 日期输入框定位器
- `target_day` (int) - 目标日期 1-31
- `target_month` (int, 可选) - 目标月份 1-12，默认当前月
- `target_year` (int, 可选) - 目标年份，默认当前年
- `max_attempts` (int, 可选) - 最大翻页次数，默认 12

**返回：** None

### `select_calendar_time()`

**参数：**
- `page` (Page) - Playwright Page 对象
- `time_field_locator` (Locator) - 时间输入框定位器
- `time_value` (str) - 时间值，如 "09:00"

**返回：** None

## 🐛 已知问题

无

## 🚀 未来改进

- [ ] 支持更多日期格式
- [ ] 支持英文月份
- [ ] 支持日期范围选择
- [ ] 添加更多测试用例

## 📄 许可证

MIT

## 👥 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 联系方式

如有问题，请创建 GitHub Issue。
