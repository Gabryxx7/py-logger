from .widget_meta import LogWidgetMeta

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
