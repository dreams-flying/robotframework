*** Settings ***
Library    SeleniumLibrary

*** Keywords ***
Click Date By JavaScript Enhanced
    [Arguments]    ${day_number}
    [Documentation]    增强版日期点击 - 带完整调试和多重备选方案

    # 步骤 1: 先进行诊断
    ${diagnostic_result}=    Diagnose Date Picker    ${day_number}
    Log To Console    ${diagnostic_result}

    # 步骤 2: 尝试 JavaScript 点击（改进版）
    ${js_result}=    Execute Javascript
    ...    // ========== 调试模式 ==========
    ...    console.log('='.repeat(60));
    ...    console.log('🔍 开始执行日期点击 - 增强调试版');
    ...    console.log('='.repeat(60));
    ...
    ...    var day = arguments[0];
    ...    console.log('📅 目标日期:', day);
    ...
    ...    // ========== 1. 查找可见的日历容器 ==========
    ...    var calendarContainers = Array.from(document.querySelectorAll('.datetimepicker, .datepicker, [class*="date-picker"]'));
    ...    console.log('📦 找到日历容器数量:', calendarContainers.length);
    ...
    ...    var visibleCalendar = calendarContainers.find(function(cal) {
    ...        return cal.offsetParent !== null &&
    ...               window.getComputedStyle(cal).display !== 'none' &&
    ...               window.getComputedStyle(cal).visibility !== 'hidden';
    ...    });
    ...
    ...    if (!visibleCalendar) {
    ...        console.error('❌ 未找到可见的日历容器');
    ...        return {success: false, error: '未找到可见的日历容器', step: 1};
    ...    }
    ...    console.log('✅ 找到可见日历容器');
    ...
    ...    // ========== 2. 解析日历标题月份 ==========
    ...    var currentSystemMonth = new Date().getMonth() + 1;
    ...    var calendarDisplayMonth = null;
    ...
    ...    var titleSelectors = [
    ...        '.switch',
    ...        '.datepicker-switch',
    ...        '.datetimepicker-months th',
    ...        'th[colspan]',
    ...        '.picker-switch'
    ...    ];
    ...
    ...    var titleEl = null;
    ...    for (var i = 0; i < titleSelectors.length; i++) {
    ...        titleEl = visibleCalendar.querySelector(titleSelectors[i]);
    ...        if (titleEl) {
    ...            console.log('✅ 找到标题元素，使用选择器:', titleSelectors[i]);
    ...            break;
    ...        }
    ...    }
    ...
    ...    if (titleEl) {
    ...        var titleText = titleEl.textContent.trim();
    ...        console.log('📋 日历标题:', titleText);
    ...
    ...        // 月份映射
    ...        var monthMap = {
    ...            '一月': 1, '二月': 2, '三月': 3, '四月': 4, '五月': 5, '六月': 6,
    ...            '七月': 7, '八月': 8, '九月': 9, '十月': 10, '十一月': 11, '十二月': 12,
    ...            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
    ...            'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12,
    ...            'January': 1, 'February': 2, 'March': 3, 'April': 4, 'June': 6,
    ...            'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
    ...        };
    ...
    ...        // 尝试多种解析方式
    ...        var match1 = titleText.match(/(\d{4})[年\-/\s\.]*(\d{1,2})/);
    ...        if (match1 && match1[2]) {
    ...            calendarDisplayMonth = parseInt(match1[2], 10);
    ...            console.log('✅ 解析月份 (格式1):', calendarDisplayMonth);
    ...        } else {
    ...            var match2 = titleText.match(/(\d{1,2})[\-/\s\.]*(\d{4})/);
    ...            if (match2 && match2[1]) {
    ...                calendarDisplayMonth = parseInt(match2[1], 10);
    ...                console.log('✅ 解析月份 (格式2):', calendarDisplayMonth);
    ...            } else {
    ...                for (var name in monthMap) {
    ...                    if (titleText.includes(name)) {
    ...                        calendarDisplayMonth = monthMap[name];
    ...                        console.log('✅ 解析月份 (名称):', name, '->', calendarDisplayMonth);
    ...                        break;
    ...                    }
    ...                }
    ...            }
    ...        }
    ...    } else {
    ...        console.warn('⚠️ 未找到日历标题元素');
    ...    }
    ...
    ...    console.log('📊 系统月份:', currentSystemMonth, ', 日历月份:', calendarDisplayMonth);
    ...
    ...    // ========== 3. 查找日期元素（多种选择器）==========
    ...    var dateSelectors = [
    ...        "td.day:not(.new):not(.old)",
    ...        "td.day:not(.disabled)",
    ...        "td[class*='day']:not([class*='old']):not([class*='new'])",
    ...        "td.day",
    ...        "[data-day]",
    ...        ".datepicker-days td"
    ...    ];
    ...
    ...    var allDayElements = [];
    ...    for (var s = 0; s < dateSelectors.length; s++) {
    ...        var elements = Array.from(visibleCalendar.querySelectorAll(dateSelectors[s]));
    ...        if (elements.length > 0) {
    ...            console.log('✅ 使用选择器:', dateSelectors[s], ', 找到元素数:', elements.length);
    ...            allDayElements = elements;
    ...            break;
    ...        }
    ...    }
    ...
    ...    if (allDayElements.length === 0) {
    ...        console.error('❌ 未找到任何日期元素');
    ...        return {success: false, error: '未找到任何日期元素', step: 3};
    ...    }
    ...
    ...    // 过滤匹配的日期和可见的元素
    ...    var matchingDays = allDayElements.filter(function(el) {
    ...        var text = el.textContent.trim();
    ...        var isMatch = text === String(day);
    ...
    ...        if (isMatch) {
    ...            var isVisible = el.offsetParent !== null &&
    ...                           el.offsetWidth > 0 &&
    ...                           el.offsetHeight > 0;
    ...            var style = window.getComputedStyle(el);
    ...            isVisible = isVisible &&
    ...                       style.display !== 'none' &&
    ...                       style.visibility !== 'hidden' &&
    ...                       parseFloat(style.opacity) > 0;
    ...
    ...            console.log('🔍 日期元素:', text,
    ...                       ', 类名:', el.className,
    ...                       ', 可见:', isVisible,
    ...                       ', offsetParent:', el.offsetParent !== null,
    ...                       ', display:', style.display,
    ...                       ', visibility:', style.visibility,
    ...                       ', opacity:', style.opacity);
    ...
    ...            return isVisible;
    ...        }
    ...        return false;
    ...    });
    ...
    ...    console.log('📊 找到匹配且可见的日期元素数量:', matchingDays.length);
    ...
    ...    if (matchingDays.length === 0) {
    ...        console.error('❌ 未找到可见的日期:', day);
    ...        return {success: false, error: '未找到可见的日期: ' + day, step: 3};
    ...    }
    ...
    ...    // ========== 4. 智能选择目标元素 ==========
    ...    var target;
    ...    if (calendarDisplayMonth === null) {
    ...        console.log('⚠️ 月份解析失败，默认选择第一个');
    ...        target = matchingDays[0];
    ...    } else if (currentSystemMonth === calendarDisplayMonth) {
    ...        console.log('✅ 月份一致，选择第一个');
    ...        target = matchingDays[0];
    ...    } else {
    ...        console.log('✅ 月份不一致，选择第', matchingDays.length > 1 ? '二' : '一', '个');
    ...        target = matchingDays.length > 1 ? matchingDays[1] : matchingDays[0];
    ...    }
    ...
    ...    console.log('🎯 选中的元素:', target.textContent, ', 类名:', target.className);
    ...
    ...    // ========== 5. 执行点击（多种策略）==========
    ...    try {
    ...        // 5.1 滚动到可见区域
    ...        target.scrollIntoView({block: 'center', behavior: 'auto'});
    ...        console.log('✅ 已滚动到元素');
    ...
    ...        // 5.2 添加高亮（调试用）
    ...        var originalBg = target.style.backgroundColor;
    ...        var originalBorder = target.style.border;
    ...        target.style.backgroundColor = 'yellow';
    ...        target.style.border = '3px solid red';
    ...        console.log('✅ 已高亮元素（3秒后恢复）');
    ...
    ...        // 5.3 策略1: 标准事件
    ...        var clickEvents = ['mousedown', 'mouseup', 'click'];
    ...        for (var e = 0; e < clickEvents.length; e++) {
    ...            target.dispatchEvent(new MouseEvent(clickEvents[e], {
    ...                bubbles: true,
    ...                cancelable: true,
    ...                view: window
    ...            }));
    ...        }
    ...        console.log('✅ 已触发鼠标事件');
    ...
    ...        // 5.4 策略2: 输入事件
    ...        ['input', 'change'].forEach(function(eventType) {
    ...            target.dispatchEvent(new Event(eventType, {bubbles: true}));
    ...        });
    ...        console.log('✅ 已触发输入事件');
    ...
    ...        // 5.5 策略3: 焦点事件
    ...        target.focus();
    ...        console.log('✅ 已设置焦点');
    ...
    ...        // 5.6 恢复样式
    ...        setTimeout(function() {
    ...            target.style.backgroundColor = originalBg;
    ...            target.style.border = originalBorder;
    ...        }, 3000);
    ...
    ...        console.log('='.repeat(60));
    ...        console.log('✅ 点击执行完成');
    ...        console.log('='.repeat(60));
    ...
    ...        return {
    ...            success: true,
    ...            selectedDay: day,
    ...            selectedElement: target.className,
    ...            totalVisible: matchingDays.length,
    ...            calendarMonth: calendarDisplayMonth,
    ...            systemMonth: currentSystemMonth
    ...        };
    ...
    ...    } catch (e) {
    ...        console.error('❌ 点击执行失败:', e);
    ...        return {success: false, error: e.message, step: 5};
    ...    }
    ...    ARGUMENTS    ${day_number}

    # 检查结果
    Log To Console    \n执行结果: ${js_result}

    ${success}=    Get From Dictionary    ${js_result}    success
    Run Keyword If    not ${success}    Handle Click Failure    ${js_result}    ${day_number}

    # 等待日期选择生效
    Sleep    500ms

    Log To Console    ✅ JavaScript 点击成功


