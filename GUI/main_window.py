from PySide2.QtGui import *
from PySide2.QtWidgets import *
from GUI.vline_widget import VLine

class MainWindow(QMainWindow):
    def __init__(self, app, background_info, background_count_label, spinner):
        super(MainWindow, self).__init__()
        self.app = app

        self.log = self.app.log

        self.background_info = background_info
        self.background_count_label =background_count_label
        self.spinner = spinner

        self.statusBar = QStatusBar(self)
        self.statusBar.addPermanentWidget(VLine())
        self.statusBar.addPermanentWidget(self.background_info)
        self.statusBar.addPermanentWidget(self.spinner)
        self.statusBar.addPermanentWidget(self.background_count_label)
        self.setStatusBar(self.statusBar)

        self.setWindowTitle("LogApp")
        self.setMinimumSize(600, 600)
        
        self.main_widget = QWidget()
        self.main_hlayout = QHBoxLayout()
        self.main_hlayout.addWidget(self.log.logWidget, 30)
        self.main_hlayout.setContentsMargins(0,0,0,0)
        self.main_widget.setLayout(self.main_hlayout)
        
        self.setCentralWidget(self.main_widget)
        self.centralWidget().layout().setContentsMargins(0,0,0,0)
        self.centralWidget().setContentsMargins(0,0,0,0)
