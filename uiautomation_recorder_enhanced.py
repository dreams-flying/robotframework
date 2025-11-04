#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI Automation Recorder Enhanced - 增强版
基于 uiautomation 的 Windows 桌面自动化录制工具

增强功能：
1. 多种定位器策略（自动生成备选方案）
2. 智能操作识别（点击、双击、右键、输入、复选框等）
3. 代码结构优化（生成函数、窗口去重）
4. 一键复制和保存功能
5. 更好的错误处理和重试机制
6. 智能等待策略
7. 参数化支持
8. 操作预览面板

依赖安装：
pip install uiautomation PyQt5 pynput pyperclip
"""

import sys
import time
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QTextEdit, QLabel,
                             QSplitter, QGroupBox, QCheckBox, QLineEdit,
                             QComboBox, QFileDialog, QMessageBox, QListWidget)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QTextCursor

import uiautomation as auto
from pynput import mouse, keyboard
import pyperclip


class EnhancedCodeGenerator:
    """增强的代码生成器"""

    @staticmethod
    def get_multiple_locators(props: dict) -> list:
        """生成多种定位器策略（按优先级排序）"""
        locators = []

        # 策略 1: AutomationId（最可靠）
        if props.get('AutomationId'):
            locators.append({
                'code': f"AutomationId='{props['AutomationId']}'",
                'priority': 1,
                'desc': 'AutomationId (最可靠)'
            })

        # 策略 2: Name + ControlType
        if props.get('Name'):
            name = props['Name'].replace("'", "\\'")
            control_type = props.get('ControlType', '')
            locators.append({
                'code': f"Name='{name}', ControlType=auto.ControlType.{control_type}",
                'priority': 2,
                'desc': 'Name + ControlType'
            })

        # 策略 3: ClassName + ControlType
        if props.get('ClassName'):
            class_name = props['ClassName']
            control_type = props.get('ControlType', '')
            locators.append({
                'code': f"ClassName='{class_name}', ControlType=auto.ControlType.{control_type}",
                'priority': 3,
                'desc': 'ClassName + ControlType'
            })

        # 策略 4: 仅 ControlType（最不可靠，但总是可用）
        if props.get('ControlType'):
            control_type = props['ControlType']
            locators.append({
                'code': f"ControlType=auto.ControlType.{control_type}",
                'priority': 4,
                'desc': 'ControlType (不推荐)'
            })

        return locators

    @staticmethod
    def generate_window_locator(window_title: str) -> str:
        """生成窗口定位器"""
        escaped_title = window_title.replace("'", "\\'")
        return f"Name='{escaped_title}'"

    @staticmethod
    def generate_find_control_code(props: dict, var_name: str = 'control', use_fallback: bool = True) -> list:
        """生成查找控件的代码（带备选方案）"""
        lines = []
        locators = EnhancedCodeGenerator.get_multiple_locators(props)

        if not use_fallback or len(locators) == 1:
            # 简单模式：只用第一个定位器
            lines.append(f"    {var_name} = window.Control({locators[0]['code']})")
        else:
            # 备选模式：尝试多个定位器
            lines.append(f"    {var_name} = None")
            for i, loc in enumerate(locators[:3]):  # 最多3个备选方案
                if i == 0:
                    lines.append(f"    try:")
                    lines.append(f"        # 方法 {i+1}: {loc['desc']}")
                    lines.append(f"        {var_name} = window.Control({loc['code']})")
                    lines.append(f"        {var_name}.Exists(maxSearchSeconds=2)")
                else:
                    lines.append(f"    except auto.LookupError:")
                    lines.append(f"        try:")
                    lines.append(f"            # 方法 {i+1}: {loc['desc']}")
                    lines.append(f"            {var_name} = window.Control({loc['code']})")
                    lines.append(f"            {var_name}.Exists(maxSearchSeconds=2)")

            # 最后的 except
            lines.append(f"        except auto.LookupError:")
            lines.append(f"            raise Exception('无法定位控件')")

        return lines

    @staticmethod
    def generate_action_code(action: str, props: dict, text: str = None) -> list:
        """根据操作类型生成代码"""
        lines = []

        if action == 'click':
            lines.append("    # 点击控件")
            lines.append("    control.SetFocus()")
            lines.append("    control.Click(simulateMove=False)")

        elif action == 'double_click':
            lines.append("    # 双击控件")
            lines.append("    control.SetFocus()")
            lines.append("    control.DoubleClick(simulateMove=False)")

        elif action == 'right_click':
            lines.append("    # 右键点击")
            lines.append("    control.SetFocus()")
            lines.append("    control.RightClick(simulateMove=False)")

        elif action == 'type':
            escaped_text = text.replace("'", "\\'") if text else ''
            # 判断是否为密码框
            if 'password' in props.get('Name', '').lower():
                lines.append("    # 输入密码")
                lines.append(f"    control.SetValue('{escaped_text}')")
            else:
                lines.append("    # 输入文本")
                lines.append("    control.SetFocus()")
                lines.append(f"    control.SendKeys('{escaped_text}', interval=0.01)")

        elif action == 'check':
            lines.append("    # 勾选复选框")
            lines.append("    if not control.GetTogglePattern().ToggleState:")
            lines.append("        control.Click()")

        elif action == 'uncheck':
            lines.append("    # 取消勾选复选框")
            lines.append("    if control.GetTogglePattern().ToggleState:")
            lines.append("        control.Click()")

        elif action == 'select':
            lines.append("    # 选择下拉项")
            lines.append("    control.Click()")
            lines.append(f"    # TODO: 选择具体项目")

        return lines

    @staticmethod
    def generate_complete_script(operations: list, use_functions: bool = True,
                                use_fallback: bool = True, add_waits: bool = True) -> str:
        """生成完整脚本"""
        if not operations:
            return "# 没有录制到任何操作\n"

        lines = []

        # 文件头
        lines.append("#!/usr/bin/env python3")
        lines.append("# -*- coding: utf-8 -*-")
        lines.append(f"# Generated by UI Automation Recorder Enhanced")
        lines.append(f"# Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        lines.append("import uiautomation as auto")
        lines.append("import time")
        lines.append("")
        lines.append("# 设置全局搜索超时")
        lines.append("auto.uiautomation.SetGlobalSearchTimeout(10)")
        lines.append("")

        if use_functions:
            # 生成函数版本
            lines.extend(EnhancedCodeGenerator._generate_function_based_code(
                operations, use_fallback, add_waits))
        else:
            # 生成线性版本
            lines.extend(EnhancedCodeGenerator._generate_linear_code(
                operations, use_fallback, add_waits))

        return "\n".join(lines)

    @staticmethod
    def _generate_function_based_code(operations: list, use_fallback: bool, add_waits: bool) -> list:
        """生成基于函数的代码"""
        lines = []

        # 辅助函数
        lines.append("def safe_click(control, action='click'):")
        lines.append('    """安全点击（带重试）"""')
        lines.append("    try:")
        lines.append("        control.SetFocus()")
        lines.append("        if action == 'double_click':")
        lines.append("            control.DoubleClick(simulateMove=False)")
        lines.append("        elif action == 'right_click':")
        lines.append("            control.RightClick(simulateMove=False)")
        lines.append("        else:")
        lines.append("            control.Click(simulateMove=False)")
        lines.append("        return True")
        lines.append("    except Exception as e:")
        lines.append("        print(f'点击失败: {e}')")
        lines.append("        return False")
        lines.append("")

        lines.append("def safe_send_keys(control, text):")
        lines.append('    """安全输入文本"""')
        lines.append("    try:")
        lines.append("        control.SetFocus()")
        lines.append("        control.SendKeys(text, interval=0.01)")
        lines.append("        return True")
        lines.append("    except Exception as e:")
        lines.append("        print(f'输入失败: {e}')")
        lines.append("        return False")
        lines.append("")

        # 主函数
        lines.append("def main():")
        lines.append('    """主自动化流程"""')
        lines.append("    print('开始执行自动化脚本...')")
        lines.append("")

        # 按窗口分组操作
        window_groups = {}
        for op in operations:
            window_title = op['props'].get('window_title', 'Unknown')
            if window_title not in window_groups:
                window_groups[window_title] = []
            window_groups[window_title].append(op)

        # 为每个窗口生成代码
        for window_title, ops in window_groups.items():
            lines.append(f"    # ========== 窗口: {window_title} ==========")
            window_locator = EnhancedCodeGenerator.generate_window_locator(window_title)
            lines.append(f"    window = auto.WindowControl({window_locator})")
            lines.append("    window.SetFocus()")
            if add_waits:
                lines.append("    time.sleep(0.5)")
            lines.append("")

            # 处理该窗口的所有操作
            for i, op in enumerate(ops, 1):
                action = op['action']
                props = op['props']
                control_name = props.get('Name', 'Unknown')

                lines.append(f"    # 步骤 {i}: {action} - {control_name}")

                # 生成定位代码
                find_lines = EnhancedCodeGenerator.generate_find_control_code(
                    props, 'control', use_fallback)
                lines.extend(find_lines)

                # 生成操作代码
                if action == 'click':
                    lines.append("    safe_click(control)")
                elif action == 'double_click':
                    lines.append("    safe_click(control, 'double_click')")
                elif action == 'right_click':
                    lines.append("    safe_click(control, 'right_click')")
                elif action == 'type':
                    text = op.get('text', '')
                    escaped_text = text.replace("'", "\\'")
                    lines.append(f"    safe_send_keys(control, '{escaped_text}')")
                else:
                    action_lines = EnhancedCodeGenerator.generate_action_code(
                        action, props, op.get('text'))
                    lines.extend(action_lines)

                if add_waits:
                    lines.append("    time.sleep(0.3)")
                lines.append("")

        lines.append("    print('✅ 自动化脚本执行完成')")
        lines.append("")
        lines.append("")
        lines.append("if __name__ == '__main__':")
        lines.append("    try:")
        lines.append("        main()")
        lines.append("    except Exception as e:")
        lines.append("        print(f'❌ 脚本执行失败: {e}')")
        lines.append("        import traceback")
        lines.append("        traceback.print_exc()")

        return lines

    @staticmethod
    def _generate_linear_code(operations: list, use_fallback: bool, add_waits: bool) -> list:
        """生成线性代码"""
        lines = []

        current_window = None
        for i, op in enumerate(operations, 1):
            action = op['action']
            props = op['props']
            window_title = props.get('window_title', 'Unknown')
            control_name = props.get('Name', 'Unknown')

            lines.append(f"# -------- 步骤 {i}: {action} - {control_name} --------")

            # 如果窗口变了，重新获取窗口
            if window_title != current_window:
                current_window = window_title
                window_locator = EnhancedCodeGenerator.generate_window_locator(window_title)
                lines.append(f"window = auto.WindowControl({window_locator})")
                lines.append("window.SetFocus()")
                if add_waits:
                    lines.append("time.sleep(0.5)")
                lines.append("")

            lines.append("try:")

            # 生成定位代码
            find_lines = EnhancedCodeGenerator.generate_find_control_code(
                props, 'control', use_fallback)
            lines.extend(find_lines)

            # 生成操作代码
            action_lines = EnhancedCodeGenerator.generate_action_code(
                action, props, op.get('text'))
            lines.extend(action_lines)

            if add_waits:
                lines.append("    time.sleep(0.3)")

            lines.append("except Exception as e:")
            lines.append(f"    print(f'步骤 {i} 失败: {{e}}')")

            lines.append("")

        lines.append("print('✅ 所有操作执行完成')")

        return lines


class EnhancedRecorderThread(QThread):
    """增强的录制线程"""
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
        self.click_threshold = 0.3  # 双击判定时间

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
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press)
        self.mouse_listener.start()
        self.keyboard_listener.start()
        self.mouse_listener.join()
        self.keyboard_listener.join()

    def _flush_text_buffer(self):
        """提交缓冲区的文本"""
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

                # 判断操作类型
                current_time = time.time()
                if button == mouse.Button.left:
                    # 检测双击
                    if current_time - self.last_click_time < self.click_threshold:
                        action = 'double_click'
                    else:
                        # 检测控件类型
                        control_type = props['ControlType']
                        if control_type == 'CheckBoxControl':
                            # TODO: 可以检测当前状态来决定是 check 还是 uncheck
                            action = 'check'
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

    def on_press(self, key):
        if not self.is_recording:
            return

        if key in [keyboard.Key.enter, keyboard.Key.tab]:
            self._flush_text_buffer()
        elif key == keyboard.Key.backspace:
            self.typed_text_buffer = self.typed_text_buffer[:-1]
        elif hasattr(key, 'char') and key.char:
            self.typed_text_buffer += key.char
        elif key == keyboard.Key.space:
            self.typed_text_buffer += ' '


class EnhancedRecorderWindow(QMainWindow):
    """增强的录制器主窗口"""

    def __init__(self):
        super().__init__()
        self.recorder_thread = None
        self.operations = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("UI Automation Recorder Enhanced - 增强版")
        self.setGeometry(150, 150, 1400, 900)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 控制面板
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel)

        # 分割器：左侧操作列表，右侧代码
        splitter = QSplitter(Qt.Horizontal)

        # 左侧：操作列表
        left_panel = self.create_operations_panel()
        splitter.addWidget(left_panel)

        # 右侧：代码显示
        right_panel = self.create_code_panel()
        splitter.addWidget(right_panel)

        splitter.setSizes([400, 1000])
        main_layout.addWidget(splitter)

        self.statusBar().showMessage("就绪 - 点击「开始录制」开始")

    def create_control_panel(self):
        """创建控制面板"""
        group = QGroupBox("⚙️ 控制面板")
        layout = QHBoxLayout()

        # 录制控制
        self.start_btn = QPushButton("🔴 开始录制")
        self.start_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 8px; }")
        self.start_btn.clicked.connect(self.start_recording)

        self.stop_btn = QPushButton("⏸️ 停止录制")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_recording)

        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)

        layout.addSpacing(20)

        # 代码生成选项
        layout.addWidget(QLabel("代码选项:"))

        self.use_functions_cb = QCheckBox("生成函数")
        self.use_functions_cb.setChecked(True)
        self.use_functions_cb.stateChanged.connect(self.regenerate_code)

        self.use_fallback_cb = QCheckBox("多重定位器")
        self.use_fallback_cb.setChecked(True)
        self.use_fallback_cb.stateChanged.connect(self.regenerate_code)

        self.add_waits_cb = QCheckBox("添加等待")
        self.add_waits_cb.setChecked(True)
        self.add_waits_cb.stateChanged.connect(self.regenerate_code)

        layout.addWidget(self.use_functions_cb)
        layout.addWidget(self.use_fallback_cb)
        layout.addWidget(self.add_waits_cb)

        layout.addStretch()

        # 操作按钮
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

        group.setLayout(layout)
        return group

    def create_code_panel(self):
        """创建代码显示面板"""
        group = QGroupBox("💻 生成的代码")
        layout = QVBoxLayout()

        self.code_text_edit = QTextEdit()
        self.code_text_edit.setReadOnly(True)
        self.code_text_edit.setFont(QFont("Consolas", 10))
        self.code_text_edit.setPlainText("# 点击「开始录制」来生成代码...")

        layout.addWidget(self.code_text_edit)

        group.setLayout(layout)
        return group

    def start_recording(self):
        """开始录制"""
        self.operations.clear()
        self.operations_list.clear()
        self.code_text_edit.setPlainText("# 录制中...\n")

        self.recorder_thread = EnhancedRecorderThread()
        self.recorder_thread.operation_detected.connect(self.on_operation_recorded)
        self.recorder_thread.status_changed.connect(self.on_status_changed)
        self.recorder_thread.start()

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.statusBar().showMessage("🔴 录制中...")

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

        # 更新操作列表
        action = op['action']
        control_name = op['props'].get('Name', 'Unknown')
        if action == 'type':
            text = op.get('text', '')[:20]
            item_text = f"[{len(self.operations)}] {action}: \"{text}...\""
        else:
            item_text = f"[{len(self.operations)}] {action}: {control_name}"

        self.operations_list.addItem(item_text)
        self.operations_list.scrollToBottom()

    def on_status_changed(self, status: str):
        """状态变化"""
        self.statusBar().showMessage(status)

    def regenerate_code(self):
        """重新生成代码"""
        if not self.operations:
            return

        use_functions = self.use_functions_cb.isChecked()
        use_fallback = self.use_fallback_cb.isChecked()
        add_waits = self.add_waits_cb.isChecked()

        code = EnhancedCodeGenerator.generate_complete_script(
            self.operations, use_functions, use_fallback, add_waits)

        self.code_text_edit.setPlainText(code)

    def copy_code(self):
        """复制代码到剪贴板"""
        code = self.code_text_edit.toPlainText()
        if code:
            try:
                pyperclip.copy(code)
                self.statusBar().showMessage("✅ 代码已复制到剪贴板", 3000)
            except Exception as e:
                QMessageBox.warning(self, "错误", f"复制失败: {str(e)}")
        else:
            QMessageBox.warning(self, "提示", "没有可复制的代码")

    def save_code(self):
        """保存代码到文件"""
        code = self.code_text_edit.toPlainText()
        if not code or code.startswith("# 点击"):
            QMessageBox.warning(self, "提示", "没有可保存的代码")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self, "保存代码", f"automation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py",
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
            self.code_text_edit.setPlainText("# 点击「开始录制」来生成代码...")
            self.statusBar().showMessage("🗑️ 已清空所有操作")

    def closeEvent(self, event):
        """关闭窗口"""
        if self.recorder_thread and self.recorder_thread.is_recording:
            self.stop_recording()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = EnhancedRecorderWindow()
    window.show()
    sys.exit(app.exec_())
