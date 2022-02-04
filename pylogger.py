import time
from datetime import datetime
import colorama
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from GUI.log_widget import LogWidget
import os
from pushbullet import PushBullet
from pywebio.input import *
from pywebio.output import *
from pywebio.session import *


class Singleton:
    def __init__(self, cls):
        self._cls = cls

    def Instance(self):
        try:
            return self._instance
        except AttributeError:
            self._instance = self._cls()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._cls)

class LogColor():
    def __init__(self, name, code, html):
        self.color_name = name
        self.color_code = code
        self.color_html = html

@Singleton
class Log(object):
    def __init__(self):
        self.logging_levels = {'a':0, 'd':1, 'i':2, 's':2, 'w':3, 'e':4}
        self.min_level = 'a'
        self.log_file = "log.txt"
        self.file = open(self.log_file, "w+")
        self.enabled = True
        self.enable_console = True
        self.enable_widget = True
        self.save_to_file = True
        self.logWidget = None

        self.colors = {'red': LogColor('red', "\033[91m", "<font color=\"Red\">"),
                       'green': LogColor('green', "\033[92m", "<font color=\"Green\">"),
                       'white': LogColor('white', "\033[37m", "<font color=\"White\">"),
                       'blue': LogColor('blue', "\033[94m", "<font color=\"Blue\">"),
                       'orange': LogColor('orange', "\033[93m", "<font color=\"Orange\">"),
                       'reset': LogColor('orange', "\033[0;0m", "</>")}

    def set_min_level(self, level):
        self.i("LOGGER", "Logging Level Changed: " + self.min_level + " - " + str(self.logging_levels[self.min_level]))
        self.min_level = level

    def get_min_level_index(self):
        return list(self.logging_levels.keys()).index(self.min_level)

    def toggle_general(self, enabled):
        self.i("LOGGER", "Logging has been " + self.status_string(enabled))
        self.enabled = enabled

    def toggle_console(self, enabled):
        self.i("LOGGER", "Logging CONSOLE has been " + self.status_string(enabled))
        self.enable_console = enabled

    def toggle_widget(self, enabled):
        self.i("LOGGER", "Logging WIDGET has been " + self.status_string(enabled))
        self.enable_widget = enabled

    def toggle_file(self, enabled):
        self.i("LOGGER", "Logging FILE has been " + self.status_string(enabled)+": " + os.path.abspath(self.log_file))
        self.save_to_file = enabled
    
    def toggle_pushbullet(self, enabled):
        self.i("LOGGER", "Logging PUSHBULLET has been " + self.status_string(enabled)+": " + os.path.abspath(self.log_file))
        self.save_to_file = enabled

    def status_string(self, status):
        if status:
            return "ENABLED"
        else:
            return  "DISABLED"

    def w(self, tag, text, log_to_widget=True):
        self.print("orange", tag, text, 'w', log_to_widget)

    def d(self, tag, text, log_to_widget=True):
        self.print("blue", tag, text, 'd', log_to_widget)

    def e(self, tag, text, log_to_widget=True):
        self.print("red", tag, text, 'e', log_to_widget)

    def s(self, tag, text, log_to_widget=True):
        self.print("green", tag, text, 's', log_to_widget)

    def i(self, tag, text, log_to_widget=True):
        self.print("white", tag, text, 'i', log_to_widget)

    def print(self, color_name, tag, text, log_level, log_to_widget=True):
        if self.enabled:
            color = self.colors[color_name]
            color_reset = self.colors['reset']
            if self.logging_levels[log_level] >= self.logging_levels[self.min_level]:
                dateTimeObj = datetime.now()
                timestampStr = dateTimeObj.strftime("%d-%b-%Y %H:%M:%S") + " - "
                log_text = log_level + "["+str(tag)+"]: " +str(text)
                if self.enable_widget and log_to_widget and self.logWidget is not None:
                    try:
                        final_text = timestampStr + color.color_html + " " + log_text + color_reset.color_html
                        self.logWidget.append(final_text + "\n")
                    except Exception as e:
                        print("Exception writing to LOG Widget:" + str(e))
                        pass
                if self.enable_console:
                    final_text = timestampStr + color.color_code + " " + log_text + color_reset.color_code
                    print(final_text)
                if self.save_to_file:
                    try:
                        self.file.write(timestampStr + log_text + "\n")
                    except Exception as e:
                        print("Exception writing to LOG File:" +str(e))
                        pass

    def create_log_widget(self):
        self.logWidget = LogWidget(self)


class LogWidget(QWidget):
    def __init__(self, logger):
        super(LogWidget, self).__init__()
        self.main_layout = QVBoxLayout()
        self.extra_layout = QHBoxLayout()
        self.logger = logger
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setFont(QFont("Courier New", 9))

        self.title = QLabel("LOG")
        self.filter_label = QLabel("Filter level:")
        self.filter_combobox = QComboBox()
        for key in self.logger.logging_levels.keys():
            self.filter_combobox.addItem(str(self.logger.logging_levels[key]) + " - " + key, key)
        self.filter_combobox.currentIndexChanged.connect(self.on_combobox_changed)
        self.enable_checkbox = QCheckBox("Enable")
        self.enable_checkbox.stateChanged.connect(self.enable_checkbox_changed)
        self.console_checkbox = QCheckBox("Console")
        self.console_checkbox.stateChanged.connect(self.console_checkbox_changed)
        self.widget_checkbox = QCheckBox("Widget")
        self.widget_checkbox.stateChanged.connect(self.widget_checkbox_changed)
        self.file_checkbox = QCheckBox("File")
        self.file_checkbox.stateChanged.connect(self.file_checkbox_changed)

        self.extra_layout.addWidget(self.title)
        self.extra_layout.addWidget(self.filter_label)
        self.extra_layout.addWidget(self.filter_combobox)
        self.extra_layout.addWidget(self.enable_checkbox)
        self.extra_layout.addWidget(self.console_checkbox)
        self.extra_layout.addWidget(self.widget_checkbox)
        self.extra_layout.addWidget(self.file_checkbox)
        self.extra_layout.addStretch(1)

        self.main_layout.addLayout(self.extra_layout)
        self.main_layout.addWidget(self.text_area)
        self.check_log_status()

        self.setLayout(self.main_layout)

    def append(self, text):
        self.text_area.append(text)
        # self.text_area.moveCursor(QTextCursor.End)
        self.text_area.verticalScrollBar().setValue(self.text_area.verticalScrollBar().maximum())

    def on_combobox_changed(self, value):
        self.logger.set_min_level(self.filter_combobox.itemData(value))

    def enable_checkbox_changed(self, value):
        self.logger.setEnabled(value)
        self.check_log_status()

    def console_checkbox_changed(self, value):
        self.logger.setConsoleEnabled(value)
        self.check_log_status()

    def widget_checkbox_changed(self, value):
        self.logger.setWidgetEnabled(value)
        self.check_log_status()

    def file_checkbox_changed(self, value):
        self.logger.setFileEnabled(value)
        self.check_log_status()

    def check_log_status(self):
        self.filter_combobox.setCurrentIndex(self.logger.get_min_level_index())

        self.enable_checkbox.setChecked(self.logger.enabled)
        self.console_checkbox.setChecked(self.logger.enable_console)
        self.widget_checkbox.setChecked(self.logger.enable_widget)
        self.file_checkbox.setChecked(self.logger.save_to_file)

        self.console_checkbox.setEnabled(self.logger.enabled)
        self.widget_checkbox.setEnabled(self.logger.enabled)
        self.file_checkbox.setEnabled(self.logger.enabled)