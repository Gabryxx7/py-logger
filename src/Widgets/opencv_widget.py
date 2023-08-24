from .widget_meta import LogWidgetMeta
from typing import overload
from .ui_widget import VisualLogWidget

class CvLogWidget(VisualLogWidget):
    def __init__(self, min_log_level='a', cv=None, id=""):
        super(CvLogWidget, self).__init__(drawer=cv, draw_type=VisualLogWidget.Type.OPENCV)
        self.cv2 = cv
        self.tag = "CVLogWidget"
        self.tag = f"{self.tag}{id}"
            
    # @overload
    def append(self, tag, text, log_level, flush=False, color=None, pos=None, font=None, font_size=1, line_height=None, **kwargs):
        return super().append(tag, text, log_level, flush, color, pos, font, font_size, line_height, **kwargs)
    
       # @overload
    def flush_lines(self, draw=True, canvas=None, debug=False):
        super().flush_lines(draw, canvas, debug)
        while len(self.text_lines) > 0:
            line = self.text_lines.pop()
            if draw:
                try:
                    self.draw_text_line(line, canvas)
                except Exception as e:
                    print(f"[{self.tag}] Error printing line '{line.text}': {e}")
        if debug:
            print(f"[{self.tag}] Remaining {len(self.text_lines)} lines")
        
    def draw_text_line(self, line, canvas=None):
        canvas = self.canvas if canvas is None else canvas
        self.cv2.putText(canvas, line.text, (int(line.pos.x), int(line.pos.y)), self.cv2.FONT_HERSHEY_SIMPLEX, line.font_size, line.color, line.thickness, self.cv2.LINE_AA)
    
    def draw_line(self, start, end, color, thickness):
        self.cv2.line(self.canvas, (int(start.x), int(start.y)), (int(end.x), int(end.y)), color, thickness)
        
    def draw_circle(self, center, color, radius, thickness):
        self.cv2.circle(self.canvas, (int(center.x), int(center.y)), radius, color, thickness)
        