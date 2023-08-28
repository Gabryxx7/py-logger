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
    pos = log.i(f"Test A {count}", "test", flush=False, end="")
    pos = log.s(f"Test B {count}", "test", pos=pos, flush=False, end=" - ")
    pos = log.w(f"Test C {count}", "test", pos=pos, flush=False)
    pos = log.e(f"Test D {count}", "test", pos=pos, flush=False)
    pos = log.d(f"Test E {count}", "test", pos=pos, flush=False)
    pos = log.d(f"", "test", pos=pos, flush=False)
    count += 1
    log.flush()
    time.sleep(1)
    
if __name__ == '__main__':
  print(__package__)
  main()
