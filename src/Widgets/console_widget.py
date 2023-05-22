from .widget_meta import LogWidgetMeta
from typing import overload

class ConsoleLogWidget(LogWidgetMeta):
    def __init__(self, min_log_level='a'):
        super(ConsoleLogWidget, self).__init__(min_log_level)
        self.tag = "ConsoleLogWidget"
        
    # @overload
    def append(self, tag, text, log_level='a', no_date=False, flush=True, color=None, **kwargs):  
        text = super().format_txt(tag, text, no_date, log_level, **kwargs)
        color = LogWidgetMeta.log_levels[log_level].color.code
        self.text_lines.append(f"{color}{text}{self.color_reset.code}")
        if flush:
            self.flush_lines()
        return None
            
    # @overload
    def flush_lines(self):
        while len(self.text_lines) > 0:
            line = self.text_lines.pop()
            print(line)   
        return None