Diagnose Date Picker
    [Arguments]    ${day_number}
    [Documentation]    诊断日期选择器的状态

    ${diagnostic}=    Execute Javascript
    ...    var day = arguments[0];
    ...    var report = [];
    ...    report.push('='.repeat(60));
    ...    report.push('📋 日期选择器诊断报告');
    ...    report.push('='.repeat(60));
    ...    report.push('');
    ...
    ...    // 1. 检查页面是否加载完成
    ...    report.push('1. 页面状态:');
    ...    report.push('   - 加载状态: ' + document.readyState);
    ...    report.push('   - 标题: ' + document.title);
    ...    report.push('');
    ...
    ...    // 2. 查找日历容器
    ...    report.push('2. 日历容器:');
    ...    var containers = document.querySelectorAll('.datetimepicker, .datepicker, [class*="date"]');
    ...    report.push('   - 总数: ' + containers.length);
    ...
    ...    Array.from(containers).forEach(function(c, i) {
    ...        var style = window.getComputedStyle(c);
    ...        report.push('   - 容器' + (i+1) + ':');
    ...        report.push('     类名: ' + c.className);
    ...        report.push('     display: ' + style.display);
    ...        report.push('     visibility: ' + style.visibility);
    ...        report.push('     offsetParent: ' + (c.offsetParent !== null));
    ...    });
    ...    report.push('');
    ...
    ...    // 3. 查找日期元素
    ...    report.push('3. 日期元素:');
    ...    var dayElements = document.querySelectorAll('td.day, td[class*="day"], [data-day]');
    ...    report.push('   - 总数: ' + dayElements.length);
    ...
    ...    var matchingDays = Array.from(dayElements).filter(function(el) {
    ...        return el.textContent.trim() === String(day);
    ...    });
    ...    report.push('   - 匹配日期 "' + day + '" 的元素数: ' + matchingDays.length);
    ...
    ...    matchingDays.forEach(function(el, i) {
    ...        var style = window.getComputedStyle(el);
    ...        report.push('   - 元素' + (i+1) + ':');
    ...        report.push('     类名: ' + el.className);
    ...        report.push('     文本: ' + el.textContent.trim());
    ...        report.push('     display: ' + style.display);
    ...        report.push('     visibility: ' + style.visibility);
    ...        report.push('     opacity: ' + style.opacity);
    ...        report.push('     offsetParent: ' + (el.offsetParent !== null));
    ...        report.push('     offsetWidth: ' + el.offsetWidth);
    ...        report.push('     offsetHeight: ' + el.offsetHeight);
    ...    });
    ...    report.push('');
    ...
    ...    // 4. 查找标题
    ...    report.push('4. 日历标题:');
    ...    var titleSelectors = ['.switch', '.datepicker-switch', 'th[colspan]'];
    ...    var foundTitle = false;
    ...    titleSelectors.forEach(function(sel) {
    ...        var title = document.querySelector(sel);
    ...        if (title) {
    ...            report.push('   - 选择器: ' + sel);
    ...            report.push('   - 文本: ' + title.textContent.trim());
    ...            foundTitle = true;
    ...        }
    ...    });
    ...    if (!foundTitle) {
    ...        report.push('   - ⚠️ 未找到标题元素');
    ...    }
    ...    report.push('');
    ...
    ...    report.push('='.repeat(60));
    ...    return report.join('\n');
    ...    ARGUMENTS    ${day_number}

    [Return]    ${diagnostic}


