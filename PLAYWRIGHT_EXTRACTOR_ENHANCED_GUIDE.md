# Playwright脚本增强型分析器使用指南

## 📋 功能特性

这是一个功能强大的Playwright脚本分析工具，能够自动提取脚本中的所有关键信息并生成可用的测试代码。

### 核心能力

1. **全面的元素定位器识别** (15+种)
   - `get_by_text`, `get_by_role`, `get_by_label`, `get_by_placeholder`
   - `get_by_alt_text`, `get_by_title`, `get_by_test_id`
   - `locator`, `query_selector`, `xpath`
   - `frame_locator`, `nth`, `first`, `last`, `filter`

2. **完整的交互操作提取** (15+种)
   - 点击: `click`, `dblclick`, `hover`, `tap`
   - 输入: `fill`, `type`, `press`, `clear`
   - 选择: `select_option`, `check`, `uncheck`, `set_checked`
   - 上传: `upload_file`, `set_input_files`
   - 其他: `focus`, `blur`, `drag_to`

3. **等待和断言识别**
   - 等待: `wait_for_selector`, `wait_for_url`, `wait_for_load_state`, `wait_for_timeout`
   - 断言: `expect`, `to_be_visible`, `to_contain_text`, `to_have_value` 等

4. **智能代码生成**
   - 自动生成Robot Framework关键字
   - 自动生成配置文件（JSON格式）
   - 自动生成参数化测试模板
   - 智能提取可参数化的部分

5. **深度分析能力**
   - 代码行号追踪
   - 上下文信息提取
   - 变量赋值识别
   - 正则表达式提取
   - 操作流程可视化

6. **完整的分析报告**
   - 摘要统计报告
   - 详细操作流程
   - 定位器类型分布
   - 参数化建议

---

## 🚀 快速开始

### 1. 基本用法

```bash
# 分析单个Playwright脚本
python playwright_variable_extractor_enhanced.py codegen_script.py

# 指定输出目录
python playwright_variable_extractor_enhanced.py codegen_script.py ./output
```

### 2. Python代码中使用

```python
from playwright_variable_extractor_enhanced import analyze_playwright_script

# 分析脚本并生成所有文件
data = analyze_playwright_script('my_playwright_script.py', './analysis_output')

# 访问提取的数据
print(f"URL: {data.url}")
print(f"操作数: {len(data.actions)}")
print(f"定位器数: {len(data.locators)}")
```

### 3. 高级用法

```python
from playwright_variable_extractor_enhanced import PlaywrightAnalyzer

# 创建分析器
analyzer = PlaywrightAnalyzer('my_script.py')

# 执行分析
data = analyzer.analyze()

# 生成不同格式的输出
print(analyzer.generate_summary_report())  # 摘要报告
print(analyzer.generate_robot_keywords())  # Robot关键字
config = analyzer.generate_config_dict()   # 配置字典

# 保存所有结果
analyzer.save_analysis_results('./output')
```

---

## 📂 输出文件说明

运行分析后，会生成以下文件：

### 1. `*_analysis_report.txt` - 摘要分析报告
```
📋 Playwright脚本分析报告
================================================================================
📄 脚本文件: codegen_script.py
🌐 主URL: https://example.com

📊 统计信息:
  - 总URL数: 3
  - 定位器数: 25
  - 操作数: 18
  - 表单填充: 5
  ...

🔄 操作流程 (共18步):
  1. [  15行] fill(get_by_placeholder('用户名')) <- 'admin'
  2. [  18行] fill(get_by_placeholder('密码')) <- 'password123'
  3. [  21行] click(get_by_role('button'))
  ...
```

### 2. `*_keywords.robot` - Robot Framework关键字
```robot
*** Settings ***
Library    Browser

*** Keywords ***
打开测试页面
    [Arguments]    ${url}=https://example.com
    New Browser    chromium    headless=False
    New Context
    New Page    ${url}

填充字段1
    [Arguments]    ${value}=admin
    Fill Text    placeholder='用户名'    ${value}

点击_登录按钮
    Click    role=button
```

