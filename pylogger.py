import time
from datetime import datetime
import colorama
from PySide2.QtGui import *
from PySide2.QtWidgets import *
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
        self.logs_folder = "./Logs/"
        self.log_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        if not os.path.exists(self.logs_folder):
            os.makedirs(self.logs_folder)
        self.log_file = open(self.logs_folder+self.log_filename, "w+")
        self.enabled = True
        self.enable_console = True
        self.enable_widget = True
        self.save_to_file = True
        self.logWidget = None
        self.pb = None
        self.pb_enabled = False
        self.pb_notif_levels = []

        self.colors = {'red': LogColor('red', "\033[91m", "<font color=\"Red\">"),
                       'green': LogColor('green', "\033[92m", "<font color=\"Green\">"),
                       'white': LogColor('white', "\033[37m", "<font color=\"White\">"),
                       'blue': LogColor('blue', "\033[94m", "<font color=\"Blue\">"),
                       'orange': LogColor('orange', "\033[93m", "<font color=\"Orange\">"),
                       'reset': LogColor('orange', "\033[0;0m", "</>")}
    def init_pushbullet(self, pb_access_token, min_notif_level=-1, notif_levels=None):
        self.pb = PushBullet(pb_access_token)
        self.pb_enabled = False
        if min_notif_level > 0:
            self.pb_notif_levels = range(min_notif_level, len(self.logging_levels))
            self.pb_enabled = True
        elif notif_levels is not None:
            self.pb_notif_levels = notif_levels
            self.pb_enabled = True


    def set_min_level(self, level):
        self.i("LOGGER", "Logging Level Changed: " + self.min_level + " - " + str(self.logging_levels[self.min_level]))
        self.min_level = level

    def get_min_level_index(self):
        return list(self.logging_levels.keys()).index(self.min_level)

    def toggle_general_logging(self, enabled):
        self.i("LOGGER", "Logging has been " + self.status_string(enabled))
        self.enabled = enabled

    def toggle_console_logging(self, enabled):
        self.i("LOGGER", "Logging CONSOLE has been " + self.status_string(enabled))
        self.enable_console = enabled

    def toggle_widget_logging(self, enabled):
        self.i("LOGGER", "Logging WIDGET has been " + self.status_string(enabled))
        self.enable_widget = enabled

    def toggle_file_logging(self, enabled):
        self.i("LOGGER", "Logging FILE has been " + self.status_string(enabled)+": " + os.path.abspath(self.log_filename))
        self.save_to_file = enabled
    
    def toggle_pushbullet(self, enabled):
        self.i("LOGGER", "Logging PUSHBULLET has been " + self.status_string(enabled)+": " + os.path.abspath(self.log_filename))
        self.pb_enabled = enabled

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
                        self.log_file.write(timestampStr + log_text + "\n")
                    except Exception as e:
                        print("Exception writing to LOG File:" +str(e))
                        pass
                if self.pb_enabled:
                    pb.push_note("Logger Test", f"{timestampStr}{log_text}")

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
        self.log_file_checkbox = QCheckBox("File")
        self.log_file_checkbox.stateChanged.connect(self.log_file_checkbox_changed)

        self.extra_layout.addWidget(self.title)
        self.extra_layout.addWidget(self.filter_label)
        self.extra_layout.addWidget(self.filter_combobox)
        self.extra_layout.addWidget(self.enable_checkbox)
        self.extra_layout.addWidget(self.console_checkbox)
        self.extra_layout.addWidget(self.widget_checkbox)
        self.extra_layout.addWidget(self.log_file_checkbox)
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
        self.logger.toggle_general_logging(value)
        self.check_log_status()

    def console_checkbox_changed(self, value):
        self.logger.toggle_console_logging(value)
        self.check_log_status()

    def widget_checkbox_changed(self, value):
        self.logger.toggle_widget_logging(value)
        self.check_log_status()

    def log_file_checkbox_changed(self, value):
        self.logger.toggle_file_logging(value)
        self.check_log_status()

    def check_log_status(self):
        self.filter_combobox.setCurrentIndex(self.logger.get_min_level_index())

        self.enable_checkbox.setChecked(self.logger.enabled)
        self.console_checkbox.setChecked(self.logger.enable_console)
        self.widget_checkbox.setChecked(self.logger.enable_widget)
        self.log_file_checkbox.setChecked(self.logger.save_to_file)

        self.console_checkbox.setEnabled(self.logger.enabled)
        self.widget_checkbox.setEnabled(self.logger.enabled)
        self.log_file_checkbox.setEnabled(self.logger.enabled)