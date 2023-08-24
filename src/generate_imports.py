import glob
import os

def get_def(*args, widget_file=""):
   print(f"Making import for {args}")
   full_def = ""
   for def_file in args:
      with open(def_file, "r") as fp:
         full_def += fp.read() + "\n"
   with open(widget_file, "r") as fp:
      widget_def = fp.read()
      widget_def = widget_def.split('\n', 1)[1]
      full_def += widget_def + "\n"
   return full_def


excludes = ["__init__.py", "widget_meta.py"]
widgets_files = glob.glob('./Widgets/*.py', recursive=True)
main_file = "../pylogger_new.py"
widget_main_file = "./Widgets/widget_meta.py"
export_folder = "./single_file_imports/"

for w_file in widgets_files:
   filename = os.path.basename(w_file)
   if os.path.basename(w_file) not in excludes:
      merged = get_def(main_file, widget_main_file, widget_file=w_file)
      with open(f"{export_folder}import_{filename}", "w") as fp:
         fp.write(merged)
         fp.flush()