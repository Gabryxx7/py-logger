
"""
Author: @Gabryxx7 (https://github.com/Gabryxx7/)
Repo: https://github.com/Gabryxx7/py-logger
Updated: 09-10-2024
"""

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
        
    def __call__(self, **kwargs):
        return self.d(**kwargs)

    def add_widget(self, widget):
        for log_w in self.widgets:
            if log_w.tag == widget.tag:
                print(f"Log Widget {widget.tag} already added!")
                return
        print(f"Adding Log Widget {widget.tag}")
        self.widgets.append(widget)
        return self

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

from typing import overload
from .ui_widget import VisualLogWidget

class PyGameLogWidget(VisualLogWidget):
    def __init__(self, min_log_level='a', pygame=None, font=None, font_size=16, canvas=None, id=""):
        super(PyGameLogWidget, self).__init__(min_log_level, drawer=pygame, draw_type=VisualLogWidget.Type.PYGAME, canvas=canvas)
        self.tag = "PyGameLogWidget"
        self.tag = f"{self.tag}{id}"
        self.font = pygame.font.SysFont('Arial', 16) if font is None else font
        self.font_size = font_size
        self.line_height = self.font_size*0.8
            
    # @overload
    def append(self, text, tag, log_level, flush=False, color=None, pos=None, font=None, font_size=1, line_height=None, **kwargs):
        return super().append(text, tag, log_level, flush, color, pos, font, font_size, line_height, **kwargs)
    
    # @overload
    def flush_lines(self, draw=True, canvas=None, debug=False):
        super().flush_lines(draw, canvas, debug)
        while len(self.text_lines) > 0:
            line = self.text_lines.pop()
            if draw:
                try:
                    self.draw_text_line(line, canvas)
                except Exception as e:
                    print(f"[{self.tag}] Error printing line '{line.text}': {e}")
        if debug:
            print(f"[{self.tag}] Remaining {len(self.text_lines)} lines")
            
    def draw_text_line(self, line, canvas=None):
        canvas = self.canvas if canvas is None else canvas
        canvas.blit(line.font.render(line.text, True, line.color), (int(line.pos.x), int(line.pos.y)))
    
    def draw_line(self, start, end, color, thickness):
        self.drawer.draw.line(self.canvas, color=color, start_pos=(int(start.x), int(start.y)), end_pos=(int(end.x), int(end.y)), width=thickness)
        
    def draw_circle(self, center, color, radius, thickness):
        self.drawer.draw.circle(self.canvas, color=color, center=(int(center.x), int(center.y)), radius=radius, width=thickness)

from typing import overload

class PushbulletLogWidget(LogWidgetMeta):
    def __init__(self, min_log_level='a', id=""):
        super(PushbulletLogWidget, self).__init__(min_log_level)
        self.tag = "PushbulletLogWidget"
        self.tag = f"{self.tag}{id}"

    def append(self, text, tag, log_level, flush=True, color=None, **kwargs):  
        text = super().format_txt(text, tag, log_level, **kwargs)
        color = LogWidgetMeta.log_levels[log_level].color.code
        self.text_lines.append(text)
        if flush:
            self.flush_lines()
        return None
            
    # @overload
    def flush_lines(self):        
        while len(self.text_lines) > 0:
            self.pb.push_note("Logger Test", f"{timestampStr:<{timestamp_length}}{log_text}")
            line = self.text_lines.pop()
            print(line)   
        return None


    def init_pushbullet(self, pb_access_token):
        try:
            self.pb = PushBullet(pb_access_token)
            self.pb_enabled = False
        except Exception as e:
            self.e("LOGGER", f"Error in initializing PushBullet, notifications DISABLED: {e}")
from PySide6.QtCore import *
from PySide6.QtGui import *
import re
import math

class VLine(QFrame):
    # a simple VLine, like the one you get from designer
    def __init__(self):
        super(VLine, self).__init__()
        self.setFrameShape(QFrame.Shape.VLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)

