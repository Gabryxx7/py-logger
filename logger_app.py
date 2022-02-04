from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
from GUI.custom_spinner_widget import QtCustomWaitingSpinner
from GUI.waiting_spinner_widget import QtWaitingSpinner
from GUI.main_window import MainWindow
from Threading.logger_worker import EventLoggerWorker, EventLoggerSignals
import time

class LogApp(QApplication):
    def __init__(self, log, *args, **kwargs):
        super(LogApp, self).__init__(*args, **kwargs)
        self.log = log
        self.log.create_log_widget()

        self.thread_pool = QThreadPool()   # 1b - create a ThreadPool and then create the Workers when you need!
        self.thread_pool.setMaxThreadCount(4)

        self.background_tasks_list = []
        self.background_info = QLabel("No background stuff!")
        self.background_count_label = QLabel("")
        self.background_completed = 0
        self.background_count_total = 0
        self.spinner = QtCustomWaitingSpinner(self, centerOnParent=False)
        self.spinner.hideSpinner()
        self.spinner.updateSize(QSize(30,30))

        self.profile_info = None
        self.startMainWindow()

    def startMainWindow(self):
        self.window = MainWindow(self, background_info=self.background_info, background_count_label=self.background_count_label, spinner=self.spinner)
        self.window.show()
        msgs_list = self.generate_random_msgs_list()
        self.start_events_generator(tag="EventGenerator", msgs_list=msgs_list, min_t=3, max_t=100)
    
    def generate_random_msgs_list(self, num_msgs=100, msg_template="Test <num>"):
        return [msg_template.replace("<num>", str(i)) for i in range(0, num_msgs)]

    def start_events_generator(self, tag=None, msgs_list=None, min_t=1, max_t=100):
        obj = EventLoggerWorker(msgs_list, min_t, max_t)
        if tag is not None:
            obj.tag = tag 
        obj.signals.msg_sent.connect(self.msg_sent_callback)  # 2 - Connect Worker`s Signals to Form method slots to post data.
        obj.signals.finished.connect(self.thread_finished_callback)  # 2 - Connect Worker`s Signals to Form method slots to post data.
        self.addBackgroundTask(obj, "Starting new Event logger background task")

    def msg_sent_callback(self, msg, worker_n, total_workers):
        self.updateBackgroundTaskInfo(f"{msg}\tWorker {worker_n}/{total_workers}")

    def thread_finished_callback(self, tag=None):
        self.completeBackgroundTask("Completed! ", tag=tag)

    def addBackgroundTask(self, task, info=""):
        if task.tag is not None:
            while task.tag in self.background_tasks_list:
                string_matches = re.match(r"(.*)([0-9]+)", task.tag)
                if string_matches is not None:
                    # print("string_matches: " +str(string_matches.groups()))
                    task.tag = string_matches.group(1)+str(int(string_matches.group(2))+1)
                else:
                    task.tag += "_1"
            self.background_tasks_list.append(task.tag)
        self.updateBackgroundTaskInfo(info)
        self.background_count_total += 1
        if self.background_count_total <= 1:
            self.spinner.showSpinner()
            self.background_count_label.setVisible(True)
        self.updateBackgroundTaskCount()
        self.log.d("THREADS", "Added new background task " +str(info) +" " +str(self.background_completed) + "/" + str(self.background_count_total) +" Tasks: " +str(self.background_tasks_list), False)
        self.thread_pool.start(task)

    def updateBackgroundTaskCount(self):
        self.background_count_label.setText(str(self.background_completed) +"/"+str(self.background_count_total))
        
    def updateBackgroundTaskInfo(self, text=""):
        self.background_info.setText(str(text))

    def completeBackgroundTask(self, info="", tag=None):
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