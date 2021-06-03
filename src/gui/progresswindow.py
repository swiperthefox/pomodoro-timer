import tkinter as tk
from tkinter import ttk
import time

from .utils import add_content_frame, grid_layout
class ProgressWindow(tk.Toplevel):
    """A window to show the progress of a session.
    
    A minimal version will only show a text like "15/45", which means 15 minutes 
    passed in a 45 minutes session.
    A normal version will show the task's description and a progress bar.
    """
    def __init__(self, master, info, duration, geometry=None, keep_on_top=False, minimize=False):
        self.duration = duration
        tk.Toplevel.__init__(self, master)
        self.protocol('WM_DELETE_WINDOW', lambda: 1)
        self.progress = self.text = None
        self.progress_text = tk.StringVar(value=f'00/{duration:02d}')
        self.overrideredirect_flag = False
        self.geometry_value = geometry
        
        total_ticks = max(duration, 20)
        self.tick_interval = duration*60000//total_ticks
        
        if geometry:
            self.geometry(geometry)
            
        if keep_on_top:
            self.attributes('-topmost', True)
            
        self.build_body(minimize, info, total_ticks)
        
    def build_body(self, minimize, info, total_ticks):
        frame = add_content_frame(self)
        pbar_text = ttk.Label(frame, textvariable=self.progress_text) # for "15/45"
        
        if not minimize:
            # Layout:

            #  The task's description           <---- task description
            #  15/45 [=====    ]                <---- progress in text and graphic
                       
            frame.config(padding=(10,10,10,10))
            self.text = tk.StringVar(value=info)
            text = ttk.Label(frame, textvariable=self.text, anchor=tk.W)
            self.progress = tk.IntVar(value=0)
            pbar = ttk.Progressbar(frame, mode='determinate', variable=self.progress, maximum=total_ticks)
            grid_layout(frame, [[text], [pbar_text, pbar]], start_row=0)
        else:
            # minimal layout, just
            # 15/45             <---- only a text label
            self.overrideredirect_flag = True # no title bar
            self.overrideredirect(self.overrideredirect_flag)
            pbar_text.grid(row=0, column=0)
            def toggle_minimal(e):
                self.overrideredirect_flag = not self.overrideredirect_flag
                self.withdraw()
                self.overrideredirect(self.overrideredirect_flag)
                self.deiconify()
            pbar_text.bind('<Double-1>', toggle_minimal)            

    def start(self, callback):
        """Start count down, call callback after the count down ends."""
        start_time = time.time()
        def tick():
            elapsed = int((time.time() - start_time)/60)
            if self.progress:
                self.progress.set(self.progress.get()+1)
            self.progress_text.set(f"{elapsed:02d}/{self.duration:02d}")
            if elapsed < self.duration:
                self.after(self.tick_interval, tick)
            else:
                self.master.after(1, callback) # callback will be called, even after self is destroyed.
                self.destroy()
        self.after(5000, tick) # 5 seconds
    
    def update_info(self, info):
        if self.text:
            self.text.set(info)
    
    def update_title(self, new_title):
        self.title(new_title)