### 3. `*_config.json` - 配置文件
```json
{
  "url": "https://example.com",
  "urls": ["https://example.com", "https://example.com/dashboard"],
  "navigation": {
    "登录": {"type": "text", "value": "登录"},
    "员工自助": {"type": "text", "value": "员工自助"}
  },
  "form_data": {
    "fills": {
      "get_by_placeholder('用户名')": "admin",
      "get_by_placeholder('密码')": "password123"
    },
    "selects": {
      "get_by_label('城市')": ["北京", "上海"]
    }
  },
  "files": ["./test_file.pdf"],
  "keyboard_inputs": ["Enter", "Escape"],
  "statistics": {
    "total_locators": 25,
    "total_actions": 18
  }
}
```

### 4. `*_full_data.json` - 完整数据
包含所有提取的详细信息（定位器、操作、断言等），可用于进一步分析或自定义处理。

### 5. `*_test_template.robot` - 测试模板
```robot
*** Settings ***
Library    Browser
Resource    codegen_script_keywords.robot
Suite Setup    打开测试页面

*** Variables ***
${BASE_URL}    https://example.com
${FIELD1_VALUE}    admin
${FIELD2_VALUE}    password123

*** Test Cases ***
测试基本流程
    [Documentation]    基于Playwright Codegen生成的测试流程
    [Tags]    smoke    auto-generated
    执行完整测试流程

数据驱动测试
    [Documentation]    参数化测试示例
    [Template]    执行完整测试流程
    # TODO: 添加测试数据
```

---

## 🎯 实际使用示例

### 示例1: 分析登录流程

假设有这样的Playwright脚本：

```python
# login_test.py
from playwright.sync_api import sync_playwright

def test_login():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # 导航到登录页
        page.goto("https://example.com/login")

        # 填充表单
        page.get_by_placeholder("用户名").fill("testuser")
        page.get_by_placeholder("密码").fill("Password123")

        # 点击登录按钮
        page.get_by_role("button", name="登录").click()

        # 等待跳转
        page.wait_for_url("**/dashboard")

        # 验证登录成功
        expect(page.get_by_text("欢迎回来")).to_be_visible()

        browser.close()
```

**运行分析:**
```bash
python playwright_variable_extractor_enhanced.py login_test.py ./login_analysis
```

**生成的关键字文件:**
```robot
*** Keywords ***
打开测试页面
    [Arguments]    ${url}=https://example.com/login
    New Browser    chromium    headless=False
    New Context
    New Page    ${url}

填充用户名
    [Arguments]    ${value}=testuser
    Fill Text    placeholder='用户名'    ${value}

填充密码
    [Arguments]    ${value}=Password123
    Fill Text    placeholder='密码'    ${value}

点击登录按钮
    Click    role=button >> text='登录'

执行完整测试流程
    打开测试页面    https://example.com/login
    填充用户名    testuser
    填充密码    Password123
    点击登录按钮
```

### 示例2: 分析表单填写流程

```python
# form_test.py
page.goto("https://example.com/form")
page.get_by_label("姓名").fill("张三")
page.get_by_label("邮箱").fill("zhangsan@example.com")
page.get_by_label("城市").select_option("北京")
page.get_by_label("性别").check()
page.get_by_role("button", name="提交").click()
```

**生成的配置文件:**
```json
{
  "url": "https://example.com/form",
  "form_data": {
    "fills": {
      "get_by_label('姓名')": "张三",
      "get_by_label('邮箱')": "zhangsan@example.com"
    },
    "selects": {
      "get_by_label('城市')": ["北京"]
    }
  },
  "navigation": {
    "提交": {"type": "text", "value": "提交"}
  }
}
```

### 示例3: 分析复杂操作流程

```python
# complex_test.py
# 导航多层菜单
page.get_by_text("业务管理").click()
page.get_by_text("员工管理").click()
page.get_by_text("新增员工").click()

# 填写多个表单字段
page.get_by_placeholder("工号").fill("E001")
page.get_by_placeholder("姓名").fill("李四")
page.locator("#dept-select").select_option("技术部")
page.locator("input[type='date']").fill("2024-01-01")

# 上传文件
page.get_by_label("上传简历").set_input_files("resume.pdf")

# 使用键盘操作
page.get_by_placeholder("备注").press("Control+A")
page.get_by_placeholder("备注").press("Delete")
```

