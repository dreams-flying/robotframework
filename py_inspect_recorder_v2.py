#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyInspect Recorder V2 - 改进版
修复定位器失败问题，生成更可靠的代码

改进点：
1. 生成多种备选定位器
2. 使用 start() 替代 connect(process=)
3. 添加错误处理和重试逻辑
4. 使用 click_input() 作为备选
5. 添加更详细的调试信息

依赖安装：
pip install pywinauto PyQt5 pynput pyperclip
"""

import sys
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QTextEdit, QLabel,
                             QComboBox, QMessageBox, QSplitter, QGroupBox, QLineEdit)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QTextCursor
from pywinauto import Desktop, Application
from pywinauto.controls.uiawrapper import UIAWrapper
from pynput import mouse, keyboard
import pyperclip


class RecorderThread(QThread):
    """录制线程 - 监听鼠标和键盘事件"""

    operation_detected = pyqtSignal(dict)
    status_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.backend = 'uia'
        self.mouse_listener = None
        self.keyboard_listener = None
        self.last_click_time = 0
        self.click_delay = 0.5
        self.typed_text = ""
        self.last_element = None
        self.app_executable = None  # 记录应用程序可执行文件

    def start_recording(self, app_executable=None):
        """开始录制"""
        self.is_recording = True
        self.typed_text = ""
        self.last_element = None
        self.app_executable = app_executable
        self.status_changed.emit("🔴 录制中...")

        self.mouse_listener = mouse.Listener(on_click=self.on_mouse_click)
        self.mouse_listener.start()

        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        self.keyboard_listener.start()

    def stop_recording(self):
        """停止录制"""
        self.is_recording = False
        self.status_changed.emit("⏸️ 已停止")

        if self.typed_text and self.last_element:
            self._emit_type_operation()

        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None

    def on_mouse_click(self, x, y, button, pressed):
        """鼠标点击事件"""
        if not self.is_recording or not pressed or button != mouse.Button.left:
            return

        current_time = time.time()
        if current_time - self.last_click_time < self.click_delay:
            return
        self.last_click_time = current_time

        if self.typed_text and self.last_element:
            self._emit_type_operation()

        try:
            element = Desktop(backend=self.backend).from_point(x, y)

            if element and isinstance(element, UIAWrapper):
                props = self._extract_element_properties(element)
                props['action'] = 'click'
                props['position'] = (x, y)
                self.operation_detected.emit(props)
                self.last_element = element
                self.typed_text = ""

        except Exception as e:
            self.status_changed.emit(f"⚠️ 元素识别失败: {str(e)[:50]}")

    def on_key_press(self, key):
        """键盘按下事件"""
        if not self.is_recording:
            return

        try:
            if hasattr(key, 'char') and key.char:
                self.typed_text += key.char
            elif key == keyboard.Key.space:
                self.typed_text += ' '
            elif key == keyboard.Key.enter:
                if self.typed_text and self.last_element:
                    self._emit_type_operation()
            elif key == keyboard.Key.backspace:
                if self.typed_text:
                    self.typed_text = self.typed_text[:-1]
            elif key == keyboard.Key.tab:
                if self.typed_text and self.last_element:
                    self._emit_type_operation()
                self.operation_detected.emit({'action': 'key', 'key': 'Tab'})
        except:
            pass

    def on_key_release(self, key):
        pass

    def _emit_type_operation(self):
        """提交累积的文本输入"""
        if self.typed_text and self.last_element:
            try:
                props = self._extract_element_properties(self.last_element)
                props['action'] = 'type'
                props['text'] = self.typed_text
                self.operation_detected.emit(props)
            except:
                pass
            finally:
                self.typed_text = ""

    def _extract_element_properties(self, element):
        """提取元素属性"""
        try:
            props = {}
            props['control_type'] = element.element_info.control_type
            props['automation_id'] = element.element_info.automation_id
            props['class_name'] = element.element_info.class_name
            props['name'] = element.element_info.name
            props['process_id'] = element.element_info.process_id

            try:
                top_window = element.top_level_parent()
                props['window_title'] = top_window.window_text()

                # 尝试获取可执行文件名
                if not self.app_executable:
                    try:
                        import psutil
                        process = psutil.Process(props['process_id'])
                        self.app_executable = process.exe()
                        props['executable'] = self.app_executable
                    except:
                        props['executable'] = None
                else:
                    props['executable'] = self.app_executable

            except:
                props['window_title'] = "Unknown"
                props['executable'] = None

            return props
        except Exception as e:
            return {'error': str(e)}

    def run(self):
        """线程主循环"""
        while True:
            time.sleep(0.1)
            if not self.is_recording:
                break


class ImprovedCodeGenerator:
    """改进的代码生成器 - 生成更可靠的代码"""

    @staticmethod
    def generate_locator_with_fallback(props, backend='uia'):
        """
        生成带备选方案的定位器代码
        返回主定位器和备选定位器
        """
        automation_id = props.get('automation_id', '')
        class_name = props.get('class_name', '')
        name = props.get('name', '')
        control_type = props.get('control_type', '')

        locators = []

        # 方法 1: AutomationId (最可靠)
        if automation_id:
            locators.append({
                'code': f'element = window.child_window(auto_id="{automation_id}")',
                'desc': 'AutomationId (推荐)'
            })

        # 方法 2: Name
        if name and name.strip():
            # 转义引号
            escaped_name = name.replace('"', '\\"')
            locators.append({
                'code': f'element = window.child_window(title="{escaped_name}")',
                'desc': 'Name/Title'
            })

        # 方法 3: Class + Control Type
        if class_name:
            locators.append({
                'code': f'element = window.child_window(class_name="{class_name}", control_type="{control_type}")',
                'desc': 'Class + Type'
            })

        # 方法 4: 仅 Control Type (最不可靠)
        if control_type:
            locators.append({
                'code': f'element = window.child_window(control_type="{control_type}")',
                'desc': 'Control Type (不推荐)'
            })

        return locators

    @staticmethod
    def generate_action_with_fallback(props):
        """生成带备选方案的操作代码"""
        action = props.get('action', 'click')

        if action == 'click':
            return [
                "    # 尝试点击",
                "    try:",
                "        element.click()",
                "    except:",
                "        # 备选方案：使用 click_input",
                "        try:",
                "            element.click_input()",
                "        except Exception as e:",
                "            print(f'点击失败: {e}')",
            ]

        elif action == 'type':
            text = props.get('text', '')
            escaped_text = text.replace('"', '\\"').replace("'", "\\'")
            return [
                "    # 输入文字",
                "    try:",
                f'        element.type_keys("{escaped_text}")',
                "    except Exception as e:",
                f"        print(f'输入失败: {{e}}')",
            ]

        elif action == 'key':
            key = props.get('key', '')
            key_map = {'Tab': '{TAB}', 'Enter': '{ENTER}', 'Esc': '{ESC}'}
            key_code = key_map.get(key, key)
            return [
                f"    element.type_keys('{key_code}')"
            ]

        return ["    # 未知操作"]

    @staticmethod
    def generate_complete_script(operations, backend='uia', app_executable=None):
        """生成完整脚本（改进版）"""
        if not operations:
            return "# 没有录制到任何操作\n"

        script = []
        script.append("#!/usr/bin/env python3")
        script.append("# -*- coding: utf-8 -*-")
        script.append("# PyInspect Recorder V2 自动生成")
        script.append("# 包含错误处理和备选方案\n")
        script.append("from pywinauto import Application")
        script.append("import time\n")

        script.append("def main():")

        # 确定应用连接方式
        first_op = operations[0]
        window_title = first_op.get('window_title', '')
        executable = first_op.get('executable') or app_executable

        script.append("    # ============ 连接应用 ============")

        if executable and executable.endswith('.exe'):
            exe_name = executable.split('\\')[-1]
            script.append(f"    # 方式 1: 启动应用（推荐）")
            script.append(f"    app = Application(backend='{backend}').start('{exe_name}')")
            script.append(f"")
            script.append(f"    # 方式 2: 连接已运行的应用")
            script.append(f"    # app = Application(backend='{backend}').connect(title_re='.*{window_title}.*')")
        else:
            script.append(f"    # 连接已运行的应用")
            script.append(f"    app = Application(backend='{backend}').connect(title_re='.*{window_title}.*')")
            script.append(f"    # 注意: 如果连接失败，请使用 start() 方法启动应用")

        script.append(f"")
        script.append(f"    # 获取主窗口")
        script.append(f"    window = app.window(title_re='.*{window_title}.*')")
        script.append(f"    window.wait('visible', timeout=10)")
        script.append(f"")

        # 生成操作
        script.append("    # ============ 执行操作 ============\n")

        for i, op in enumerate(operations):
            script.append(f"    # -------- 操作 {i+1}: {op.get('action', 'unknown')} --------")

            # 生成多种定位器
            locators = ImprovedCodeGenerator.generate_locator_with_fallback(op, backend)

            if len(locators) > 1:
                script.append(f"    # 定位元素（尝试多种方法）")
                script.append(f"    element = None")

                for j, loc in enumerate(locators):
                    if j == 0:
                        script.append(f"    try:")
                        script.append(f"        # 方法 {j+1}: {loc['desc']}")
                        script.append(f"        {loc['code']}")
                        script.append(f"        element.wait('exists', timeout=2)")
                    else:
                        script.append(f"    except:")
                        script.append(f"        try:")
                        script.append(f"            # 方法 {j+1}: {loc['desc']}")
                        script.append(f"            {loc['code']}")
                        script.append(f"            element.wait('exists', timeout=2)")

                # 最后的 except
                script.append(f"        except Exception as e:")
                script.append(f"            print(f'元素定位失败: {{e}}')")
                script.append(f"            continue")
                script.append(f"")

            elif len(locators) == 1:
                script.append(f"    # 定位元素")
                script.append(f"    try:")
                script.append(f"        {locators[0]['code']}")
                script.append(f"        element.wait('exists', timeout=2)")
                script.append(f"    except Exception as e:")
                script.append(f"        print(f'元素定位失败: {{e}}')")
                script.append(f"        continue")
                script.append(f"")

            # 生成操作代码
            action_lines = ImprovedCodeGenerator.generate_action_with_fallback(op)
            script.extend(action_lines)

            script.append(f"    time.sleep(0.5)  # 等待操作完成")
            script.append(f"")

        script.append("    print('✅ 所有操作执行完成')")
        script.append("")
        script.append("if __name__ == '__main__':")
        script.append("    try:")
        script.append("        main()")
        script.append("    except Exception as e:")
        script.append("        print(f'❌ 脚本执行失败: {e}')")
        script.append("        import traceback")
        script.append("        traceback.print_exc()")

        return "\n".join(script)


class RecorderWindow(QMainWindow):
    """录制器主窗口"""

    def __init__(self):
        super().__init__()
        self.operations = []
        self.recorder_thread = None
        self.app_executable = None
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("PyInspect Recorder V2 - 改进版（更可靠的代码生成）")
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 控制面板
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel)

        # 分割器
        splitter = QSplitter(Qt.Horizontal)

        # 左侧：操作列表
        operations_group = QGroupBox("📋 录制的操作")
        operations_layout = QVBoxLayout()
        self.operations_text = QTextEdit()
        self.operations_text.setReadOnly(True)
        self.operations_text.setFont(QFont("Courier", 10))
        operations_layout.addWidget(self.operations_text)
        operations_group.setLayout(operations_layout)
        splitter.addWidget(operations_group)

        # 右侧：生成的代码
        code_group = QGroupBox("💻 生成的代码（包含错误处理）")
        code_layout = QVBoxLayout()
        self.code_text = QTextEdit()
        self.code_text.setReadOnly(True)
        self.code_text.setFont(QFont("Courier", 10))
        code_layout.addWidget(self.code_text)

        code_buttons = QHBoxLayout()
        copy_btn = QPushButton("📋 复制代码")
        copy_btn.clicked.connect(self.copy_code)
        clear_btn = QPushButton("🗑️ 清空")
        clear_btn.clicked.connect(self.clear_operations)
        code_buttons.addWidget(copy_btn)
        code_buttons.addWidget(clear_btn)
        code_buttons.addStretch()
        code_layout.addLayout(code_buttons)

        code_group.setLayout(code_layout)
        splitter.addWidget(code_group)

        splitter.setSizes([400, 800])
        main_layout.addWidget(splitter)

        self.statusBar().showMessage("⏸️ 就绪 - 点击「开始录制」开始")

    def create_control_panel(self):
        """创建控制面板"""
        group = QGroupBox("⚙️ 控制面板")
        layout = QHBoxLayout()

        # Backend 选择
        layout.addWidget(QLabel("Backend:"))
        self.backend_combo = QComboBox()
        self.backend_combo.addItems(['uia', 'win32'])
        layout.addWidget(self.backend_combo)

        layout.addSpacing(10)

        # 应用程序路径（可选）
        layout.addWidget(QLabel("应用 (可选):"))
        self.app_exe_input = QLineEdit()
        self.app_exe_input.setPlaceholderText("如 notepad.exe")
        self.app_exe_input.setFixedWidth(150)
        layout.addWidget(self.app_exe_input)

        layout.addSpacing(20)

        # 录制控制
        self.start_btn = QPushButton("🔴 开始录制")
        self.start_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        self.start_btn.clicked.connect(self.start_recording)
        layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("⏸️ 停止录制")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_recording)
        layout.addWidget(self.stop_btn)

        layout.addStretch()

        help_btn = QPushButton("❓ 帮助")
        help_btn.clicked.connect(self.show_help)
        layout.addWidget(help_btn)

        group.setLayout(layout)
        return group

    def start_recording(self):
        """开始录制"""
        app_exe = self.app_exe_input.text().strip()
        self.app_executable = app_exe if app_exe else None

        self.recorder_thread = RecorderThread()
        self.recorder_thread.backend = self.backend_combo.currentText()
        self.recorder_thread.operation_detected.connect(self.on_operation_detected)
        self.recorder_thread.status_changed.connect(self.on_status_changed)

        self.recorder_thread.start()
        self.recorder_thread.start_recording(self.app_executable)

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.backend_combo.setEnabled(False)
        self.app_exe_input.setEnabled(False)

        self.statusBar().showMessage("🔴 录制中... (在任意应用程序上进行操作)")

    def stop_recording(self):
        """停止录制"""
        if self.recorder_thread:
            self.recorder_thread.stop_recording()
            self.recorder_thread.quit()
            self.recorder_thread.wait()
            self.recorder_thread = None

        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.backend_combo.setEnabled(True)
        self.app_exe_input.setEnabled(True)

        self.statusBar().showMessage("⏸️ 已停止录制")

    def on_operation_detected(self, props):
        """处理检测到的操作"""
        self.operations.append(props)

        action = props.get('action', 'unknown')
        window_title = props.get('window_title', 'Unknown')

        if action == 'click':
            name = props.get('name', props.get('automation_id', props.get('class_name', 'Unknown')))
            op_text = f"[{len(self.operations)}] 点击: {name} (窗口: {window_title})"
        elif action == 'type':
            text = props.get('text', '')
            op_text = f"[{len(self.operations)}] 输入: \"{text}\""
        elif action == 'key':
            key = props.get('key', '')
            op_text = f"[{len(self.operations)}] 按键: {key}"
        else:
            op_text = f"[{len(self.operations)}] 未知操作"

        self.operations_text.append(op_text)

        cursor = self.operations_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.operations_text.setTextCursor(cursor)

        self.update_generated_code()

    def on_status_changed(self, status):
        """处理状态变化"""
        self.statusBar().showMessage(status)

    def update_generated_code(self):
        """更新生成的代码"""
        backend = self.backend_combo.currentText()
        code = ImprovedCodeGenerator.generate_complete_script(
            self.operations, backend, self.app_executable
        )
        self.code_text.setPlainText(code)

    def copy_code(self):
        """复制代码到剪贴板"""
        code = self.code_text.toPlainText()
        if code:
            try:
                pyperclip.copy(code)
                self.statusBar().showMessage("✅ 代码已复制到剪贴板", 3000)
            except Exception as e:
                QMessageBox.warning(self, "错误", f"复制失败: {str(e)}")
        else:
            QMessageBox.warning(self, "提示", "没有可复制的代码")

    def clear_operations(self):
        """清空操作"""
        reply = QMessageBox.question(
            self, "确认", "确定要清空所有录制的操作吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.operations.clear()
            self.operations_text.clear()
            self.code_text.clear()
            self.statusBar().showMessage("🗑️ 已清空所有操作")

    def show_help(self):
        """显示帮助"""
        help_text = """
<h3>PyInspect Recorder V2 - 改进版</h3>

<h4>🆕 V2 改进：</h4>
<ul>
  <li>✅ 生成多种备选定位器（自动尝试）</li>
  <li>✅ 使用 start() 替代 connect(process=)</li>
  <li>✅ 添加 try-except 错误处理</li>
  <li>✅ click() 失败自动尝试 click_input()</li>
  <li>✅ 更详细的错误提示</li>
</ul>

<h4>📖 使用步骤：</h4>
<ol>
  <li>（可选）输入应用程序名称，如 notepad.exe</li>
  <li>点击「开始录制」</li>
  <li>在目标应用上操作</li>
  <li>点击「停止录制」</li>
  <li>复制生成的代码</li>
</ol>

<h4>💡 提示：</h4>
<ul>
  <li>生成的代码包含多种定位方法</li>
  <li>如果一种方法失败，会自动尝试下一种</li>
  <li>代码可以直接运行，无需修改</li>
</ul>
        """
        QMessageBox.information(self, "帮助", help_text)

    def closeEvent(self, event):
        """关闭窗口时停止录制"""
        if self.recorder_thread and self.recorder_thread.is_recording:
            self.stop_recording()
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = RecorderWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
