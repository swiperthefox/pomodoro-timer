from .simpledialog import Dialog
from asset import get_asset_pool
from tkinter import ttk
import tkinter as tk
from model import tasks
from .utils import grid_layout
from .tomatobox import TomatoBox

class NewTaskDialog(Dialog):
    """A dialog for creating a new task."""
    def __init__(self, master, title, tasks):
        self.tasks = tasks
        Dialog.__init__(self, master, title)
        
    # dialog body layout
    #
    # Task    : [                     ]
    # Tomatoes: RRGGG
    # Duration: [] Long [] Short
    # Parent  : [ choose a parent    v]
    # (optional error messages)
    # 
    
    def body(self, master):
        get_image = get_asset_pool(self).get_image
        
        t_label = ttk.Label(master, text="Task:", anchor=tk.W)
        self.t_entry = ttk.Entry(master)
        
        c_label = ttk.Label(master, text="Tomatoes:", anchor=tk.W)
        self.tomatoes = 0
        
        def on_choose_tomato(i):
            self.tomatoes = i
            tomatoes = [get_image('tomato_red')]*i + [get_image('tomato_dim')]*(5-i)
            tomatobox.config(tomatoes=tomatoes)
        tomatobox = TomatoBox(master, [get_image('tomato_dim')]*5, on_choose_tomato)
        
        self.long_session_var = tk.IntVar()
        session_type_label = ttk.Label(master, text="Duration", anchor=tk.W)
        long_session_btn = ttk.Radiobutton(master, text="Long",
            variable=self.long_session_var, value=1)
        short_session_btn = ttk.Radiobutton(master, text="Short", 
            variable=self.long_session_var, value=0)
        
        parent_list = ["None ", *(task.description for task in self.tasks)]
        parent_label = ttk.Label(master, text="Parent", anchor=tk.W)
        parent_title_var = tk.StringVar()
        self.parent_widget = ttk.Combobox(master, values = parent_list)
        self.parent_widget.state(['readonly'])
        
        self.error_var = tk.StringVar()
        error_label = ttk.Label(master, textvariable=self.error_var, foreground='red', anchor=tk.W)
        
        rows = [[t_label,              self.t_entry,          self.t_entry],
                [c_label,              tomatobox,                tomatobox],
                [session_type_label,   long_session_btn, short_session_btn],
                [parent_label,         self.parent_widget, self.parent_widget],
                [error_label,          error_label,           error_label]]
        grid_layout(master, rows, 0, padx=3, pady=5)
        return self.t_entry
        
    def apply(self):
        selected_parent_index = self.parent_widget.current()
        parent_id = None if selected_parent_index == 0 else self.tasks[selected_parent_index].id
            
        self.result = tasks.Task.create(
            description = self.t_entry.get().strip().capitalize(),
            tomato = self.tomatoes,
            long_session = self.long_session_var.get()==1,
            parent = parent_id
        )
    
    def validate(self):
        if len(self.t_entry.get().strip()) == 0:
            self.error_var.set("Task description can't be empty .")
            return False
        if self.tomatoes == 0:
            self.error_var.set("Must choose some tomatoes.")
            return False
        self.error_var.set('')
        return True
