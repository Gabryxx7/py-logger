import time
from datetime import datetime
import colorama
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
import os
from pushbullet import PushBullet
from pywebio.input import *
from pywebio.output import *
from pywebio.session import *
import math
import re
import threading

class VLine(QFrame):
    # a simple VLine, like the one you get from designer
    def __init__(self):
        super(VLine, self).__init__()
        self.setFrameShape(self.VLine)
        self.setFrameShadow(self.Sunken)
class QtWaitingSpinner(QWidget):
    def __init__(self, parent, centerOnParent=True, disableParentWhenSpinning=False, modality=Qt.NonModal):
        super().__init__(parent)

        self._centerOnParent = centerOnParent
        self._disableParentWhenSpinning = disableParentWhenSpinning

        # WAS IN initialize()
        self._color = QColor("#4455ff")
        self._roundness = 100.0
        self._minimumTrailOpacity = 15
        self._trailFadePercentage = 50.0
        self._revolutionsPerSecond = 1.57079632679489661923
        self._numberOfLines = 21
        self._lineLength = 4
        self._lineWidth = 10
        self._innerRadius = 11
        self._currentCounter = 0
        self._isSpinning = False

        self._revolutionsPerSecond = 1.00

        self._timer = QTimer(self)
        self._timer.timeout.connect(self.rotate)
        self.updateBoundingBox()
        self.updateTimer()
        self.hide()
        # END initialize()

        self.setWindowModality(modality)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def paintEvent(self, QPaintEvent):
        self.updatePosition()
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.transparent)
        painter.setRenderHint(QPainter.Antialiasing, True)

        if self._currentCounter >= self._numberOfLines:
            self._currentCounter = 0

        painter.setPen(Qt.NoPen)
        for i in range(0, self._numberOfLines):
            painter.save()
            painter.translate(self._innerRadius + self._lineLength, self._innerRadius + self._lineLength)
            rotateAngle = float(360 * i) / float(self._numberOfLines)
            painter.rotate(rotateAngle)
            painter.translate(self._innerRadius, 0)
            distance = self.lineCountDistanceFromPrimary(i, self._currentCounter, self._numberOfLines)
            color = self.currentLineColor(distance, self._numberOfLines, self._trailFadePercentage,
                                          self._minimumTrailOpacity, self._color)
            painter.setBrush(color)
            painter.drawRoundedRect(QRect(0, -self._lineWidth / 2, self._lineLength, self._lineWidth), self._roundness,
                                    self._roundness, Qt.RelativeSize)
            painter.restore()

    def showSpinner(self):
        self.start()
        self.setVisible(True)

    def hideSpinner(self):
        self.stop()
        self.setVisible(False)

    def updateSize(self, size):
        self.setMinimumSize(size.height(), size.width())

    def start(self):
        self.updatePosition()
        self._isSpinning = True
        self.show()

        if self.parentWidget and self._disableParentWhenSpinning:
            self.parentWidget().setEnabled(False)

        if not self._timer.isActive():
            self._timer.start()
            self._currentCounter = 0

    def stop(self):
        self._isSpinning = False
        self.hide()

        if self.parentWidget() and self._disableParentWhenSpinning:
            self.parentWidget().setEnabled(True)

        if self._timer.isActive():
            self._timer.stop()
            self._currentCounter = 0

    def setNumberOfLines(self, lines):
        self._numberOfLines = lines
        self._currentCounter = 0
        self.updateTimer()

    def setLineLength(self, length):
        self._lineLength = length
        self.updateBoundingBox()

    def setLineWidth(self, width):
        self._lineWidth = width
        self.updateBoundingBox()

    def setInnerRadius(self, radius):
        self._innerRadius = radius
        self.updateBoundingBox()

    def color(self):
        return self._color

    def roundness(self):
        return self._roundness

    def minimumTrailOpacity(self):
        return self._minimumTrailOpacity

    def trailFadePercentage(self):
        return self._trailFadePercentage

    def revolutionsPersSecond(self):
        return self._revolutionsPerSecond

    def numberOfLines(self):
        return self._numberOfLines

    def lineLength(self):
        return self._lineLength

    def lineWidth(self):
        return self._lineWidth

    def innerRadius(self):
        return self._innerRadius

    def isSpinning(self):
        return self._isSpinning

    def setRoundness(self, roundness):
        self._roundness = max(0.0, min(100.0, roundness))

    def setColor(self, color=Qt.black):
        self._color = QColor(color)

    def setRevolutionsPerSecond(self, revolutionsPerSecond):
        self._revolutionsPerSecond = revolutionsPerSecond
        self.updateTimer()

    def setTrailFadePercentage(self, trail):
        self._trailFadePercentage = trail

    def setMinimumTrailOpacity(self, minimumTrailOpacity):
        self._minimumTrailOpacity = minimumTrailOpacity

    def rotate(self):
        self._currentCounter += 1
        if self._currentCounter >= self._numberOfLines:
            self._currentCounter = 0
        self.update()

    def updateBoundingBox(self):
        size = (self._innerRadius + self._lineLength) * 2
        self.setFixedSize(size, size)

    def updateTimer(self):
        self._timer.setInterval(1000 / (self._numberOfLines * self._revolutionsPerSecond))

    def updatePosition(self):
        if self.parentWidget() and self._centerOnParent:
            self.move(self.parentWidget().width() / 2 - self.width() / 2,
                      self.parentWidget().height() / 2 - self.height() / 2)

    def lineCountDistanceFromPrimary(self, current, primary, totalNrOfLines):
        distance = primary - current
        if distance < 0:
            distance += totalNrOfLines
        return distance

    def currentLineColor(self, countDistance, totalNrOfLines, trailFadePerc, minOpacity, colorinput):
        color = QColor(colorinput)
        if countDistance == 0:
            return color
        minAlphaF = minOpacity / 100.0
        distanceThreshold = int(math.ceil((totalNrOfLines - 1) * trailFadePerc / 100.0))
        if countDistance > distanceThreshold:
            color.setAlphaF(minAlphaF)
        else:
            alphaDiff = color.alphaF() - minAlphaF
            gradient = alphaDiff / float(distanceThreshold + 1)
            resultAlpha = color.alphaF() - gradient * countDistance
            # If alpha is out of bounds, clip it.
            resultAlpha = min(1.0, max(0.0, resultAlpha))
            color.setAlphaF(resultAlpha)
        return color