Handle Click Failure
    [Arguments]    ${result}    ${day_number}
    [Documentation]    处理点击失败的情况

    ${error}=    Get From Dictionary    ${result}    error
    ${step}=    Get From Dictionary    ${result}    step    default=unknown

    Log To Console    \n❌ JavaScript 点击失败
    Log To Console    错误信息: ${error}
    Log To Console    失败步骤: ${step}

    # 尝试备选方案
    Log To Console    \n🔄 尝试备选方案...

    # 备选方案 1: Selenium 原生点击
    ${selenium_result}=    Run Keyword And Return Status    Click Date By Selenium    ${day_number}
    Run Keyword If    ${selenium_result}    Return From Keyword

    # 备选方案 2: 强制 JavaScript 点击（忽略可见性）
    ${force_result}=    Run Keyword And Return Status    Click Date By Force    ${day_number}
    Run Keyword If    ${force_result}    Return From Keyword

    # 所有方案都失败
    Fail    所有日期点击方案都失败了。请检查页面元素。


Click Date By Selenium
    [Arguments]    ${day_number}
    [Documentation]    使用 Selenium 原生方法点击日期

    Log To Console    \n📍 尝试 Selenium 原生点击...

    # 查找所有匹配的日期元素
    ${locator}=    Set Variable    xpath=//td[contains(@class, 'day') and not(contains(@class, 'old')) and not(contains(@class, 'new')) and text()='${day_number}']

    ${count}=    Get Element Count    ${locator}
    Log To Console    找到 ${count} 个匹配元素

    Run Keyword If    ${count} == 0    Fail    未找到日期元素

    # 获取系统月份
    ${current_month}=    Evaluate    __import__('datetime').datetime.now().month

    # 获取日历显示月份
    ${calendar_month}=    Run Keyword And Return Status
    ...    Page Should Contain Element    xpath=//th[@class='switch']

    # 根据月份选择元素
    Run Keyword If    ${count} == 1
    ...    Click Element    ${locator}
    ...    ELSE
    ...    Click Element    ${locator}[1]    # 默认点第一个

    Sleep    300ms
    Log To Console    ✅ Selenium 点击成功


Click Date By Force
    [Arguments]    ${day_number}
    [Documentation]    强制点击（忽略可见性检查）

    Log To Console    \n⚡ 尝试强制点击...

    ${result}=    Execute Javascript
    ...    var day = arguments[0];
    ...    var xpath = "//td[contains(@class, 'day') and text()='" + day + "']";
    ...    var iterator = document.evaluate(xpath, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
    ...
    ...    if (iterator.snapshotLength === 0) {
    ...        return false;
    ...    }
    ...
    ...    var target = iterator.snapshotItem(0);
    ...    target.scrollIntoView({block: 'center'});
    ...    target.click();
    ...    target.dispatchEvent(new Event('change', {bubbles: true}));
    ...
    ...    return true;
    ...    ARGUMENTS    ${day_number}

    Run Keyword If    not ${result}    Fail    强制点击也失败了

    Sleep    300ms
    Log To Console    ✅ 强制点击成功
