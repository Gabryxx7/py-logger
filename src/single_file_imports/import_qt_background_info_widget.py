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
      
  def add_widget(self, widget):
    for log_w in self.widgets:
      if log_w.tag == widget.tag:
        print(f"Log Widget {widget.tag} already added!")
        return
    print(f"Adding Log Widget {widget.tag}")
    self.widgets.append(widget)
      
  def w(self, tag, text, **kwargs):
    return self.append(tag, text, 'w', **kwargs)

  def d(self, tag, text, **kwargs):
    return self.append(tag, text, 'd', **kwargs)

  def e(self, tag, text, **kwargs):
    return self.append(tag, text, 'e', **kwargs)

  def s(self, tag, text, **kwargs):
    return self.append(tag, text, 's', **kwargs)

  def i(self, tag, text, **kwargs):
    return self.append(tag, text, 'i', **kwargs)

  def append(self, tag, text, log_level='a', **kwargs):
    pos = 0
    for widget in self.widgets:
      res = widget.append(tag, text, log_level, **kwargs)    
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
        
    def __init__(self, min_log_level='a'):
        self.tag = "LogWidgetMeta"
        self.min_log_level = 'a'
        self.log_level = self.min_log_level
        self.color_reset = LogLevel.LogColor('reset', "\033[0;0m", "</>", (255,255,255))
        self.enabled = True
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
    
    def format_txt(self, tag, text, no_date, log_level='a', **kwargs):    
        if self.log_levels[log_level].level < self.log_levels[self.min_log_level].level:
            return None
        
        timestampStr = ""
        if not no_date:
            dateTimeObj = datetime.now()
            timestampStr = dateTimeObj.strftime("%d-%b-%Y %H:%M:%S") + " - "
        log_text = f"{timestampStr}{log_level.upper()}[{tag}]: {text}"
        return log_text
    
    # To be overridden
    def append(self, tag, text, log_level, no_date=False, flush=True, **kwargs):
        text = self.format_txt(tag, text, no_date, log_level, **kwargs)
        self.text_lines.append(text)
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


