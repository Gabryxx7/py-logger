import threading

class Singleton:
  def __init__(self, cls):
    self._cls = cls
    self._lock = threading.Lock()

  def Instance(self):
    try:
      return self._instance
    except AttributeError:
      with self._lock:
        # another thread could have created the instance
        # before we acquired the lock. So check that the
        # instance is still nonexistent.
        self._instance = self._cls()
      return self._instance

  def __call__(self):
    raise TypeError('Singletons must be accessed through `Instance()`.')

  def __instancecheck__(self, inst):
    return isinstance(inst, self._cls)

@Singleton
class Log(object):
  def __init__(self):
    self.widgets = []
    self.global_tag = ""
      
  def add_widget(self, widget):
    for log_w in self.widgets:
      if log_w.tag == widget.tag:
        print(f"Log Widget {widget.tag} already added!")
        return
    print(f"Adding Log Widget {widget.tag}")
    self.widgets.append(widget)

  def set_global_tag(self, tag):
    self.global_tag = tag
      
  def w(self, text, tag=None, **kwargs):
    return self.append(text, tag, 'w', **kwargs)

  def d(self, text, tag=None, **kwargs):
    return self.append(text, tag, 'd', **kwargs)

  def e(self, text, tag=None, **kwargs):
    return self.append(text, tag, 'e', **kwargs)

  def s(self, text, tag=None, **kwargs):
    return self.append(text, tag, 's', **kwargs)

  def i(self, text, tag=None, **kwargs):
    return self.append(text, tag, 'i', **kwargs)

  def append(self, text, tag=None, log_level='a', **kwargs):
    tag = self.global_tag if tag is None else tag
    pos = 0
    for widget in self.widgets:
      res = widget.append(text, tag, log_level, **kwargs)    
      if res is not None:
        pos = res      
    return pos
    # if self.enabled:
    #     color = self.colors[color_name]
    #     color_reset = self.colors['reset']
    #     if self.log_levels[log_level] >= self.log_levels[self.min_log_level]:
    #         if self.enable_widget and log_to_widget and self.logWidget is not None:
    #             try:
    #                 final_text = timestampStr + color.color_html + " " + log_text + color_reset.color_html
    #                 self.logWidget.append(final_text + "\n")
    #             except Exception as e:
    #                 print("Exception writing to LOG Widget:" + str(e))
    #                 pass
    #         if self.enable_console:
    #             final_text = timestampStr + color.color_code + " " + log_text + color_reset.color_code
    #             print(final_text)
    #         if self.save_to_file:
    #             try:
    #                 self.file.write(timestampStr + log_text + "\n")
    #             except Exception as e:
    #                 print("Exception writing to LOG File:" +str(e))
    #                 pass
      
  def flush(self, **kwargs):
    for widget in self.widgets:
      widget.flush_lines(**kwargs)
          
  def init(self):
    for widget in self.widgets:
      widget.init()
      
  def destroy(self):
    for widget in self.widgets:
      widget.destroy()

import time
from datetime import datetime
import colorama
import os

""" Logging meta classes """
class LogLevel():    
    class LogColor:
        def __init__(self, name, code, html, rgb):
            self.name = name
            self.code = code
            self.html = html
            self.rgb = rgb
        
    def __init__(self, level, name, description, code, html, rgb):
        self.color = self.LogColor(name, code, html, rgb)
        self.level = level
        self.name = name

class LogWidgetMeta:
    log_levels = {  'a': LogLevel(0, 'all', 'white', "\033[37m", "<font color=\"White\">", (255,255,255)),  
                    'd': LogLevel(1, 'debug', 'blue', "\033[94m", "<font color=\"Blue\">", (0,0,255)),
                    'i': LogLevel(2, 'info', 'white', "\033[37m", "<font color=\"White\">", (255,255,255)),
                    's': LogLevel(2, 'success', 'green', "\033[92m", "<font color=\"Green\">", (0,255,0)),
                    'w': LogLevel(3, 'warning', 'orange', "\033[93m", "<font color=\"Orange\">", (255,155,0)),
                    'e': LogLevel(4, 'exception', 'red', "\033[91m", "<font color=\"Red\">", (255,0,0)),
                }
        
    def __init__(self, min_log_level='a', auto_flush=False):
        self.tag = "LogWidgetMeta"
        self.min_log_level = 'a'
        self.log_level = self.min_log_level
        self.color_reset = LogLevel.LogColor('reset', "\033[0;0m", "</>", (255,255,255))
        self.enabled = True
        self.auto_flush = auto_flush
        self.text_lines = []

    def set_min_log_level(self, level):
        self.i("LOGGER", f"{self.tag} Logging Level Changed: {self.min_log_level} - {str(self.log_levels[self.min_log_level])}")
        self.min_log_level = level

    def get_min_log_level_index(self):
        return list(self.log_levels.keys()).index(self.min_log_level)

    def setEnabled(self, enabled):
        self.i("LOGGER", f"Logging has been {self.status_string(enabled)}") 
        self.enabled = enabled
        
    def status_string(self, status):
        return "ENABLED" if status else "DISABLED"
    
    def format_txt(self, text, tag, no_date, log_level='a', **kwargs):    
        if self.log_levels[log_level].level < self.log_levels[self.min_log_level].level:
            return None
        
        timestampStr = ""
        if not no_date:
            dateTimeObj = datetime.now()
            timestampStr = dateTimeObj.strftime("%d-%b-%Y %H:%M:%S") + " - "
        log_text = f"{timestampStr}{log_level.upper()}[{tag}]: {text}"
        return log_text
    
    # To be overridden
    def append(self, text, tag, log_level, no_date=False, flush=None, **kwargs):
        text = self.format_txt(text, tag, no_date, log_level, **kwargs)
        self.text_lines.append(text)
        flush = self.auto_flush if flush is None else flush
        if flush:
            self.flush_lines()
        return None

    # To be overridden
    def flush_lines(self):
        pass    

    # To be overridden
    def destroy(self):
        pass

    # To be overridden
    def check_log_status(self, text):
        pass

    # To be overridden
    def on_logging_level_changed(self, new_logging_level):
        pass

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
    def __init__(self, tag="LoggableTaskWorker", id=""):
        super(LoggableTaskWorker, self).__init__()
        self.tag = tag
        self.tag = f"{self.tag}{id}"
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
    def append(self, text, tag, log_level='a', no_date=False, flush=True, **kwargs):
        text = self.format_txt(text, tag, no_date, log_level, **kwargs)
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


