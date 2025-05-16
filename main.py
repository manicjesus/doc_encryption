import tkinter as tk
import sys 
import os

src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.append(src_path)

from ui import showMainMenu # type: ignore
from settings_utils import applyScreenSettings # type: ignore

if __name__ == "__main__":
    root = tk.Tk()
    applyScreenSettings(root)
    showMainMenu(root)
    root.mainloop()