class QtWaitingSpinner(QWidget):
    def __init__(self, parent, centerOnParent=True, disableParentWhenSpinning=False, modality=Qt.NonModal, id=""):
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
            painter.translate(self._innerRadius + self._lineLength,
                            self._innerRadius + self._lineLength)
            rotateAngle = float(360 * i) / float(self._numberOfLines)
            painter.rotate(rotateAngle)
            painter.translate(self._innerRadius, 0)
            distance = self.lineCountDistanceFromPrimary(
                i, self._currentCounter, self._numberOfLines)
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
        self._timer.setInterval(
            1000 / (self._numberOfLines * self._revolutionsPerSecond))

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
        distanceThreshold = int(
            math.ceil((totalNrOfLines - 1) * trailFadePerc / 100.0))
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

        
class BackgroundTasksInfoWidget(QWidget):
    def __init__(self, app, *args, **kwargs):
        super(BackgroundTasksInfoWidget, self).__init__(*args, **kwargs)
        self.app = app
        self.logger = self.app.logger
        self.background_tasks_list = []
        self.background_info = QLabel("No background stuff!")
        self.background_count_label = QLabel("")
        self.background_completed = 0
        self.background_count_total = 0
        self.spinner = QtWaitingSpinner(self, centerOnParent=False)
        self.spinner.hideSpinner()
        self.spinner.updateSize(QSize(30, 30))

        self.hbox = QHBoxLayout()

        self.hbox.addWidget(VLine())
        self.hbox.addWidget(self.background_info)
        self.hbox.addWidget(self.spinner)
        self.hbox.addWidget(self.background_count_label)
        self.hbox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.hbox)

    # Incremental task numbering
    def get_new_task_number(self, tag):
        while tag in self.background_tasks_list:
            string_matches = re.match(r"(.*)([0-9]+)", tag)
            if string_matches is not None:
                # print("string_matches: " +str(string_matches.groups()))
                tag = string_matches.group(
                    1)+str(int(string_matches.group(2))+1)
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
        task.logger_signals.started.connect(self.updateBackgroundTaskInfo)
        task.logger_signals.updated.connect(self.updateBackgroundTaskInfo)
        task.logger_signals.completed.connect(self.completeBackgroundTask)
        self.logger.i("THREADS", "Added new background task " + str(info) + " " + str(self.background_completed) +
                "/" + str(self.background_count_total) + " Tasks: " + str(self.background_tasks_list))
        return task

    def updateBackgroundTaskCount(self):
        self.background_count_label.setText("Completed: " + str(self.background_completed) + "/"+str(self.background_count_total))

    def updateBackgroundTaskInfo(self, tag="", info=""):
        self.background_info.setText(str(info))
        self.logger.d(tag, str(info))

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
        self.logger.d("THREADS", "Completed background task " + str(info) + " " + str(self.background_completed) +
                "/" + str(self.background_count_total) + " Tasks: " + str(self.background_tasks_list))


from typing import overload
from .ui_widget import VisualLogWidget

class CvLogWidget(VisualLogWidget):
    def __init__(self, min_log_level='a', cv=None, id=""):
        super(CvLogWidget, self).__init__(drawer=cv, draw_type=VisualLogWidget.Type.OPENCV)
        self.cv2 = cv
        self.tag = "CVLogWidget"
        self.tag = f"{self.tag}{id}"
            
    # @overload
    def append(self, text, tag, log_level, flush=False, color=None, pos=None, font=None, font_size=1, line_height=None, **kwargs):
        return super().append(text, tag, log_level, flush, color, pos, font, font_size, line_height, **kwargs)
    
    # @overload
    def flush_lines(self, draw=True, canvas=None, debug=False):
        super().flush_lines(draw, canvas, debug)
        while len(self.text_lines) > 0:
            line = self.text_lines.pop()
            if draw:
                try:
                    self.draw_text_line(line, canvas)
                except Exception as e:
                    print(f"[{self.tag}] Error printing line '{line.text}': {e}")
        if debug:
            print(f"[{self.tag}] Remaining {len(self.text_lines)} lines")
        
    def draw_text_line(self, line, canvas=None):
        canvas = self.canvas if canvas is None else canvas
        self.cv2.putText(canvas, line.text, (int(line.pos.x), int(line.pos.y)), self.cv2.FONT_HERSHEY_SIMPLEX, line.font_size, line.color, line.thickness, self.cv2.LINE_AA)
    
    def draw_line(self, start, end, color, thickness):
        self.cv2.line(self.canvas, (int(start.x), int(start.y)), (int(end.x), int(end.y)), color, thickness)
        
    def draw_circle(self, center, color, radius, thickness):
        self.cv2.circle(self.canvas, (int(center.x), int(center.y)), radius, color, thickness)
        

