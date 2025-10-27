*** Settings ***
Library    SeleniumLibrary
Library    String

*** Keywords ***
Click Tree Node Expand By Data PID
    [Documentation]    使用 data-pid 精确点击树节点的展开图标
    ...                这是最可靠的方法，因为 data-pid 对每个节点是唯一的
    [Arguments]    ${data_pid}

    # 使用 data-pid 精确定位展开图标
    ${expand_icon}=    Set Variable    xpath=//span[@data-pid='${data_pid}' and contains(@class, 'jtree_expand')]

    # 等待元素可见
    Wait Until Element Is Visible    ${expand_icon}    timeout=10s

    # 检查节点状态 - 只有关闭状态才需要点击
    ${class_attr}=    Get Element Attribute    ${expand_icon}    class
    ${is_closed}=    Run Keyword And Return Status    Should Contain    ${class_attr}    jtree_node_close

    # 如果节点是关闭状态，点击展开
    Run Keyword If    ${is_closed}    Click Element    ${expand_icon}
    Run Keyword If    ${is_closed}    Sleep    1s

    # 返回节点是否被展开
    [Return]    ${is_closed}

Click Tree Node Label By Data PID
    [Documentation]    点击树节点的标签（选中该节点）
    [Arguments]    ${data_pid}

    # 定位标签元素 - 标签通常是展开图标的兄弟元素
    ${label_locator}=    Set Variable    xpath=//span[@data-pid='${data_pid}']/following-sibling::label

    # 等待并点击
    Wait Until Element Is Visible    ${label_locator}    timeout=10s
    Click Element    ${label_locator}
    Sleep    0.5s

Select Tree Node By Path With Data PIDs
    [Documentation]    按照路径依次展开并选择树节点
    ...                data_pid_path: 从根到目标节点的 data-pid 列表
    ...                例如: ['0102000000', '0102000008', '0102000008001']
    [Arguments]    ${data_pid_path}

    # 依次展开每一级（除了最后一个）
    ${path_length}=    Get Length    ${data_pid_path}
    ${last_index}=    Evaluate    ${path_length} - 1

    FOR    ${index}    IN RANGE    ${last_index}
        ${pid}=    Get From List    ${data_pid_path}    ${index}
        Log    展开节点: ${pid}
        Click Tree Node Expand By Data PID    ${pid}
    END

    # 选择最后一个节点
    ${target_pid}=    Get From List    ${data_pid_path}    ${last_index}
    Log    选择节点: ${target_pid}
    Click Tree Node Label By Data PID    ${target_pid}

Get All Tree Node Data PIDs With Text
    [Documentation]    获取所有树节点的 data-pid 和文本（调试用）
    ...                返回: 字典列表 [{'pid': '...', 'text': '...'}, ...]

    ${js_code}=    Catenate    SEPARATOR=\n
    ...    var nodes = document.querySelectorAll('span[data-pid]');
    ...    var result = [];
    ...    nodes.forEach(function(el) {
    ...        var pid = el.getAttribute('data-pid');
    ...        var parentLi = el.closest('li');
    ...        var text = parentLi ? parentLi.textContent.trim().split('\\n')[0].trim() : 'N/A';
    ...        result.push({pid: pid, text: text});
    ...    });
    ...    return result;

    ${result}=    Execute Javascript    ${js_code}
    [Return]    ${result}

Find Tree Node Data PID By Text
    [Documentation]    根据节点文本查找对应的 data-pid（调试用）
    [Arguments]    ${search_text}

    ${js_code}=    Catenate    SEPARATOR=\n
    ...    var searchText = arguments[0];
    ...    var nodes = document.querySelectorAll('span[data-pid]');
    ...    var matches = [];
    ...    nodes.forEach(function(el) {
    ...        var parentLi = el.closest('li');
    ...        var text = parentLi ? parentLi.textContent.trim() : '';
    ...        if (text.indexOf(searchText) !== -1) {
    ...            var pid = el.getAttribute('data-pid');
    ...            matches.push({pid: pid, text: text.split('\\n')[0].trim()});
    ...        }
    ...    });
    ...    return matches;

    ${result}=    Execute Javascript    ${js_code}    ${search_text}
    [Return]    ${result}

*** Test Cases ***
示例1：使用 data-pid 选择单个成本中心
    [Documentation]    最简单的场景 - 已知目标节点的 data-pid
    Open Browser    http://your-url.com    chrome
    # ... 登录和导航到成本中心选择页面 ...

    # 点击"选择成本中心"按钮打开树
    Click Element    xpath=//button[contains(., '选择成本中心')]
    Sleep    1s

    # 直接使用 data-pid 选择节点
    Click Tree Node Expand By Data PID    0102000008
    Click Tree Node Label By Data PID    0102000008

    [Teardown]    Close Browser

示例2：使用路径选择多级成本中心
    [Documentation]    需要展开多级节点的场景
    Open Browser    http://your-url.com    chrome
    # ... 登录和导航 ...

    Click Element    xpath=//button[contains(., '选择成本中心')]
    Sleep    1s

    # 按照层级路径选择
    # 假设路径是: 一级部门(0102000000) -> 技术与大数据平台部(0102000008) -> 某子部门(0102000008001)
    ${path}=    Create List    0102000000    0102000008    0102000008001
    Select Tree Node By Path With Data PIDs    ${path}

    [Teardown]    Close Browser

示例3：调试 - 查找节点的 data-pid
    [Documentation]    当不知道 data-pid 时，使用此测试用例查找
    Open Browser    http://your-url.com    chrome
    # ... 登录和导航 ...

    Click Element    xpath=//button[contains(., '选择成本中心')]
    Sleep    2s

    # 搜索包含"技术与大数据平台部"的节点
    ${matches}=    Find Tree Node Data PID By Text    技术与大数据平台部

    # 打印结果
    Log    找到 ${matches} 个匹配项    console=True
    FOR    ${match}    IN    @{matches}
        Log    PID: ${match}[pid], 文本: ${match}[text]    console=True
    END

    # 或者列出所有节点
    ${all_nodes}=    Get All Tree Node Data PIDs With Text
    Log    总共 ${all_nodes} 个节点    console=True

    [Teardown]    Close Browser

*** Comments ***
# ============================================================================
# 使用说明
# ============================================================================
#
# 问题原因：
# - 之前使用文本定位 //li[contains(.,'技术与大数据平台部')]//span 会匹配到 23 个元素
# - 因为 contains(.) 会匹配该节点及其所有子孙节点的文本
#
# 解决方案：
# - 使用 data-pid 属性，它对每个树节点是唯一的
# - data-pid="0102000008" 只会匹配到一个元素
#
# 如何获取 data-pid：
# 方法1: 在浏览器开发者工具中：
#   - 右键点击目标节点 -> 检查
#   - 查看 <span> 元素的 data-pid 属性
#
# 方法2: 在 Console 中运行 debug_tree_nodes.js 脚本：
#   - findNodeByText("技术与大数据平台部")
#   - 会列出所有匹配节点的 data-pid
#
# 方法3: 在 Robot Framework 中运行"示例3"测试用例
#
# 注意事项：
# - data-pid 可能在不同环境中不同（开发/测试/生产）
# - 如果 data-pid 会变化，考虑在测试开始时动态获取
# - jtree_node_close = 节点关闭（未展开）
# - jtree_node_open = 节点打开（已展开）