class LogColor():
    def __init__(self, name, code, html):
        self.color_name = name
        self.color_code = code
        self.color_html = html

class Log():
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                # another thread could have created the instance
                # before we acquired the lock. So check that the
                # instance is still nonexistent.
                if not cls._instance:
                    cls._instance = super(Log, cls).__new__(cls)
        return cls._instance

    def __init__(self, logs_folder="./Logs/"):
        self.logging_levels = {'a':0, 'd':1, 'i':2, 's':2, 'w':3, 'e':4}
        self.logs_folder = "./Logs/"
        self.log_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        if not os.path.exists(self.logs_folder):
            os.makedirs(self.logs_folder)
        self.log_file = None
        self.logWidget = None
        self.pb = None

        self.colors = {'red': LogColor('red', "\033[31m", "<font color=\"Red\">"),
                       'green': LogColor('green', "\033[32m", "<font color=\"Green\">"),
                       'white': LogColor('white', "\033[37m", "<font color=\"White\">"),
                       'blue': LogColor('blue', "\033[34m", "<font color=\"Cyan\">"),
                       'orange': LogColor('orange', "\033[93m", "<font color=\"Orange\">"),
                       'reset': LogColor('reset', "\033[0;0m", "</>")}
    
        self.general_enabled = True
        self.general_log_levels = list(self.logging_levels.keys())
        self.console_enabled = True
        self.console_log_levels = list(self.logging_levels.keys())
        self.widget_enabled = True
        self.widget_log_levels = list(self.logging_levels.keys())
        self.file_enabled = True
        self.file_log_levels = list(self.logging_levels.keys())
        self.pb_enabled = False
        self.pb_log_levels = ['s']

    def stop(self):
        if self.log_file is not None:
            self.log_file.close()
        
    def init_pushbullet(self, pb_access_token):
        try:
            self.pb = PushBullet(pb_access_token)
            self.pb_enabled = False
        except Exception as e:
            self.e("LOGGER", f"Error in initializing PushBullet, notifications DISABLED: {e}")

    def set_general_logging_level(self, min_level=-1, levels_list=None):
        if isinstance(min_level, str):
            min_level = self.logging_levels[min_level]
        if min_level > 0:
            self.general_log_levels = [list(self.logging_levels)[i] for i in range(0, min_level)]
        elif levels_list is not None:
            self.general_log_levels = levels_list if isinstance(levels_list, list) else [levels_list]
        self.i("LOGGER", f"General Logging Level Changed: {self.general_log_levels}")

    def set_console_logging_level(self, min_level=-1, levels_list=None):
        if isinstance(min_level, str):
            min_level = self.logging_levels[min_level]
        if min_level > 0:
            self.console_log_levels = [list(self.logging_levels)[i] for i in range(0, min_level)]
        elif levels_list is not None:
            self.console_log_levels = levels_list if isinstance(levels_list, list) else [levels_list]
        self.i("LOGGER", f"File Logging Level Changed: {self.console_log_levels}")

    def set_file_logging_level(self, min_level=-1, levels_list=None):
        if isinstance(min_level, str):
            min_level = self.logging_levels[min_level]
        if min_level > 0:
            self.file_log_levels = [list(self.logging_levels)[i] for i in range(0, min_level)]
        elif levels_list is not None:
            self.file_log_levels = levels_list if isinstance(levels_list, list) else [levels_list]
        self.i("LOGGER", f"File Logging Level Changed: {self.file_log_levels}")

    def set_pb_logging_level(self, min_level=-1, levels_list=None):
        if isinstance(min_level, str):
            min_level = self.logging_levels[min_level]
        if min_level > 0:
            self.pb_log_levels = [list(self.logging_levels)[i] for i in range(0, min_level)]
            self.pb_enabled = True
        elif levels_list is not None:
            self.pb_log_levels = levels_list if isinstance(levels_list, list) else [levels_list]
            self.pb_enabled = True
        self.i("LOGGER", f"PushBullet Logging Level Changed: {self.pb_log_levels}")

    def set_widget_logging_level(self, min_level=-1, levels_list=None):
        if isinstance(min_level, str):
            min_level = self.logging_levels[min_level]
        if min_level > 0:
            self.widget_log_levels = [list(self.logging_levels)[i] for i in range(0, min_level)]
        elif levels_list is not None:
            self.widget_log_levels = levels_list if isinstance(levels_list, list) else [levels_list]
        self.i("LOGGER", f"Widget Logging Level Changed: {self.widget_log_levels}")

    def get_logging_level_index(self, level_key):
        return list(self.logging_levels.keys()).index(level_key)

    def toggle_general_logging(self, enabled):
        self.i("LOGGER", "Logging has been " + self.status_string(enabled))
        self.general_enabled = enabled

    def toggle_console_logging(self, enabled):
        self.i("LOGGER", "Logging CONSOLE has been " + self.status_string(enabled))
        self.general_enabled = enabled

    def toggle_widget_logging(self, enabled):
        self.i("LOGGER", "Logging WIDGET has been " + self.status_string(enabled))
        self.widget_enabled = enabled

    def toggle_file_logging(self, enabled):
        self.i("LOGGER", "Logging FILE has been " + self.status_string(enabled)+": " + os.path.abspath(self.log_filename))
        self.file_enabled = enabled
    
    def toggle_pushbullet(self, enabled):
        self.i("LOGGER", "Logging PUSHBULLET has been " + self.status_string(enabled)+": " + os.path.abspath(self.log_filename))
        self.pb_enabled = enabled

    def status_string(self, status):
        if status:
            return "ENABLED"
        else:
            return  "DISABLED"

    def w(self, tag="", text="", to_console=True, to_widget=True, to_file=True, to_pb=True):
        self.print("orange", tag, text, 'w',to_console, to_widget, to_file, to_pb)

    def d(self, tag="", text="", to_console=True, to_widget=True, to_file=True, to_pb=True):
        self.print("blue", tag, text, 'd',to_console, to_widget, to_file, to_pb)

    def e(self, tag="", text="", to_console=True, to_widget=True, to_file=True, to_pb=True):
        self.print("red", tag, text, 'e',to_console, to_widget, to_file, to_pb)

    def s(self, tag="", text="", to_console=True, to_widget=True, to_file=True, to_pb=True):
        self.print("green", tag, text, 's',to_console, to_widget, to_file, to_pb)

    def i(self, tag, text, to_console=True, to_widget=True, to_file=True, to_pb=True):
        self.print("white", tag, text, 'i',to_console, to_widget, to_file, to_pb)

    def print(self, color_name, tag, text, log_level, to_console=True, to_widget=True, to_file=True, to_pb=True):
        if self.general_enabled:
            color = self.colors[color_name]
            color_reset = self.colors['reset']
            if log_level in self.general_log_levels:
                dateTimeObj = datetime.now()
                timestampStr = f"{dateTimeObj.strftime('%d-%b-%Y %H:%M:%S')} - "
                timestamp_length = len(timestampStr)
                if tag != "":
                    tag_txt = "["+str(tag)+"]"
                log_text = f"{log_level}{tag_txt}: {text}"
                log_text = log_text.replace("\n", f"\n{'':<{timestamp_length}}")
                if self.widget_enabled and to_widget and self.logWidget is not None:
                    if log_level in self.widget_log_levels:
                        try:
                            final_text = f"{timestampStr:<{timestamp_length}}{color.color_html}{log_text}{color_reset.color_html}"
                            self.logWidget.append(final_text + "\n")
                        except Exception as e:
                            print("Exception writing to LOG Widget:" + str(e))
                if self.console_enabled:
                    if log_level in self.console_log_levels:
                        final_text = f"{timestampStr:<{timestamp_length}}{color.color_code}{log_text}{color_reset.color_code}"
                        print(final_text)
                if self.file_enabled:
                    if log_level in self.file_log_levels:
                        final_text = f"{timestampStr:<{timestamp_length}}{log_text}\n"
                        try:
                            with open(f"{self.logs_folder}{self.log_filename}", "w+") as log_file:
                                log_file.write(final_text)
                                log_file.flush()
                        except Exception as e:
                            print("Exception writing to LOG File:" +str(e))
                if self.pb_enabled:
                    if log_level in self.pb_log_levels:
                        self.pb.push_note("Logger Test", f"{timestampStr:<{timestamp_length}}{log_text}")

    def create_log_widget(self):
        self.logWidget = LogWidget(self)

