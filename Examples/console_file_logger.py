# Either use the module
from pylogger_new import Log
from src.Widgets.console_widget import ConsoleLogWidget
from src.Widgets.file_widget import FileLogWidget

# Or import the merged single-file import
# from py_logger import Log, FileLogWidget, ConsoleLogWidget, PyGameLogWidget

import time

log = Log.Instance()

def main():
  global log
  log.add_widget(FileLogWidget())
  log.add_widget(ConsoleLogWidget())
  count = 0
  while True:
    pos = log.i("test", f"Test A {count}", flush=False, end="")
    pos = log.s("test", f"Test B {count}", pos=pos, flush=False, end=" - ")
    pos = log.w("test", f"Test C {count}", pos=pos, flush=False)
    pos = log.e("test", f"Test D {count}", pos=pos, flush=False)
    pos = log.d("test", f"Test E {count}", pos=pos, flush=False)
    count += 1
    log.flush()
    time.sleep(1)
    
if __name__ == '__main__':
  print(__package__)
  main()
