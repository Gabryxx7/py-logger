from pylogger import *
from logger_app import *
import argparse
import sys
import faulthandler
import time
import oyaml as yaml
import traceback

log = None

"""
THIS IS SUPER IMPORTANT IN PYQT5 APPS
Without this, python won't print any unhandled exception since they happen within the app.exec_()
"""
def trap_exc_during_debug(*args):
    global log
    exc_type, exc_value, exc_traceback = sys.exc_info()
    log.e("MAIN", f"General Exception: {args}\n{str(traceback.format_exc())}" )
    traceback.print_tb(exc_traceback, limit=None, file=sys.stdout)

def process_cl_args():
    global log
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--swallow', action='store')  # optional flag
    parser.add_argument('holy_hand_grenade', action='store')  # positional argument

    parsed_args, unparsed_args = parser.parse_known_args()
    return parsed_args, unparsed_args

def main():
    global log
    config = {}
    with open("config.no_commit.yaml") as f:
        config = yaml.safe_load(f)
    pb_token = config.get("pb_access_token", "")
    log = Log.Instance()
    # install exception hook: without this, uncaught exception would cause application to exit
    sys.excepthook = trap_exc_during_debug
    # QApplication expects the first argument to be the program name.
    qt_args = sys.argv[:1]

    with open("./fault_handler.log", "w") as fobj:
        faulthandler.enable(fobj)
        app = LogApp(log)
        app.exec_()

if __name__ == '__main__':
    main()