**生成的分析报告:**
```
📊 统计信息:
  - 定位器数: 11
  - 操作数: 10
  - 表单填充: 4
  - 下拉选择: 2
  - 点击元素: 3
  - 文件上传: 1
  - 键盘输入: 2

🔄 操作流程 (共10步):
  1. [  12行] click(get_by_text('业务管理'))
  2. [  13行] click(get_by_text('员工管理'))
  3. [  14行] click(get_by_text('新增员工'))
  4. [  17行] fill(get_by_placeholder('工号')) <- 'E001'
  5. [  18行] fill(get_by_placeholder('姓名')) <- '李四'
  6. [  19行] select_option(locator('#dept-select')) <- ['技术部']
  7. [  20行] fill(locator("input[type='date']")) <- '2024-01-01'
  8. [  23行] set_input_files(get_by_label('上传简历')) <- 'resume.pdf'
  9. [  26行] press(get_by_placeholder('备注')) <- 'Control+A'
  10. [  27行] press(get_by_placeholder('备注')) <- 'Delete'

🎯 定位器类型分布:
  - get_by_text: 3次
  - get_by_placeholder: 4次
  - locator: 2次
  - get_by_label: 1次

💡 参数化建议:
  - 发现多个导航文本，建议创建导航配置字典
  - 发现文件上传操作，建议将文件路径参数化
```

---

## 💡 高级功能

### 1. 自定义分析逻辑

```python
from playwright_variable_extractor_enhanced import EnhancedPlaywrightExtractor
import ast

class CustomExtractor(EnhancedPlaywrightExtractor):
    """自定义提取器，扩展特定业务逻辑"""

    def visit_Call(self, node: ast.Call):
        # 调用父类方法
        super().visit_Call(node)

        # 添加自定义逻辑
        call_name = self._get_call_name(node.func)
        if call_name == 'my_custom_method':
            # 处理自定义方法
            pass

# 使用自定义提取器
with open('script.py', 'r') as f:
    content = f.read()

tree = ast.parse(content)
extractor = CustomExtractor(content)
extractor.visit(tree)
data = extractor.data
```

### 2. 批量分析多个脚本

```python
from pathlib import Path
from playwright_variable_extractor_enhanced import PlaywrightAnalyzer

def batch_analyze(script_dir: str, output_dir: str):
    """批量分析目录下的所有Playwright脚本"""
    script_path = Path(script_dir)
    output_path = Path(output_dir)

    # 查找所有Python脚本
    scripts = list(script_path.glob('**/*.py'))

    print(f"找到 {len(scripts)} 个脚本文件")

    for script in scripts:
        print(f"\n正在分析: {script}")
        try:
            analyzer = PlaywrightAnalyzer(str(script))
            data = analyzer.analyze()

            # 为每个脚本创建单独的输出目录
            script_output = output_path / script.stem
            script_output.mkdir(parents=True, exist_ok=True)

            analyzer.save_analysis_results(str(script_output))
            print(f"✅ 完成: {script.name}")
        except Exception as e:
            print(f"❌ 失败: {script.name} - {e}")

# 使用示例
batch_analyze('./playwright_scripts', './batch_analysis')
```

### 3. 生成测试数据工厂

```python
def generate_test_data_factory(data: ExtractedData) -> str:
    """基于提取的数据生成测试数据工厂类"""

    factory_code = []
    factory_code.append("class TestDataFactory:")
    factory_code.append('    """自动生成的测试数据工厂"""')
    factory_code.append("")

    # 为每个表单字段生成默认数据
    for i, (locator, value) in enumerate(data.form_fills.items(), 1):
        field_name = f"field_{i}"
        factory_code.append(f"    @staticmethod")
        factory_code.append(f"    def get_{field_name}_data():")
        factory_code.append(f'        """获取{locator}的测试数据"""')
        factory_code.append(f"        return '{value}'")
        factory_code.append("")

    return '\n'.join(factory_code)

# 使用
from playwright_variable_extractor_enhanced import analyze_playwright_script
data = analyze_playwright_script('script.py')
factory_code = generate_test_data_factory(data)
print(factory_code)
```

### 4. 集成到CI/CD

```yaml
# .github/workflows/analyze_playwright.yml
name: Analyze Playwright Scripts

on:
  pull_request:
    paths:
      - 'tests/**/*.py'

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'

      - name: Analyze Playwright scripts
        run: |
          python playwright_variable_extractor_enhanced.py tests/e2e/test_*.py ./analysis

      - name: Upload analysis results
        uses: actions/upload-artifact@v2
        with:
          name: playwright-analysis
          path: ./analysis
```

