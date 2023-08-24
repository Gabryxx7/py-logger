from .widget_meta import LogWidgetMeta
from typing import overload
from .ui_widget import VisualLogWidget

class PyGameLogWidget(VisualLogWidget):
    def __init__(self, min_log_level='a', pygame=None, font=None, font_size=16, canvas=None, id=""):
        super(PyGameLogWidget, self).__init__(min_log_level, drawer=pygame, draw_type=VisualLogWidget.Type.PYGAME, canvas=canvas)
        self.tag = "PyGameLogWidget"
        self.tag = f"{self.tag}{id}"
        self.font = pygame.font.SysFont('Arial', 16) if font is None else font
        self.font_size = font_size
        self.line_height = self.font_size*0.8
            
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
        canvas.blit(line.font.render(line.text, True, line.color), (int(line.pos.x), int(line.pos.y)))
    
    def draw_line(self, start, end, color, thickness):
        self.drawer.draw.line(self.canvas, color=color, start_pos=(int(start.x), int(start.y)), end_pos=(int(end.x), int(end.y)), width=thickness)
        
    def draw_circle(self, center, color, radius, thickness):
        self.drawer.draw.circle(self.canvas, color=color, center=(int(center.x), int(center.y)), radius=radius, width=thickness)
