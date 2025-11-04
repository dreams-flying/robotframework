#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI Automation Recorder - Super Enhanced Version
超级增强版：高级定位器 + 完整键盘识别

新增功能：
1. 10+ 种定位器策略（XPath、正则、索引、相对路径等）
2. 定位器稳定性评分系统
3. 智能定位器选择算法
4. 完整键盘操作识别（单键、组合键、功能键）
5. 快捷键序列识别
6. 定位器可视化比较
7. 元素层级关系定位

依赖安装：
pip install uiautomation PyQt5 pynput pyperclip pillow
"""

import sys
import time
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QTextEdit, QLabel,
                             QSplitter, QGroupBox, QCheckBox, QSpinBox,
                             QFileDialog, QMessageBox, QListWidget, QComboBox,
                             QTabWidget, QTableWidget, QTableWidgetItem)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor

import uiautomation as auto
from pynput import mouse, keyboard
import pyperclip
import re


class AdvancedLocatorGenerator:
    """高级定位器生成器"""

    @staticmethod
    def generate_all_locators(props: dict, element=None) -> list:
        """生成所有可能的定位器（带稳定性评分）"""
        locators = []

        # 策略 1: AutomationId（稳定性最高）
        if props.get('AutomationId'):
            locators.append({
                'strategy': 'AutomationId',
                'code': f"AutomationId='{props['AutomationId']}'",
                'params': {'AutomationId': props['AutomationId']},
                'stability': 95,  # 稳定性评分 0-100
                'speed': 90,  # 查找速度评分
                'description': '最稳定的定位方式（ID通常不变）'
            })

        # 策略 2: Name（稳定性高）
        if props.get('Name'):
            name = props['Name'].replace("'", "\\'")
            locators.append({
                'strategy': 'Name',
                'code': f"Name='{name}'",
                'params': {'Name': name},
                'stability': 80,
                'speed': 85,
                'description': '使用元素名称定位'
            })

        # 策略 3: Name + ControlType（稳定性很高）
        if props.get('Name') and props.get('ControlType'):
            name = props['Name'].replace("'", "\\'")
            control_type = props['ControlType']
            locators.append({
                'strategy': 'Name+ControlType',
                'code': f"Name='{name}', ControlType=auto.ControlType.{control_type}Control",
                'params': {
                    'Name': name,
                    'ControlType': f"auto.ControlType.{control_type}Control"
                },
                'stability': 90,
                'speed': 85,
                'description': '名称+控件类型组合定位'
            })

        # 策略 4: ClassName + ControlType
        if props.get('ClassName') and props.get('ControlType'):
            locators.append({
                'strategy': 'ClassName+ControlType',
                'code': f"ClassName='{props['ClassName']}', ControlType=auto.ControlType.{props['ControlType']}Control",
                'params': {
                    'ClassName': props['ClassName'],
                    'ControlType': f"auto.ControlType.{props['ControlType']}Control"
                },
                'stability': 70,
                'speed': 80,
                'description': '类名+控件类型组合定位'
            })

        # 策略 5: Name 正则匹配
        if props.get('Name'):
            name = props['Name'].replace("'", "\\'")
            locators.append({
                'strategy': 'Name_Regex',
                'code': f"Name=RegexPattern('{name}')",
                'params': {'Name': f"RegexPattern('{name}')"},
                'stability': 75,
                'speed': 70,
                'description': '名称正则表达式匹配（支持模糊匹配）',
                'note': '需要自定义 RegexPattern 函数'
            })

        # 策略 6: 部分名称匹配（Contains）
        if props.get('Name') and len(props['Name']) > 5:
            name_part = props['Name'][:min(10, len(props['Name']))]
            locators.append({
                'strategy': 'Name_Contains',
                'code': f"searchDepth=1, foundIndex=1, Name匹配='{name_part}...'",
                'params': {'Name': name_part},
                'stability': 65,
                'speed': 60,
                'description': '部分名称匹配（适合动态名称）',
                'note': '需要遍历查找包含该字符串的元素'
            })

        # 策略 7: 仅 ControlType（稳定性最低）
        if props.get('ControlType'):
            locators.append({
                'strategy': 'ControlType_Only',
                'code': f"ControlType=auto.ControlType.{props['ControlType']}Control",
                'params': {
                    'ControlType': f"auto.ControlType.{props['ControlType']}Control"
                },
                'stability': 40,
                'speed': 90,
                'description': '仅控件类型定位（最不推荐，可能匹配多个）'
            })

        # 策略 8: 索引定位（当有多个相同元素时）
        if props.get('ClassName'):
            locators.append({
                'strategy': 'Index',
                'code': f"ClassName='{props['ClassName']}', foundIndex=1",
                'params': {
                    'ClassName': props['ClassName'],
                    'foundIndex': 1
                },
                'stability': 50,
                'speed': 75,
                'description': '索引定位（第N个匹配的元素）',
                'note': '需要指定 foundIndex 参数'
            })

        # 策略 9: 相对路径定位（父子关系）
        locators.append({
            'strategy': 'RelativePath',
            'code': f"# parent.child_window(Name='{props.get('Name', 'element')}')",
            'params': {},
            'stability': 85,
            'speed': 80,
            'description': '通过父元素定位子元素（推荐）',
            'note': '需要先定位父元素'
        })

        # 策略 10: XPath 风格（深度优先）
        if props.get('ClassName'):
            locators.append({
                'strategy': 'XPath_Style',
                'code': f"# 类似 XPath: //Window/Pane/{props['ControlType']}[@Name='{props.get('Name', '')}']",
                'params': {},
                'stability': 75,
                'speed': 60,
                'description': 'XPath 风格路径定位',
                'note': '需要自定义实现 XPath 解析器'
            })

        # 按稳定性排序
        locators.sort(key=lambda x: x['stability'], reverse=True)

        return locators

    @staticmethod
    def select_best_locators(locators: list, count: int = 3) -> list:
        """选择最佳的 N 个定位器"""
        # 过滤掉需要自定义实现的策略
        valid_locators = [loc for loc in locators if 'note' not in loc or 'foundIndex' not in str(loc.get('params', {}))]

        # 综合评分：稳定性 * 0.7 + 速度 * 0.3
        for loc in valid_locators:
            loc['score'] = loc['stability'] * 0.7 + loc['speed'] * 0.3

        # 排序并返回前 N 个
        valid_locators.sort(key=lambda x: x['score'], reverse=True)
        return valid_locators[:count]


class KeyboardRecognizer:
    """键盘操作识别器"""

    # 特殊键映射
    SPECIAL_KEYS = {
        keyboard.Key.enter: ('Enter', '{ENTER}'),
        keyboard.Key.tab: ('Tab', '{TAB}'),
        keyboard.Key.esc: ('Esc', '{ESC}'),
        keyboard.Key.space: ('Space', ' '),
        keyboard.Key.backspace: ('Backspace', '{BACKSPACE}'),
        keyboard.Key.delete: ('Delete', '{DELETE}'),
        keyboard.Key.home: ('Home', '{HOME}'),
        keyboard.Key.end: ('End', '{END}'),
        keyboard.Key.page_up: ('PageUp', '{PGUP}'),
        keyboard.Key.page_down: ('PageDown', '{PGDN}'),
        keyboard.Key.up: ('Up', '{UP}'),
        keyboard.Key.down: ('Down', '{DOWN}'),
        keyboard.Key.left: ('Left', '{LEFT}'),
        keyboard.Key.right: ('Right', '{RIGHT}'),
        keyboard.Key.insert: ('Insert', '{INSERT}'),
        keyboard.Key.f1: ('F1', '{F1}'),
        keyboard.Key.f2: ('F2', '{F2}'),
        keyboard.Key.f3: ('F3', '{F3}'),
        keyboard.Key.f4: ('F4', '{F4}'),
        keyboard.Key.f5: ('F5', '{F5}'),
        keyboard.Key.f6: ('F6', '{F6}'),
        keyboard.Key.f7: ('F7', '{F7}'),
        keyboard.Key.f8: ('F8', '{F8}'),
        keyboard.Key.f9: ('F9', '{F9}'),
        keyboard.Key.f10: ('F10', '{F10}'),
        keyboard.Key.f11: ('F11', '{F11}'),
        keyboard.Key.f12: ('F12', '{F12}'),
    }

    def __init__(self):
        self.pressed_keys = set()
        self.current_modifiers = set()

    def on_key_press(self, key):
        """按键按下"""
        self.pressed_keys.add(key)

        # 记录修饰键
        if key in [keyboard.Key.ctrl_l, keyboard.Key.ctrl_r, keyboard.Key.ctrl]:
            self.current_modifiers.add('Ctrl')
        elif key in [keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.alt, keyboard.Key.alt_gr]:
            self.current_modifiers.add('Alt')
        elif key in [keyboard.Key.shift_l, keyboard.Key.shift_r, keyboard.Key.shift]:
            self.current_modifiers.add('Shift')
        elif key in [keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r]:
            self.current_modifiers.add('Win')

    def on_key_release(self, key):
        """按键释放"""
        if key in self.pressed_keys:
            self.pressed_keys.discard(key)

        # 清除修饰键
        if key in [keyboard.Key.ctrl_l, keyboard.Key.ctrl_r, keyboard.Key.ctrl]:
            self.current_modifiers.discard('Ctrl')
        elif key in [keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.alt, keyboard.Key.alt_gr]:
            self.current_modifiers.discard('Alt')
        elif key in [keyboard.Key.shift_l, keyboard.Key.shift_r, keyboard.Key.shift]:
            self.current_modifiers.discard('Shift')
        elif key in [keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r]:
            self.current_modifiers.discard('Win')

    def get_shortcut_string(self, key) -> tuple:
        """获取快捷键字符串"""
        # 如果是修饰键本身，不生成快捷键
        if key in [keyboard.Key.ctrl_l, keyboard.Key.ctrl_r, keyboard.Key.ctrl,
                   keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.alt, keyboard.Key.alt_gr,
                   keyboard.Key.shift_l, keyboard.Key.shift_r, keyboard.Key.shift,
                   keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r]:
            return None, None

        modifiers = sorted(self.current_modifiers)
        key_name = None
        sendkeys_code = None

        # 特殊键
        if key in self.SPECIAL_KEYS:
            key_name, sendkeys_code = self.SPECIAL_KEYS[key]
        # 普通字符键
        elif hasattr(key, 'char') and key.char:
            key_name = key.char.upper()
            sendkeys_code = key.char

        if not key_name:
            return None, None

        # 组合快捷键
        if modifiers:
            display_name = '+'.join(modifiers) + '+' + key_name
            # 生成 SendKeys 代码
            sendkeys_parts = []
            if 'Ctrl' in modifiers:
                sendkeys_parts.append('^')
            if 'Alt' in modifiers:
                sendkeys_parts.append('%')
            if 'Shift' in modifiers:
                sendkeys_parts.append('+')
            if 'Win' in modifiers:
                sendkeys_parts.append('^{ESC}')  # Win 键比较特殊

            sendkeys_parts.append(sendkeys_code if sendkeys_code else key_name.lower())
            sendkeys_str = ''.join(sendkeys_parts)
            return display_name, sendkeys_str
        else:
            # 单键
            return key_name, sendkeys_code


class SuperRecorderThread(QThread):
    """超级录制线程"""
    operation_detected = pyqtSignal(dict)
    status_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.mouse_listener = None
        self.keyboard_listener = None
        self.typed_text_buffer = ""
        self.last_control_info = None
        self.last_click_time = 0
        self.click_threshold = 0.3
        self.keyboard_recognizer = KeyboardRecognizer()
        self.last_shortcut_time = 0
        self.shortcut_delay = 0.5  # 快捷键最小间隔

    def stop(self):
        self.is_recording = False
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        self._flush_text_buffer()

    def run(self):
        self.is_recording = True
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        self.mouse_listener.start()
        self.keyboard_listener.start()
        self.mouse_listener.join()
        self.keyboard_listener.join()

    def _flush_text_buffer(self):
        if self.typed_text_buffer and self.last_control_info:
            op = {
                'action': 'type',
                'text': self.typed_text_buffer,
                'props': self.last_control_info
            }
            self.operation_detected.emit(op)
            self.typed_text_buffer = ""

    def on_click(self, x, y, button, pressed):
        if not self.is_recording or not pressed:
            return

        with auto.UIAutomationInitializerInThread():
            self._flush_text_buffer()

            try:
                control = auto.ControlFromPoint(x, y)
                if not control:
                    return

                props = {
                    'Name': control.Name,
                    'AutomationId': control.AutomationId,
                    'ClassName': control.ClassName,
                    'ControlType': control.ControlTypeName,
                    'window_title': control.GetTopLevelControl().Name
                }
                self.last_control_info = props

                current_time = time.time()
                if button == mouse.Button.left:
                    if current_time - self.last_click_time < self.click_threshold:
                        action = 'double_click'
                    else:
                        action = 'click'
                    self.last_click_time = current_time
                elif button == mouse.Button.right:
                    action = 'right_click'
                else:
                    return

                op = {'action': action, 'props': props}
                self.operation_detected.emit(op)
                self.status_changed.emit(f"✅ 录制: {action} - {props.get('Name', 'Unknown')}")

            except Exception as e:
                self.status_changed.emit(f"⚠️ 错误: {str(e)[:50]}")

    def on_key_press(self, key):
        if not self.is_recording:
            return

        # 更新键盘识别器状态
        self.keyboard_recognizer.on_key_press(key)

        # 检测快捷键
        current_time = time.time()
        if self.keyboard_recognizer.current_modifiers and current_time - self.last_shortcut_time > self.shortcut_delay:
            shortcut_name, sendkeys_code = self.keyboard_recognizer.get_shortcut_string(key)

            if shortcut_name and sendkeys_code:
                # 提交当前文本缓冲
                self._flush_text_buffer()

                # 记录快捷键操作
                op = {
                    'action': 'shortcut',
                    'shortcut': shortcut_name,
                    'sendkeys': sendkeys_code,
                    'props': self.last_control_info or {}
                }
                self.operation_detected.emit(op)
                self.status_changed.emit(f"⌨️ 快捷键: {shortcut_name}")
                self.last_shortcut_time = current_time
                return

        # 普通文本输入
        if key in [keyboard.Key.enter, keyboard.Key.tab]:
            self._flush_text_buffer()
        elif key == keyboard.Key.backspace:
            self.typed_text_buffer = self.typed_text_buffer[:-1]
        elif hasattr(key, 'char') and key.char and not self.keyboard_recognizer.current_modifiers:
            self.typed_text_buffer += key.char
        elif key == keyboard.Key.space and not self.keyboard_recognizer.current_modifiers:
            self.typed_text_buffer += ' '

    def on_key_release(self, key):
        if not self.is_recording:
            return

        # 更新键盘识别器状态
        self.keyboard_recognizer.on_key_release(key)


class SuperCodeGenerator:
    """超级代码生成器"""

    @staticmethod
    def generate_complete_script(operations: list, use_advanced_locators: bool = True,
                                use_robust: bool = True, max_retry: int = 3) -> str:
        """生成完整脚本"""
        if not operations:
            return "# 没有录制到任何操作\n"

        lines = []

        # 头部
        lines.extend(SuperCodeGenerator._generate_header())

        # 工具函数
        if use_robust:
            lines.extend(SuperCodeGenerator._generate_utility_functions())

        # 主函数
        lines.extend(SuperCodeGenerator._generate_main_function(
            operations, use_advanced_locators, use_robust, max_retry))

        # 入口点
        lines.extend(SuperCodeGenerator._generate_entry_point(max_retry))

        return "\n".join(lines)

    @staticmethod
    def _generate_header() -> list:
        lines = []
        lines.append("#!/usr/bin/env python3")
        lines.append("# -*- coding: utf-8 -*-")
        lines.append(f"# Generated by UI Automation Recorder - Super Enhanced")
        lines.append(f"# Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        lines.append("import uiautomation as auto")
        lines.append("import time")
        lines.append("import logging")
        lines.append("from datetime import datetime")
        lines.append("from pathlib import Path")
        lines.append("")
        lines.append("# 日志配置")
        lines.append("logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')")
        lines.append("logger = logging.getLogger(__name__)")
        lines.append("")
        lines.append("auto.uiautomation.SetGlobalSearchTimeout(10)")
        lines.append("")
        return lines

    @staticmethod
    def _generate_utility_functions() -> list:
        lines = []
        lines.append("class Config:")
        lines.append("    MAX_RETRY = 3")
        lines.append("    RETRY_DELAY = 1.0")
        lines.append("    OPERATION_DELAY = 0.5")
        lines.append("")

        # 查找控件函数
        lines.append("def find_control_smart(window, locators, name='control'):")
        lines.append('    """使用多种定位器智能查找控件"""')
        lines.append("    for retry in range(Config.MAX_RETRY):")
        lines.append("        for i, loc in enumerate(locators, 1):")
        lines.append("            try:")
        lines.append("                logger.debug(f'尝试定位器 {i}/{len(locators)}: {loc[\"strategy\"]}')")
        lines.append("                control = window.Control(**loc['params'])")
        lines.append("                if control.Exists(maxSearchSeconds=2):")
        lines.append("                    logger.info(f'✅ 找到 \"{name}\" (策略: {loc[\"strategy\"]})')")
        lines.append("                    return control")
        lines.append("            except:")
        lines.append("                continue")
        lines.append("        if retry < Config.MAX_RETRY - 1:")
        lines.append("            time.sleep(Config.RETRY_DELAY)")
        lines.append("    raise Exception(f'无法定位控件: {name}')")
        lines.append("")

        # 鲁棒点击
        lines.append("def click_smart(control, name='control'):")
        lines.append('    """智能点击"""')
        lines.append("    strategies = [")
        lines.append("        lambda: control.Click(simulateMove=False),")
        lines.append("        lambda: control.Click(simulateMove=True),")
        lines.append("        lambda: control.ClickInput()")
        lines.append("    ]")
        lines.append("    for strategy in strategies:")
        lines.append("        try:")
        lines.append("            control.SetFocus()")
        lines.append("            time.sleep(0.1)")
        lines.append("            strategy()")
        lines.append("            logger.info(f'✅ 点击成功: {name}')")
        lines.append("            return True")
        lines.append("        except:")
        lines.append("            continue")
        lines.append("    raise Exception(f'点击失败: {name}')")
        lines.append("")

        # 智能输入
        lines.append("def send_keys_smart(control, text, name='control'):")
        lines.append('    """智能输入"""')
        lines.append("    try:")
        lines.append("        control.SetFocus()")
        lines.append("        time.sleep(0.1)")
        lines.append("        control.SendKeys(text, interval=0.01)")
        lines.append("        logger.info(f'✅ 输入成功: {name}')")
        lines.append("        return True")
        lines.append("    except Exception as e:")
        lines.append("        logger.error(f'输入失败: {e}')")
        lines.append("        return False")
        lines.append("")

        return lines

    @staticmethod
    def _generate_main_function(operations: list, use_advanced_locators: bool,
                               use_robust: bool, max_retry: int) -> list:
        lines = []
        lines.append("def main():")
        lines.append("    logger.info('='*60)")
        lines.append("    logger.info('开始执行自动化脚本（超级增强版）')")
        lines.append("    logger.info('='*60)")
        lines.append("    ")

        # 按窗口分组
        window_groups = {}
        for op in operations:
            window_title = op['props'].get('window_title', 'Unknown') if 'props' in op else 'Unknown'
            if window_title not in window_groups:
                window_groups[window_title] = []
            window_groups[window_title].append(op)

        step_num = 0
        for window_title, ops in window_groups.items():
            lines.append(f"    # {'='*50}")
            lines.append(f"    # 窗口: {window_title}")
            lines.append(f"    # {'='*50}")
            lines.append(f"    window = auto.WindowControl(Name='{window_title}')")
            lines.append(f"    window.SetFocus()")
            lines.append(f"    time.sleep(0.3)")
            lines.append(f"    ")

            for op in ops:
                step_num += 1
                action = op['action']

                if action == 'shortcut':
                    # 快捷键操作
                    shortcut = op.get('shortcut', 'Unknown')
                    sendkeys = op.get('sendkeys', '')
                    lines.append(f"    # 步骤 {step_num}: 快捷键 {shortcut}")
                    lines.append(f"    try:")
                    lines.append(f"        window.SendKeys('{sendkeys}')")
                    lines.append(f"        logger.info('✅ 快捷键: {shortcut}')")
                    lines.append(f"        time.sleep(Config.OPERATION_DELAY)")
                    lines.append(f"    except Exception as e:")
                    lines.append(f"        logger.error(f'快捷键失败: {{e}}')")
                    lines.append(f"    ")
                    continue

                props = op['props']
                control_name = props.get('Name', 'Unknown')

                if use_advanced_locators:
                    # 生成高级定位器
                    all_locators = AdvancedLocatorGenerator.generate_all_locators(props)
                    best_locators = AdvancedLocatorGenerator.select_best_locators(all_locators, 3)

                    lines.append(f"    # 步骤 {step_num}: {action} - {control_name}")
                    lines.append(f"    try:")
                    lines.append(f"        locators = [")
                    for loc in best_locators:
                        params_str = str(loc['params']).replace("'auto.ControlType.", "auto.ControlType.").replace("Control'", "Control")
                        lines.append(f"            {{'strategy': '{loc['strategy']}', 'params': {params_str}}},")
                    lines.append(f"        ]")

                    if use_robust:
                        lines.append(f"        control = find_control_smart(window, locators, '{control_name}')")
                    else:
                        lines.append(f"        control = window.Control(**locators[0]['params'])")
                else:
                    # 简单定位器
                    lines.append(f"    # 步骤 {step_num}: {action} - {control_name}")
                    lines.append(f"    try:")
                    if props.get('AutomationId'):
                        lines.append(f"        control = window.Control(AutomationId='{props['AutomationId']}')")
                    elif props.get('Name'):
                        lines.append(f"        control = window.Control(Name='{props['Name']}')")
                    else:
                        lines.append(f"        control = window.Control(ClassName='{props.get('ClassName', '')}')")

                # 生成操作
                if action in ['click', 'double_click', 'right_click']:
                    if use_robust:
                        lines.append(f"        click_smart(control, '{control_name}')")
                    else:
                        if action == 'double_click':
                            lines.append(f"        control.DoubleClick()")
                        elif action == 'right_click':
                            lines.append(f"        control.RightClick()")
                        else:
                            lines.append(f"        control.Click()")
                elif action == 'type':
                    text = op.get('text', '')
                    escaped_text = text.replace("'", "\\'")
                    if use_robust:
                        lines.append(f"        send_keys_smart(control, '{escaped_text}', '{control_name}')")
                    else:
                        lines.append(f"        control.SendKeys('{escaped_text}')")

                lines.append(f"        time.sleep(Config.OPERATION_DELAY)")
                lines.append(f"    except Exception as e:")
                lines.append(f"        logger.error(f'步骤 {step_num} 失败: {{e}}')")
                lines.append(f"    ")

        lines.append("    logger.info('='*60)")
        lines.append("    logger.info('脚本执行完成')")
        lines.append("    logger.info('='*60)")
        lines.append("")
        return lines

    @staticmethod
    def _generate_entry_point(max_retry: int) -> list:
        lines = []
        lines.append("if __name__ == '__main__':")
        lines.append("    try:")
        lines.append(f"        Config.MAX_RETRY = {max_retry}")
        lines.append("        main()")
        lines.append("    except KeyboardInterrupt:")
        lines.append("        logger.warning('用户中断')")
        lines.append("    except Exception as e:")
        lines.append("        logger.error(f'异常: {e}')")
        return lines


class SuperRecorderWindow(QMainWindow):
    """超级录制器窗口"""

    def __init__(self):
        super().__init__()
        self.recorder_thread = None
        self.operations = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("UI Automation Recorder - Super Enhanced (高级定位器+键盘识别)")
        self.setGeometry(50, 50, 1600, 1000)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 控制面板
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel)

        # 主分割器
        main_splitter = QSplitter(Qt.Horizontal)

        # 左侧：操作列表
        left_panel = self.create_operations_panel()
        main_splitter.addWidget(left_panel)

        # 右侧：Tab页（代码+定位器分析）
        right_panel = self.create_right_panel()
        main_splitter.addWidget(right_panel)

        main_splitter.setSizes([400, 1200])
        main_layout.addWidget(main_splitter)

        self.statusBar().showMessage("就绪 - 超级增强版（10+种定位器策略+完整键盘识别）")

    def create_control_panel(self):
        """创建控制面板"""
        group = QGroupBox("⚙️ 控制面板 - 超级增强配置")
        layout = QHBoxLayout()

        # 录制按钮
        self.start_btn = QPushButton("🔴 开始录制")
        self.start_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 10px; }")
        self.start_btn.clicked.connect(self.start_recording)

        self.stop_btn = QPushButton("⏸️ 停止录制")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_recording)

        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)
        layout.addSpacing(20)

        # 选项
        self.advanced_locators_cb = QCheckBox("高级定位器")
        self.advanced_locators_cb.setChecked(True)
        self.advanced_locators_cb.stateChanged.connect(self.regenerate_code)

        self.robust_mode_cb = QCheckBox("鲁棒模式")
        self.robust_mode_cb.setChecked(True)
        self.robust_mode_cb.stateChanged.connect(self.regenerate_code)

        layout.addWidget(self.advanced_locators_cb)
        layout.addWidget(self.robust_mode_cb)

        layout.addWidget(QLabel("重试:"))
        self.max_retry_spin = QSpinBox()
        self.max_retry_spin.setRange(1, 10)
        self.max_retry_spin.setValue(3)
        self.max_retry_spin.valueChanged.connect(self.regenerate_code)
        layout.addWidget(self.max_retry_spin)

        layout.addStretch()

        # 按钮
        copy_btn = QPushButton("📋 复制代码")
        copy_btn.clicked.connect(self.copy_code)

        save_btn = QPushButton("💾 保存代码")
        save_btn.clicked.connect(self.save_code)

        clear_btn = QPushButton("🗑️ 清空")
        clear_btn.clicked.connect(self.clear_operations)

        layout.addWidget(copy_btn)
        layout.addWidget(save_btn)
        layout.addWidget(clear_btn)

        group.setLayout(layout)
        return group

    def create_operations_panel(self):
        """创建操作列表面板"""
        group = QGroupBox("📋 录制的操作")
        layout = QVBoxLayout()

        self.operations_list = QListWidget()
        self.operations_list.setFont(QFont("Consolas", 10))
        layout.addWidget(self.operations_list)

        # 特性说明
        info = QLabel(
            "✅ 10+种定位器 ✅ 稳定性评分\n"
            "⌨️ 快捷键识别 ⌨️ 组合键支持\n"
            "🎯 智能定位器选择"
        )
        info.setStyleSheet("QLabel { background-color: #e3f2fd; padding: 10px; border-radius: 5px; }")
        layout.addWidget(info)

        group.setLayout(layout)
        return group

    def create_right_panel(self):
        """创建右侧Tab面板"""
        tab_widget = QTabWidget()

        # Tab 1: 生成的代码
        code_tab = QWidget()
        code_layout = QVBoxLayout(code_tab)
        self.code_text_edit = QTextEdit()
        self.code_text_edit.setReadOnly(True)
        self.code_text_edit.setFont(QFont("Consolas", 9))
        self.code_text_edit.setPlainText("# 点击「开始录制」生成超级增强代码...")
        code_layout.addWidget(self.code_text_edit)
        tab_widget.addTab(code_tab, "💻 生成的代码")

        # Tab 2: 定位器分析
        locator_tab = QWidget()
        locator_layout = QVBoxLayout(locator_tab)
        self.locator_table = QTableWidget()
        self.locator_table.setColumnCount(4)
        self.locator_table.setHorizontalHeaderLabels(["策略", "稳定性", "速度", "描述"])
        self.locator_table.setFont(QFont("Consolas", 9))
        locator_layout.addWidget(self.locator_table)
        tab_widget.addTab(locator_tab, "🎯 定位器分析")

        return tab_widget

    def start_recording(self):
        """开始录制"""
        self.operations.clear()
        self.operations_list.clear()
        self.code_text_edit.setPlainText("# 录制中...\n")

        self.recorder_thread = SuperRecorderThread()
        self.recorder_thread.operation_detected.connect(self.on_operation_recorded)
        self.recorder_thread.status_changed.connect(self.on_status_changed)
        self.recorder_thread.start()

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.statusBar().showMessage("🔴 录制中... (支持快捷键识别)")

    def stop_recording(self):
        """停止录制"""
        if self.recorder_thread:
            self.recorder_thread.stop()
            self.recorder_thread.quit()
            self.recorder_thread.wait()

        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.statusBar().showMessage(f"录制已停止 - 共 {len(self.operations)} 个操作")

        self.regenerate_code()

    def on_operation_recorded(self, op: dict):
        """操作被录制"""
        self.operations.append(op)

        action = op['action']
        if action == 'shortcut':
            item_text = f"[{len(self.operations)}] ⌨️ {op.get('shortcut', 'Unknown')}"
        elif action == 'type':
            text = op.get('text', '')[:20]
            item_text = f"[{len(self.operations)}] ⌨️ 输入: \"{text}...\""
        else:
            control_name = op['props'].get('Name', 'Unknown')
            item_text = f"[{len(self.operations)}] 🖱️ {action}: {control_name}"

        self.operations_list.addItem(item_text)
        self.operations_list.scrollToBottom()

        # 更新定位器分析（只分析最后一个操作）
        if 'props' in op:
            self.update_locator_analysis(op['props'])

    def update_locator_analysis(self, props: dict):
        """更新定位器分析表"""
        all_locators = AdvancedLocatorGenerator.generate_all_locators(props)

        self.locator_table.setRowCount(len(all_locators))
        for i, loc in enumerate(all_locators):
            self.locator_table.setItem(i, 0, QTableWidgetItem(loc['strategy']))

            stability_item = QTableWidgetItem(f"{loc['stability']}")
            if loc['stability'] >= 80:
                stability_item.setBackground(QColor(76, 175, 80, 100))  # 绿色
            elif loc['stability'] >= 60:
                stability_item.setBackground(QColor(255, 193, 7, 100))  # 黄色
            else:
                stability_item.setBackground(QColor(244, 67, 54, 100))  # 红色
            self.locator_table.setItem(i, 1, stability_item)

            self.locator_table.setItem(i, 2, QTableWidgetItem(f"{loc['speed']}"))
            self.locator_table.setItem(i, 3, QTableWidgetItem(loc['description']))

        self.locator_table.resizeColumnsToContents()

    def on_status_changed(self, status: str):
        """状态变化"""
        self.statusBar().showMessage(status)

    def regenerate_code(self):
        """重新生成代码"""
        if not self.operations:
            return

        use_advanced = self.advanced_locators_cb.isChecked()
        use_robust = self.robust_mode_cb.isChecked()
        max_retry = self.max_retry_spin.value()

        code = SuperCodeGenerator.generate_complete_script(
            self.operations, use_advanced, use_robust, max_retry)

        self.code_text_edit.setPlainText(code)

    def copy_code(self):
        """复制代码"""
        code = self.code_text_edit.toPlainText()
        if code:
            try:
                pyperclip.copy(code)
                self.statusBar().showMessage("✅ 代码已复制到剪贴板", 3000)
            except Exception as e:
                QMessageBox.warning(self, "错误", f"复制失败: {str(e)}")

    def save_code(self):
        """保存代码"""
        code = self.code_text_edit.toPlainText()
        if not code or code.startswith("# 点击"):
            QMessageBox.warning(self, "提示", "没有可保存的代码")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self, "保存代码", f"automation_super_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py",
            "Python Files (*.py)")

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(code)
                self.statusBar().showMessage(f"✅ 代码已保存到: {filename}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")

    def clear_operations(self):
        """清空操作"""
        reply = QMessageBox.question(
            self, "确认", "确定要清空所有录制的操作吗？",
            QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.operations.clear()
            self.operations_list.clear()
            self.code_text_edit.setPlainText("# 点击「开始录制」生成超级增强代码...")
            self.locator_table.setRowCount(0)
            self.statusBar().showMessage("🗑️ 已清空所有操作")

    def closeEvent(self, event):
        """关闭窗口"""
        if self.recorder_thread and self.recorder_thread.is_recording:
            self.stop_recording()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SuperRecorderWindow()
    window.show()
    sys.exit(app.exec_())
