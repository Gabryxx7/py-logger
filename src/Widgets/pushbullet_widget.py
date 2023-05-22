from .widget_meta import LogWidgetMeta
from typing import overload

class PushbulletLogWidget(LogWidgetMeta):
    def __init__(self, min_log_level='a'):
        super(PushbulletLogWidget, self).__init__(min_log_level)
        self.tag = "PushbulletLogWidget"

    def append(self, tag, text, log_level, flush=True, color=None, **kwargs):  
        text = super().format_txt(tag, text, log_level, **kwargs)
        color = LogWidgetMeta.log_levels[log_level].color.code
        self.text_lines.append(text)
        if flush:
            self.flush_lines()
        return None
            
       # @overload
    def flush_lines(self):        
        while len(self.text_lines) > 0:
            self.pb.push_note("Logger Test", f"{timestampStr:<{timestamp_length}}{log_text}")
            line = self.text_lines.pop()
            print(line)   
        return None


    def init_pushbullet(self, pb_access_token):
        try:
            self.pb = PushBullet(pb_access_token)
            self.pb_enabled = False
        except Exception as e:
            self.e("LOGGER", f"Error in initializing PushBullet, notifications DISABLED: {e}")