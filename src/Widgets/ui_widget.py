from .widget_meta import LogWidgetMeta
from typing import overload

class VisualLogWidget(LogWidgetMeta):
    class Type:
        NONE = "None"
        OPENCV = 'cv'
        PYGAME = 'pygame'
        
    class Point:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            
    class DebugTextLine:
        def __init__(self, text, color, pos, font=None, font_size=0.4, line_height=-1, thickness=1):
            self.text = text
            self.color = color
            self.pos = pos
            self.font = font
            self.font_size = font_size
            self.thickness = thickness
            self.line_height = line_height
            if line_height < 0:
                self.line_height = self.font_size*0.8

    def __init__(self, min_log_level='a', drawer=None, draw_type=None, canvas=None, id=""):
        super(VisualLogWidget, self).__init__(min_log_level)
        self.tag = "VisualLogWidget"
        self.tag = f"{self.tag}{id}"
        self.drawer = drawer
        self.draw_type = self.Type.NONE if draw_type is None else draw_type
        self.canvas = canvas
        self.font = None
        self.font_size = 20
        self.line_height = 20

    def set_canvas(self, canvas):
        self.canvas = canvas

    def draw_text_line(self, start, end, color, thickness):
        pass

    def draw_line(self, start, end, color, thickness):
        pass

    def draw_circle(self, center, color, radius, thickness):
        pass

    def append(self, tag, text, log_level, flush=False, no_date=False, color=None, pos=None, font=None, font_size=1, line_height=None, thickness=1, **kwargs):
        if pos is None:
            pos = VisualLogWidget.Point(10, 10)
        elif len(pos) > 1:
            pos = VisualLogWidget.Point(pos[0], pos[1])
        text = super().format_txt(tag, text, log_level, **kwargs)
        font = self.font if font is None else font
        font_size == self.font_size if font_size is None else font_size
        line_height = self.line_height if line_height is None else line_height
        color = LogWidgetMeta.log_levels[log_level].color.rgb if color is None else color
        self.text_lines.append(self.DebugTextLine(text, color, self.Point(pos.x, pos.y), font, font_size, thickness))
        pos.y += line_height
        return pos

       # @overload
    def flush_lines(self, draw=True, canvas=None, debug=False):
        if debug:
            print(f"[{self.tag}] Flushing {len(self.text_lines)} lines")
        return 