class LogWidget(QWidget):
    def __init__(self, logger):
        super(LogWidget, self).__init__()
        self.main_layout = QVBoxLayout()
        self.extra_layout = QHBoxLayout()
        self.logger = logger
        self.font_family = "Courier New"
        self.font_size = 9
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setFont(QFont(self.font_family, self.font_size))

        self.title = QLabel("LOG")
        self.filter_label = QLabel("Filter level:")
        self.filter_combobox = QComboBox()
        for key in self.logger.logging_levels.keys():
            self.filter_combobox.addItem(str(self.logger.logging_levels[key]) + " - " + key, key)
        # self.filter_combobox.currentIndexChanged.connect(self.on_combobox_changed)
        self.general_checkbox = QCheckBox("Enable")
        self.general_checkbox.stateChanged.connect(self.general_checkbox_changed)
        self.console_checkbox = QCheckBox("Console")
        self.console_checkbox.stateChanged.connect(self.console_checkbox_changed)
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

    def append(self, text):
        self.text_area.append(text)
        # self.text_area.moveCursor(QTextCursor.End)
        self.text_area.verticalScrollBar().setValue(self.text_area.verticalScrollBar().maximum())

    def on_combobox_changed(self, value):
        self.logger.set_general_logging_level(min_level=self.filter_combobox.itemData(value))

    def general_checkbox_changed(self, value):
        self.logger.toggle_general_logging(value)
        self.check_log_status()

    def console_checkbox_changed(self, value):
        self.logger.toggle_console_logging(value)
        self.check_log_status()

    def widget_checkbox_changed(self, value):
        self.logger.toggle_widget_logging(value)
        self.check_log_status()

    def file_checkbox_changed(self, value):
        self.logger.toggle_file_logging(value)
        self.check_log_status()

    def pb_checkbox_changed(self, value):
        self.logger.toggle_pushbullet(value)
        self.check_log_status()

    def check_log_status(self):
        self.filter_combobox.setCurrentIndex(self.logger.get_logging_level_index(self.logger.general_log_levels[-1]))

        self.general_checkbox.setChecked(self.logger.general_enabled)
        self.console_checkbox.setChecked(self.logger.console_enabled)
        self.widget_checkbox.setChecked(self.logger.widget_enabled)
        self.file_checkbox.setChecked(self.logger.file_enabled)
        self.pb_checkbox.setChecked(self.logger.pb_enabled)

