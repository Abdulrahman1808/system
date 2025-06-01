from dotenv import load_dotenv
load_dotenv()

# Disable DPI awareness to avoid block_update_dimensions_event error
import ctypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

import tkinter as tk
from app import HookahShopApp

if __name__ == "__main__":
    root = tk.Tk()
    app = HookahShopApp(root)
    root.mainloop()