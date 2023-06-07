# -*- coding: utf-8 -*-
# @Time    : 2023/6/5 23:29
# @Author  : CXRui
# @File    : main.py
# @Description :
import datetime
import os.path
import sys
import subprocess
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtCore import QProcess, Qt, QTime, QTimer, QDir
from PyQt6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QComboBox, \
    QTextEdit, QLabel, QFileDialog, QMessageBox, QLineEdit


class FastbotMonkey(QMainWindow):
    def __init__(self):
        super(FastbotMonkey, self).__init__()
        # 设置标题
        self.test_process = None    # 打印monkey log的进程
        self.crash_num = 0          # crash数量初始化为0
        self.anr_num = 0            # anr数量初始化为0
        self.setWindowTitle("Fastbot Monkey PyQt")

        # 得到系统屏幕的大小
        screen = QGuiApplication.primaryScreen().geometry()
        screen_width = screen.width()
        screen_height = screen.height()

        # 得到窗口的大小
        window = self.geometry()
        window_width = window.width()
        window_heigh = window.height()

        # 得到居中时左顶点x坐标和y坐标
        left_x = int((screen_width - window_width) / 2)
        left_y = int((screen_height - window_heigh) / 2)

        layout1 = QVBoxLayout()

        self.start_execute_btn = QPushButton("开始执行", self)
        self.start_execute_btn.clicked.connect(self.click_start_execute_btn)
        self.stop_execute_btn = QPushButton("停止执行", self)
        self.stop_execute_btn.clicked.connect(self.click_stop_execute_btn)
        self.export_log_btn = QPushButton("导出log", self)
        self.export_log_btn.clicked.connect(self.export_files)

        layout2 = QHBoxLayout()
        layout2.addWidget(self.start_execute_btn)
        layout2.addWidget(self.stop_execute_btn)
        layout2.addWidget(self.export_log_btn)
        layout1.addLayout(layout2)

        layout3 = QHBoxLayout()
        self.device_title = QLabel("测试设备：", self)
        self.device_combobox = QComboBox(self)
        self.package_title = QLabel("测试包名：", self)
        self.device_combobox.currentTextChanged.connect(self.select_device)
        self.test_time_num_title = QLabel("测试时间：")
        self.test_time_num_edit = QLineEdit(self)
        self.test_time_num_edit.setText("720")
        self.throttle_num_title = QLabel("点击频率：")
        self.throttle_num_edit = QLineEdit(self)
        self.throttle_num_edit.setText("500")
        self.refresh_btn = QPushButton("刷新", self)
        self.refresh_btn.clicked.connect(self.refresh_devices)
        self.package_combobox = QComboBox(self)
        self.package_combobox.addItem("请先选择测试设备")

        layout3.addWidget(self.device_title)
        layout3.addWidget(self.device_combobox)
        layout3.addWidget(self.package_title)
        layout3.addWidget(self.package_combobox)
        layout3.addWidget(self.refresh_btn)
        layout3.addWidget(self.test_time_num_title)
        layout3.addWidget(self.test_time_num_edit)
        layout3.addWidget(self.throttle_num_title)
        layout3.addWidget(self.throttle_num_edit)
        layout1.addLayout(layout3)

        layout4 = QHBoxLayout()
        self.test_time_title = QLabel("当前已测试时长：")
        self.test_time_title.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.test_time = QLabel("00:00:00")
        self.test_time.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.initial_time = QTime(0, 0, 0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.crash_num_title = QLabel("Crash数量：")
        self.crash_num_title.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.crash_num_show = QLabel("0", self)
        self.crash_num_show.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.anr_num_title = QLabel("Anr数量：")
        self.anr_num_title.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.anr_num_show = QLabel("0", self)
        self.anr_num_show.setAlignment(Qt.AlignmentFlag.AlignLeft)

        layout4.addWidget(self.test_time_title)
        layout4.addWidget(self.test_time)
        layout4.addWidget(self.crash_num_title)
        layout4.addWidget(self.crash_num_show)
        layout4.addWidget(self.anr_num_title)
        layout4.addWidget(self.anr_num_show)
        layout1.addLayout(layout4)

        self.log_text_edit = QTextEdit(self)
        self.log_text_edit.setReadOnly(True)
        layout1.addWidget(self.log_text_edit)

        central_widget = QWidget()
        central_widget.setLayout(layout1)
        self.setCentralWidget(central_widget)

        self.setLayout(layout1)
        self.setGeometry(left_x, left_y, 900, 600)

    def get_all_devices(self):
        """
        QProcess获取所有设备
        :return:
        """
        cmd = "adb devices"
        sp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf8")
        all_devices = [i.split("\t")[0] for i in sp.stdout.read().strip().split("\n")][1:]
        self.device_combobox.addItems(all_devices)

    def refresh_devices(self):
        """
        点击刷新按钮，就重新执行adb devices命令
        :return:
        """
        self.device_combobox.clear()
        self.get_all_devices()

    def refresh_package(self):
        """
        获取设备的所有包名
        :return:
        """
        self.package_combobox.clear()
        if not self.device_combobox.currentText():
            self.package_combobox.addItem("请先选择测试设备")
        else:
            self.get_all_package()

    def select_device(self):
        """
        选择设备后，刷新显示新的设备所有包名
        :return:
        """
        self.refresh_package()

    def get_all_package(self):
        """
        QProcess获取所有包名
        :return:
        """
        cmd = f"adb -s {self.device_combobox.currentText()} shell pm list packages"
        sp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf8")
        package_list = [i.split(":")[1] for i in sp.stdout.read().strip().split("\n")]
        self.package_combobox.addItems(package_list)

    def click_start_execute_btn(self):
        """
        点击开始执行
        :return:
        """
        self.log_text_edit.clear()      # 清除QTextEdit的log打印
        self.start_execute_btn.setEnabled(False)
        self.stop_execute_btn.setEnabled(True)
        self.export_log_btn.setEnabled(False)
        self.test_time_num_edit.setEnabled(False)
        self.throttle_num_edit.setEnabled(False)
        self.test_time.setText("00:00:00")
        self.initial_time = QTime(0, 0, 0)
        self.timer.start(1000)      # 每隔1秒发出timeout信号
        self.move_jar_todevice()    # 移到fastbot的jar到对应的设备

        self.test_process = QProcess()
        self.test_process.readyReadStandardOutput.connect(self.test_process_output)
        self.test_process.finished.connect(self.test_process_finished)
        adb_command = ['-s', self.device_combobox.currentText(), 'shell',
                       'CLASSPATH=/sdcard/monkeyq.jar:/sdcard/framework.jar:/sdcard/fastbot-thirdpart.jar',
                       'exec', 'app_process', '/system/bin', 'com.android.commands.monkey.Monkey',
                       '-p', self.package_combobox.currentText(), '--agent', 'reuseq', '--running-minutes',
                       self.test_time_num_edit.text(), '--throttle', self.throttle_num_edit.text(), '-v', '-v']
        self.test_process.start("adb", adb_command)

    def click_stop_execute_btn(self):
        """
        点击停止执行
        :return:
        """
        self.start_execute_btn.setEnabled(True)
        self.stop_execute_btn.setEnabled(False)
        self.export_log_btn.setEnabled(True)
        self.test_time_num_edit.setEnabled(True)
        self.throttle_num_edit.setEnabled(True)
        self.timer.stop()
        if self.test_process is not None:
            self.test_process.terminate()

    def update_time(self):
        """
        每秒更新下时间显示
        :return:
        """
        self.initial_time = self.initial_time.addSecs(1)    # 每秒增加1S
        time_text = self.initial_time.toString("hh:mm:ss")
        self.test_time.setText(time_text)

    def move_jar_todevice(self):
        """
        移动fastbot monkey的jar包到设备
        :return:
        """
        jar_path = os.path.join(".", "jar")
        for root, _, filenames in os.walk(jar_path):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                cmd = f"adb -s {self.device_combobox.currentText()} push {file_path} /sdcard"
                os.system(cmd)

    def test_process_output(self):
        """
        打印monkey log的进程
        :return:
        """
        data = self.test_process.readAllStandardOutput()
        output = bytes(data).decode().strip()
        self.log_text_edit.append(output)
        if "app_crash" in output:
            self.crash_num += 1
            self.crash_num_show.setText(self.crash_num)
        if "anr_com" in output:
            self.anr_num += 1
            self.anr_num_show.setText(self.anr_num)

    def test_process_finished(self):
        self.start_execute_btn.setEnabled(True)
        self.stop_execute_btn.setEnabled(False)
        self.export_log_btn.setEnabled(True)
        self.timer.stop()
        self.test_process.terminate()

    def export_files(self):
        file_dialog = QFileDialog()
        options = file_dialog.options()
        save_path, _ = file_dialog.getSaveFileName(self, "选择保存路径和文件夹名称", "",
                                                   "All Files (*);;Text Files (*.txt)", options=options)
        if save_path:
            save_dir = os.path.dirname(save_path)
            folder_name = os.path.basename(save_path)
            os.makedirs(os.path.join(save_dir, folder_name), exist_ok=True)

            monkey_log_path = os.path.join(save_path, "monkey.log")
            bugreport_filename = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "_bugreport.zip"
            with open(monkey_log_path, "w") as file:
                file.write(self.log_text_edit.toPlainText())
            adb_command_1 = f"adb -s {self.device_combobox.currentText()} /sdcard/fastbot-output/ {save_path}"
            # adb_command_2 = f"adb -s {self.device_combobox.currentText()} bugreport > {os.path.join(save_path, bugreport_filename)}"
            adb_command_3 = f"adb -s {self.device_combobox.currentText()} /sdcard/crash-dump.log {save_path}"
            os.system(adb_command_1)
            # os.system(adb_command_2)
            os.system(adb_command_3)
            QMessageBox.about(self, "导出", "导出成功！！！")

    def showEvent(self, event):
        """
        程序启动时，执行的事件
        :param event:
        :return:
        """
        super().showEvent(event)
        self.refresh_devices()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FastbotMonkey()
    window.show()
    sys.exit(app.exec())
