import glob
import os

def get_def(*args, skip_lines=0):
   full_def = ""
   for def_file in args:
      with open(def_file, "r") as fp:
         import_def = fp.read()
         import_def = import_def.split('\n', skip_lines)[-1]
         full_def += import_def + "\n"
   return full_def


excludes = ["__init__.py", "widget_meta.py"]
main_files = ["../pylogger_new.py", "./Widgets/widget_meta.py"]
default_def = get_def(*main_files)
all_defs = default_def

widgets_files = glob.glob('./Widgets/*.py', recursive=True)
export_folder = "./single_file_imports/"

for w_file in widgets_files:
   filename = os.path.basename(w_file)
   if os.path.basename(w_file) not in excludes:
      print(f"Making import for {w_file}", end="")
      merged = get_def(w_file, skip_lines=1)
      all_defs += merged
      full_path = f"{export_folder}merged_{filename}"
      with open(full_path, "w") as fp:
         fp.write(default_def)
         fp.write(merged)
         fp.flush()
         print(f"\tWritten to file {full_path}")

w_file = "ALL.py"
full_path = f"{export_folder}merged_{w_file}"
print(f"Making import for {w_file}", end="")
with open(full_path, "w") as fp:
   fp.write(all_defs)
   fp.flush()
   print(f"\tWritten to file {full_path}")