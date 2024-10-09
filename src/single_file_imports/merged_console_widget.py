
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

