import tkinter as tk
from tkinter import ttk

from .simpledialog import Dialog
from .utils import grid_layout

class SessionNoteDialog(Dialog):
    """
    A dialog for editing a short note.
    """
    def __init__(self, master, content, title):
        self.task_content = content
        super().__init__(master, title)
        
    def body(self, master):
        task_content_label = ttk.Label(master, text=self.task_content)
        t_label = ttk.Label(master, text="Short note about the session (ESC to cancel)")
        self.t_entry = tk.Text(master, width=60, height=3)
        grid_layout(master, [[task_content_label], [t_label], [self.t_entry]])
        return self.t_entry
        
    def apply(self):
        self.result = self.t_entry.get('1.0', 'end')
