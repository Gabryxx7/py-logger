from .widget_meta import LogWidgetMeta

class ConsoleLogWidget(LogWidgetMeta):
    def __init__(self, min_log_level='a', id=""):
        super(ConsoleLogWidget, self).__init__(min_log_level)
        self.tag = "ConsoleLogWidget"
        self.tag = f"{self.tag}{id}"
        
    # @overload
    def append(self, tag, text, log_level='a', no_date=False, flush=True, color=None, **kwargs):  
        color = LogWidgetMeta.log_levels[log_level].color.code
        end_char = kwargs.get('end', "\n")
        if end_char == "\n":
          text = super().format_txt(tag, text, no_date, log_level, **kwargs)
        self.text_lines.append(f" {color}{text}{self.color_reset.code}{end_char} ")
        if flush:
            self.flush_lines()
        return None
            
    # @overload
    def flush_lines(self):
        while len(self.text_lines) > 0:
            line = self.text_lines.pop(0)
            print(line, end="")
        return None
