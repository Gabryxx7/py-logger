from main import Log
from src.Widgets.console_widget import ConsoleLogWidget
from src.Widgets.file_widget import FileLogWidget
from src.Widgets.pygame_widget import PyGameLogWidget
from src.Utils.fps_counter import FPSCounter

import time
import pygame

log = Log.Instance()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720


def main():
    global log
    fps_counter = FPSCounter()
    pygame.init()
    screen = pygame.display.set_mode((int(SCREEN_WIDTH), int(SCREEN_HEIGHT)))
    pygame.display.set_caption("SWARM")
    # screen = pygame.display.get_surface()
    log.add_widget(PyGameLogWidget(pygame=pygame, font=pygame.font.SysFont('Cascadia', 16), font_size=16, canvas=screen))
    # log.add_widget(FileLogWidget())
    # log.add_widget(ConsoleLogWidget())
    count = 0
    while True:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                return False
        fps_counter.update(new_frames=1)
        pos = log.i("test", f"FPS: {fps_counter.fps:.2f}", flush=False)
        pos = log.s("test", f"FPS: {fps_counter.fps:.2f}", pos=pos, flush=False)
        pos = log.w("test", f"FPS: {fps_counter.fps:.2f}", pos=pos, flush=False)
        pos = log.e("test", f"FPS: {fps_counter.fps:.2f}", pos=pos, flush=False)
        pos = log.d("test", f"FPS: {fps_counter.fps:.2f}", pos=pos, flush=False)
        sceneClock = pygame.time.Clock()
        screen_delay = sceneClock.tick()
        screen.fill((0, 0, 0))
        log.flush()
        pygame.display.flip()
        # time.sleep(0.1)


if __name__ == '__main__':
    main()
