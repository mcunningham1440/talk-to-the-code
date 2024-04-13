import tkinter as tk
import os

os.chdir("/Users/michaelcunningham/Desktop/Coding/t2tc")

from config import *
from src.control_module import *


def main():
    root = tk.Tk()
    root.geometry("400x400+300+300")
    root.title("Recorder")
    app = ControlModule(root, config.code_dir)
    root.mainloop()

if __name__ == "__main__":
    main()