class ConsoleLogWidget(LogWidgetMeta):
    def __init__(self, min_log_level='a', id="", auto_flush=True):
        super(ConsoleLogWidget, self).__init__(min_log_level, auto_flush)
        self.tag = "ConsoleLogWidget"
        self.tag = f"{self.tag}{id}"
        
    # @overload
    def append(self, text, tag, log_level='a', no_date=False, flush=True, color=None, **kwargs):  
        color = LogWidgetMeta.log_levels[log_level].color.code
        end_char = kwargs.get('end', "\n")
        prev_end = "\n" 
        if len(self.text_lines) > 0:
            prev_end = self.text_lines[-1][-1]
        if len(self.text_lines) <= 0 or prev_end == "\n":
          text = super().format_txt(text, tag, no_date, log_level, **kwargs)
        self.text_lines.append(f"{color}{text}{self.color_reset.code}{end_char}")
        if end_char == "\n":
            self.flush_lines()
        return None
            
    # @overload
    def flush_lines(self):
        while len(self.text_lines) > 0:
            line = self.text_lines.pop(0)
            print(line, end="")
        return None

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


from typing import overload

class VisualLogWidget(LogWidgetMeta):
    class Type:
        NONE = "None"
        OPENCV = 'cv'
        PYGAME = 'pygame'
        
    class Point:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            
    class DebugTextLine:
        def __init__(self, text, color, pos, font=None, font_size=0.4, line_height=-1, thickness=1):
            self.text = text
            self.color = color
            self.pos = pos
            self.font = font
            self.font_size = font_size
            self.thickness = thickness
            self.line_height = line_height
            if line_height < 0:
                self.line_height = self.font_size*0.8

    def __init__(self, min_log_level='a', drawer=None, draw_type=None, canvas=None, id=""):
        super(VisualLogWidget, self).__init__(min_log_level)
        self.tag = "VisualLogWidget"
        self.tag = f"{self.tag}{id}"
        self.drawer = drawer
        self.draw_type = self.Type.NONE if draw_type is None else draw_type
        self.canvas = canvas
        self.font = None
        self.font_size = 20
        self.line_height = 20

    def set_canvas(self, canvas):
        self.canvas = canvas

    def draw_text_line(self, start, end, color, thickness):
        pass

    def draw_line(self, start, end, color, thickness):
        pass

    def draw_circle(self, center, color, radius, thickness):
        pass

    def append(self, text, tag, log_level, flush=False, no_date=False, color=None, pos=None, font=None, font_size=1, line_height=None, thickness=1, **kwargs):
        if pos is None:
            pos = VisualLogWidget.Point(10, 10)
        elif len(pos) > 1:
            pos = VisualLogWidget.Point(pos[0], pos[1])
        text = super().format_txt(text, tag, log_level, **kwargs)
        font = self.font if font is None else font
        font_size == self.font_size if font_size is None else font_size
        line_height = self.line_height if line_height is None else line_height
        color = LogWidgetMeta.log_levels[log_level].color.rgb if color is None else color
        self.text_lines.append(self.DebugTextLine(text, color, self.Point(pos.x, pos.y), font, font_size, thickness))
        pos.y += line_height
        return pos

       # @overload
    def flush_lines(self, draw=True, canvas=None, debug=False):
        if debug:
            print(f"[{self.tag}] Flushing {len(self.text_lines)} lines")
        return 


from typing import overload
from datetime import datetime
import os

class FileLogWidget(LogWidgetMeta):
    def __init__(self, min_log_level='a', filename=None, dir_path="logs", id=""):
        super(FileLogWidget, self).__init__(min_log_level)
        self.tag = "FileLogWidget"
        self.tag = f"{self.tag}{id}"
        filename = f"log_{datetime.now().strftime('%d_%b_%Y-%H_%M_%S')}.txt" if filename is None else filename   
        self.log_file_path = f"{dir_path}/{filename}.txt" 
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        self.file = open(self.log_file_path, "w+")
            
    # @overload
    def flush_lines(self):
        while len(self.text_lines) > 0:
            line = self.text_lines.pop()
            self.file.write(f"{line}\n")  
        return None   

    # @overload
    def destroy(self):
        self.file.close()

