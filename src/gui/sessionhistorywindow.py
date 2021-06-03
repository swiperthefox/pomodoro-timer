import tkinter as tk
from tkinter import ttk

from .utils import add_content_frame

class SessionHistoryWindow(tk.Toplevel):
    def __init__(self, master, sessions, task_title, show_flag):
        super().__init__(master)
        self.frame = add_content_frame(self)
        self.title(f'Session History: {task_title}') # type: ignore
        self.render_sessions(sessions)
        self.transient(master)
        self.bind('<Escape>', lambda e: self.destroy())
        def on_close(e):
            show_flag[0] = False
        self.frame.bind('<Destroy>', on_close)
        
    def render_sessions(self, sessions):
        columns = ('start', 'end', 'note')
        tree = ttk.Treeview(self.frame, columns=columns)
        tree.grid(row=0, column=0, sticky='wens')
        self.frame.rowconfigure(0,weight=1)
        self.frame.columnconfigure(0,weight=1)
        tree.column('start', width=200)
        tree.column('end', width=200)
        tree.column('note', stretch=1)
        tree.heading('#0', text="ID")
        tree.column('#0', width=40)
        for col in columns:
            tree.heading(col, text=col.capitalize())
            
        for i, session in enumerate(sessions):
            tree.insert('', tk.END, text=str(i+1), values = session)
