from .widget_meta import LogWidgetMeta
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
