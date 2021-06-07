import tkinter as tk
from tkinter import ttk

class PositionSelector(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        prompt = ttk.Label(self, text="Move the process indicator to the desired position, then click to confirm the position.")
        self.label = ttk.Label(self, text="20/45")
        self.attributes('-fullscreen', True)
        self.attributes('-alpha', 0.3)
        self.bind('<Button-1>', self.close)
        prompt.place(x=600, y=600)
        self.label.place(x=700, y=700)
        self.bind("<Motion>", self.update_position)
    def update_position(self, e):
        x, y = max(0, e.x_root-10), max(0, e.y_root-10)
        self.label.place_configure(x=x, y=y)
        self.position = (x, y)
    
    def close(self, e):
        self.destroy()
        
 