from pylogger import *

log = Log.Instance()



class LogApp(QApplication):
    def __init__(self, parsed_args, *args, **kwargs):
        super(LogApp, self).__init__(*args, **kwargs)

        log.create_log_widget()

        self.thread_pool = QThreadPool()   # 1b - create a ThreadPool and then create the Workers when you need!
        self.thread_pool.setMaxThreadCount(4)

        self.profile_info = None
        self.startMainWindow(True)

    def startMainWindow(self, doAsync=False):
        self.window = mw.MainWindow(self)
        self.window.show()
        self.main_vlayout.addWidget(log.logWidget, 30)

class MainWindow(QMainWindow):
    def __init__(self, app):
        super(MainWindow, self).__init__()
        self.app = app
        self.setWindowTitle("LogApp")
        self.setMinimumSize(600, 600)
        self.main_widget = QWidget()
        self.main_hlayout = QHBoxLayout()
        self.main_hlayout.addWidget(log.logWidget, 30)
        self.main_hlayout.setContentsMargins(0,0,0,0)
        self.main_widget.setLayout(self.main_hlayout)
        
        self.setCentralWidget(self.main_widget)
        self.centralWidget().layout().setContentsMargins(0,0,0,0)
        self.centralWidget().setContentsMargins(0,0,0,0)

"""
THIS IS SUPER IMPORTANT IN PYQT5 APPS
Without this, python won't print any unhandled exception since they happen within the app.exec_()
"""
def trap_exc_during_debug(*args):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    log.e("MAIN", "General Exception: " +str(args))
    traceback.print_tb(exc_traceback, limit=None, file=sys.stdout)

def main():
    # install exception hook: without this, uncaught exception would cause application to exit
    sys.excepthook = trap_exc_during_debug
    parsed_args, unparsed_args = process_cl_args()
    # QApplication expects the first argument to be the program name.
    qt_args = sys.argv[:1] + unparsed_args

    with open("./fault_handler.log", "w") as fobj:
        faulthandler.enable(fobj)
        app = TinderApp(parsed_args, qt_args)
        app.exec_()

if __name__ == '__main__':
    main()