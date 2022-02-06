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

        self.colors = {'red': LogColor('red', "\033[31m", "<font color=\"Red\">"),
                       'green': LogColor('green', "\033[32m", "<font color=\"Green\">"),
                       'white': LogColor('white', "\033[37m", "<font color=\"White\">"),
                       'blue': LogColor('blue', "\033[34m", "<font color=\"Cyan\">"),
                       'orange': LogColor('orange', "\033[93m", "<font color=\"Orange\">"),
                       'reset': LogColor('reset', "\033[0;0m", "</>")}
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

