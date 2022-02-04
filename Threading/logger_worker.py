from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
import time
import random

class EventLoggerSignals(QObject):
    msg_sent = Signal(str, int, int)
    finished = Signal(str)

class EventLoggerWorker(QRunnable):
    def __init__(self, msgs_list=None, min=0, max=100, tag="EventLogger"):
        super(EventLoggerWorker, self).__init__()
        self.msgs_list = msgs_list
        self.min = 0
        self.max = max
        if not isinstance(msgs_list, list):
            self.msgs_list = [msgs_list]
        self.signals = EventLoggerSignals()
        self.tag = tag

    @Slot()
    def run(self): # A slot takes no params
        for i in range(len(self.msgs_list)):
            log_msg = self.msgs_list[i]
            waiting_time = random.randint(self.min, self.max)
            self.signals.msg_sent.emit(f"{log_msg} - Waiting for {waiting_time} seconds", i, len(self.msgs_list))
            time.sleep(random.randint(self.min, self.max))
        self.signals.finished.emit(self.tag)