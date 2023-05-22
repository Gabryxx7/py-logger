from pylogger_new import Log
from src.Widgets.console_widget import ConsoleLogWidget
from src.Widgets.file_widget import FileLogWidget
from src.Widgets.pygame_widget import PyGameLogWidget
import time

log = Log.Instance()

def main():
  global log
  log.add_widget(FileLogWidget())
  log.add_widget(ConsoleLogWidget())
  count = 0
  while True:
    pos = log.i("test", f"Test {count}", flush=False)
    pos = log.s("test", f"Test {count}", pos=pos, flush=False)
    pos = log.w("test", f"Test {count}", pos=pos, flush=False)
    pos = log.e("test", f"Test {count}", pos=pos, flush=False)
    pos = log.d("test", f"Test {count}", pos=pos, flush=False)
    count += 1
    log.flush()
    time.sleep(1)
    
if __name__ == '__main__':
  print(__package__)
  main()
