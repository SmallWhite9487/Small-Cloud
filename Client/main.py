import sys
import os
from modules.gui import SmallCloudGUI
import tkinter as tk

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, relative_path)

modules_path = get_resource_path("modules")
if modules_path not in sys.path:
    sys.path.append(modules_path)

def main():
    root = tk.Tk()
    icon_path = get_resource_path("icon.ico")
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)
        
    app = SmallCloudGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()