---

## 📊 数据结构说明

### LocatorInfo
```python
@dataclass
class LocatorInfo:
    type: str          # 定位器类型
    value: str         # 定位器值
    line: int          # 代码行号
    context: str       # 代码上下文
    operation: str     # 后续操作
    operation_value: str  # 操作值
```

### ActionInfo
```python
@dataclass
class ActionInfo:
    action_type: str      # 操作类型
    target: str           # 目标元素
    value: Optional[str]  # 操作值
    line: int             # 行号
    locator_type: str     # 定位器类型
    locator_value: str    # 定位器值
```

### ExtractedData
```python
@dataclass
class ExtractedData:
    url: Optional[str]                    # 主URL
    urls: List[str]                       # 所有URL
    locators: List[LocatorInfo]           # 所有定位器
    actions: List[ActionInfo]             # 所有操作
    form_fills: Dict[str, str]            # 表单填充
    form_selects: Dict[str, List[str]]    # 下拉选择
    uploaded_files: List[str]             # 上传文件
    clicked_elements: List[str]           # 点击元素
    assertions: List[Dict[str, Any]]      # 断言
    waits: List[Dict[str, Any]]           # 等待
    keyboard_inputs: List[str]            # 键盘输入
    regex_patterns: List[str]             # 正则模式
    variables: Dict[str, str]             # 变量
    navigation_texts: Set[str]            # 导航文本
```

---

## 🔧 故障排除

### 1. 语法错误

**问题**: `SyntaxError: invalid syntax`

**解决方案**: 确保Playwright脚本语法正确，可以先运行脚本验证。

### 2. 提取不完整

**问题**: 某些定位器或操作没有被提取

**解决方案**:
- 检查是否使用了非标准的Playwright API
- 查看`LOCATOR_METHODS`和`ACTION_METHODS`列表，确认方法是否支持
- 可以扩展`EnhancedPlaywrightExtractor`类添加自定义支持

### 3. 编码问题

**问题**: `UnicodeDecodeError`

**解决方案**: 确保脚本文件使用UTF-8编码保存。

### 4. 文件路径问题

**问题**: `FileNotFoundError`

**解决方案**:
- 使用绝对路径
- 确认文件确实存在
- 检查文件权限

---

## 🎓 最佳实践

### 1. Codegen生成高质量脚本

```bash
# 使用有意义的操作，便于后续识别
playwright codegen --target python \
  --viewport-size=1920,1080 \
  https://example.com
```

### 2. 为关键元素添加test-id

```html
<!-- 在页面中添加test-id -->
<button data-testid="submit-button">提交</button>
```

```python
# 在Playwright中使用
page.get_by_test_id("submit-button").click()
```

这样提取器能生成更稳定的定位器。

### 3. 组织脚本结构

```python
# 推荐的脚本结构
def setup(page):
    """初始化设置"""
    page.goto(BASE_URL)

def login(page, username, password):
    """登录流程"""
    page.get_by_placeholder("用户名").fill(username)
    page.get_by_placeholder("密码").fill(password)
    page.get_by_role("button", name="登录").click()

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        setup(page)
        login(page, "user", "pass")
        browser.close()
```

提取器能更好地识别模块化的代码。

### 4. 添加注释辅助分析

```python
# 登录流程开始
page.get_by_placeholder("用户名").fill("admin")  # 填充用户名
page.get_by_placeholder("密码").fill("pass")     # 填充密码
page.get_by_role("button", name="登录").click()  # 点击登录按钮
# 登录流程结束
```

### 5. 定期更新分析结果

```bash
# 创建定期分析脚本
#!/bin/bash
python playwright_variable_extractor_enhanced.py \
  tests/e2e/all_tests.py \
  ./docs/test_analysis \
  && echo "✅ 分析完成: $(date)" >> analysis.log
```

---

## 📚 扩展阅读

- [Playwright官方文档](https://playwright.dev/)
- [Robot Framework Browser库](https://marketsquare.github.io/robotframework-browser/)
- [Python AST官方文档](https://docs.python.org/3/library/ast.html)

---

## 🤝 贡献与反馈

如有问题或建议，欢迎反馈！

---

## 📄 许可证

MIT License

---

**最后更新**: 2025-11-05
