from .widget_meta import LogWidgetMeta
from .qt_background_info_widget import BackgroundTasksInfoWidget
from typing import overload
from PySide6.QtWidgets import *
# from PySide6.QtWidgets.QFrame import *
from PySide6.QtCore import *
from PySide6.QtGui import *


class LoggableTaskSignals(QObject):
    started = Signal(str, dict)
    updated = Signal(str, dict)
    completed = Signal(str, dict)

class LoggableTaskWorker(QRunnable):
    def __init__(self, tag="LoggableTaskWorker"):
        super(LoggableTaskWorker, self).__init__()
        self.tag = tag
        self.logger_signals = LoggableTaskSignals()

class QTLogWidget(QWidget, LogWidgetMeta):
    def __init__(self):
        super(QTLogWidget, self).__init__()
        self.main_layout = QVBoxLayout()
        self.extra_layout = QHBoxLayout()
        self.font_family = "Courier New"
        self.font_size = 10
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setFont(QFont(self.font_family, self.font_size))

        self.title = QLabel("LOG")
        self.filter_label = QLabel("Filter level:")
        self.filter_combobox = QComboBox()
        for key in self.log_levels.keys():
            self.filter_combobox.addItem(str(self.log_levels[key].name) + " - " + key, key)
        # self.filter_combobox.currentIndexChanged.connect(self.on_combobox_changed)
        self.general_checkbox = QCheckBox("Enable")
        self.general_checkbox.stateChanged.connect(
            self.general_checkbox_changed)
        self.console_checkbox = QCheckBox("Console")
        self.console_checkbox.stateChanged.connect(
            self.console_checkbox_changed)
        self.widget_checkbox = QCheckBox("Widget")
        self.widget_checkbox.stateChanged.connect(self.widget_checkbox_changed)
        self.file_checkbox = QCheckBox("File")
        self.file_checkbox.stateChanged.connect(self.file_checkbox_changed)
        self.pb_checkbox = QCheckBox("PB")
        self.pb_checkbox.stateChanged.connect(self.pb_checkbox_changed)
        self.extra_layout.addWidget(self.title)
        self.extra_layout.addWidget(self.filter_label)
        self.extra_layout.addWidget(self.filter_combobox)
        self.extra_layout.addWidget(self.general_checkbox)
        self.extra_layout.addWidget(self.console_checkbox)
        self.extra_layout.addWidget(self.widget_checkbox)
        self.extra_layout.addWidget(self.file_checkbox)
        self.extra_layout.addWidget(self.pb_checkbox)
        self.extra_layout.addStretch(1)

        self.main_layout.addLayout(self.extra_layout)
        self.main_layout.addWidget(self.text_area)
        self.check_log_status()

        self.setLayout(self.main_layout)

    def set_font_family(self, font_family):
        self.font_family = font_family
        self.text_area.setFont(QFont(self.font_family, self.font_size))

    def set_font_size(self, font_size):
        self.font_size = font_size
        self.text_area.setFont(QFont(self.font_family, self.font_size))

    # @overload
    def append(self, tag, text, log_level='a', no_date=False, flush=True, **kwargs):
        text = self.format_txt(tag, text, no_date, log_level, **kwargs)
        color = LogWidgetMeta.log_levels[log_level].color.html
        final_text = f"{color}{text}{self.color_reset.html}"
        self.text_lines.append(final_text)
        if flush:
            self.flush_lines()
        return None
            
    # @overload
    def flush_lines(self): 
        while len(self.text_lines) > 0:
            line = self.text_lines.pop()
            self.text_area.append(line)
        # self.text_area.moveCursor(QTextCursor.End)
        self.text_area.verticalScrollBar().setValue(self.text_area.verticalScrollBar().maximum())

    def on_combobox_changed(self, value):
        return
        self.logger.set_general_logging_level(min_level=self.filter_combobox.itemData(value))

    def general_checkbox_changed(self, value):
        return
        self.logger.toggle_general_logging(value)
        self.check_log_status()

    def console_checkbox_changed(self, value):
        return
        self.logger.toggle_console_logging(value)
        self.check_log_status()

    def widget_checkbox_changed(self, value):
        return
        self.logger.toggle_widget_logging(value)
        self.check_log_status()

    def file_checkbox_changed(self, value):
        return
        self.logger.toggle_file_logging(value)
        self.check_log_status()

    def pb_checkbox_changed(self, value):
        return
        self.logger.toggle_pushbullet(value)
        self.check_log_status()

    # @overload
    def check_log_status(self):
        return
        self.filter_combobox.setCurrentIndex(
            self.logger.get_logging_level_index(self.logger.general_log_levels[-1]))

        self.general_checkbox.setChecked(self.logger.general_enabled)
        self.console_checkbox.setChecked(self.logger.console_enabled)
        self.widget_checkbox.setChecked(self.logger.widget_enabled)
        self.file_checkbox.setChecked(self.logger.file_enabled)
        self.pb_checkbox.setChecked(self.logger.pb_enabled)

