from sys import platform

from tkinter import *


class App(Tk):
    def __init__(self):
        super().__init__()
        w = 350
        h = 200
        self.title('Computer Automation')
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = int((ws / 2) - (w / 2))
        y = int((hs / 2) - (h / 2))
        self.geometry(f'{w}x{h}+{x}+{y}')
        self.resizable(False, False)

        # make app semi-transparent
        if platform.lower() == 'linux':
            self.wait_visibility(self)
            self.wm_attributes('-alpha', 0.85)
