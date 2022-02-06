from pylogger import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
import time
import random


class EventLoggerWorker(LoggableTaskWorker):
    def __init__(self, msgs_list=None, min=0, max=100, tag="EventLogger"):
        super(EventLoggerWorker, self).__init__()
        self.msgs_list = msgs_list
        self.min = 0
        self.max = max
        if not isinstance(msgs_list, list):
            self.msgs_list = [msgs_list]
        self.tag = tag

    @Slot()
    def run(self): # A slot takes no params
        self.log_signals.started.emit(self.tag, {self.tag})
        for i in range(len(self.msgs_list)):
            log_msg = self.msgs_list[i]
            waiting_time = random.randint(self.min, self.max)
            self.log_signals.updated.emit(self.tag, {f"Msg {log_msg}/{len(self.msgs_list)} - Waiting for {waiting_time} seconds", i, len(self.msgs_list)})
            time.sleep(random.randint(self.min, self.max))
        self.log_signals.completed.emit(self.tag, {self.tag})

class LogApp(QApplication):
    def __init__(self, log, *args, **kwargs):
        super(LogApp, self).__init__(*args, **kwargs)
        self.log = log
        self.log.create_log_widget()
        self.log.logWidget.set_font_size(12)

        self.thread_pool = QThreadPool()   # 1b - create a ThreadPool and then create the Workers when you need!
        self.thread_pool.setMaxThreadCount(4)

        self.profile_info = None
        self.initMainWindow()

    def initMainWindow(self):
        self.window = QMainWindow()
        self.tasks_logger = BackgroundTasksLogger(self)
        self.statusBar = QStatusBar(self.window)
        self.statusBar.addPermanentWidget(self.tasks_logger)

        self.window.setStatusBar(self.statusBar)

        self.window.setWindowTitle("LogApp")
        self.window.setMinimumSize(600, 600)
        
        self.main_widget = QWidget()
        self.main_hlayout = QHBoxLayout()
        self.main_hlayout.addWidget(self.log.logWidget, 30)
        self.main_hlayout.setContentsMargins(0,0,0,0)
        self.main_widget.setLayout(self.main_hlayout)
        
        self.window.setCentralWidget(self.main_widget)
        self.window.centralWidget().layout().setContentsMargins(0,0,0,0)
        self.window.centralWidget().setContentsMargins(0,0,0,0)

        self.window.show()
        msgs_list = self.generate_random_msgs_list(num_msgs=5)
        self.start_events_generator(tag="EventGenerator", n_workers=10, msgs_list=msgs_list, min_t=3, max_t=10)
    
    def generate_random_msgs_list(self, num_msgs=10, msg_template="Test <num>"):
        return [msg_template.replace("<num>", str(i)) for i in range(0, num_msgs)]

    def start_events_generator(self, tag=None, n_workers=10, msgs_list=None, min_t=1, max_t=100):
        for i in range(0, n_workers):
            task = self.tasks_logger.addBackgroundTask(EventLoggerWorker(msgs_list, min_t, max_t, tag=tag), "Starting new Event logger background task")
            task.log_signals.updated.connect(self.msg_sent_callback)  # 2 - Connect Worker`s Signals to Form method slots to post data.
            task.log_signals.completed.connect(self.thread_finished_callback)  # 2 - Connect Worker`s Signals to Form method slots to post data.
            self.thread_pool.start(task)

    def msg_sent_callback(self, tag, data):
        # msg = data[0]
        # worker_n = data[1]
        # total_workers = data[1]
        # txt = f"{msg}\tWorker {worker_n}/{total_workers}"
        self.log.d(tag, f"This is the App updated_callback from {tag}")

    def thread_finished_callback(self, tag, data):
        self.log.d(tag, "Completed! ")