class LoggableTaskSignals(QObject):
    started = Signal(str, dict)
    updated = Signal(str, dict)
    completed = Signal(str, dict)

class LoggableTaskWorker(QRunnable):
    def __init__(self, tag="LoggableTaskWorker"):
        super(LoggableTaskWorker, self).__init__()
        self.tag = tag
        self.log_signals = LoggableTaskSignals()

class BackgroundTasksLogger(QWidget):
    def __init__(self, app, *args, **kwargs):
        super(BackgroundTasksLogger, self).__init__(*args, **kwargs)
        self.app = app
        self.log = self.app.log
        self.background_tasks_list = []
        self.background_info = QLabel("No background stuff!")
        self.background_count_label = QLabel("")
        self.background_completed = 0
        self.background_count_total = 0
        self.spinner = QtWaitingSpinner(self, centerOnParent=False)
        self.spinner.hideSpinner()
        self.spinner.updateSize(QSize(30,30))

        self.hbox = QHBoxLayout()

        self.hbox.addWidget(VLine())
        self.hbox.addWidget(self.background_info)
        self.hbox.addWidget(self.spinner)
        self.hbox.addWidget(self.background_count_label)
        self.hbox.setContentsMargins(0,0,0,0)

        self.setLayout(self.hbox)

    # Incremental task numbering
    def get_new_task_number(self, tag):
        while tag in self.background_tasks_list:
            string_matches = re.match(r"(.*)([0-9]+)", tag)
            if string_matches is not None:
                # print("string_matches: " +str(string_matches.groups()))
                tag = string_matches.group(1)+str(int(string_matches.group(2))+1)
            else:
                tag += "_1"
        return tag

    def addBackgroundTask(self, task, info=""):
        if task.tag is not None:
            task.tag = self.get_new_task_number(task.tag)
        self.background_tasks_list.append(task.tag)
        self.updateBackgroundTaskInfo(info)
        self.background_count_total += 1
        if self.background_count_total <= 1:
            self.spinner.showSpinner()
            self.background_count_label.setVisible(True)
        self.updateBackgroundTaskCount()
        task.log_signals.started.connect(self.updateBackgroundTaskInfo)
        task.log_signals.updated.connect(self.updateBackgroundTaskInfo)
        task.log_signals.completed.connect(self.updateBackgroundTaskInfo)
        self.log.d("THREADS", "Added new background task " +str(info) +" " +str(self.background_completed) + "/" + str(self.background_count_total) +" Tasks: " +str(self.background_tasks_list), False)
        return task

    def updateBackgroundTaskCount(self):
        self.background_count_label.setText(str(self.background_completed) +"/"+str(self.background_count_total))
        
    def updateBackgroundTaskInfo(self, tag="", info=""):
        self.background_info.setText(str(info))
        self.log.d(tag, str(info))
        
    def completeBackgroundTask(self, tag="", info=""):
        if info != "":
            self.updateBackgroundTaskInfo(info)
        if tag is not None and tag in self.background_tasks_list:
            self.background_tasks_list.remove(tag)
        self.background_completed += 1
        if self.background_completed >= self.background_count_total:
            self.background_count_total = 0
            self.background_completed = 0
            self.spinner.hideSpinner()
            self.updateBackgroundTaskInfo("All tasks completed!")
            self.background_count_label.setVisible(False)
        self.updateBackgroundTaskCount()
        self.log.d("THREADS", "Completed background task " +str(info) +" " +str(self.background_completed) + "/" + str(self.background_count_total) +" Tasks: " +str(self.background_tasks_list), False)

