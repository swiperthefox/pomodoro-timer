from datetime import datetime
from tkinter import ttk
import tkinter as tk

from model.scheduledtask import ScheduledTask
from .simpledialog import Dialog
from asset import get_asset_pool
from model import models
from .utils import grid_layout
from .tomatobox import TomatoBox
from taskparser import parse_task_description, parse_date_spec, parse_repeat_pattern


def new_task(master, parent_tasks):
    new_task_dialog = NewTaskDialog(master, "Add Task", parent_tasks)
    new_task = new_task_dialog.result
    if isinstance(new_task, ScheduledTask):
        today = datetime.today()
        new_task.last_gen = today.toordinal()
        new_task.save_to_db(['last_gen'])
        new_task = new_task.get_task_for_date(today)
    return new_task
    
        # if isinstance(new_task, models.Todo):
        #     self.todo_task.add_todo(new_task)
        # elif isinstance(new_task, models.Task):
        #     self.task_list.add(new_task)
        # else:
        #     pass # new task for today

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
    # On      : [ date                ]
    # Repeat  : [ repeat pattern      ]
    # (optional error messages)
    # 
    
    def body(self, master):
        get_image = get_asset_pool(self).get_image
        
        t_label = ttk.Label(master, text="Task:", anchor=tk.W)
        self.t_entry = tk.Text(master, width=60, height=2, font=get_asset_pool(self).get_font('normal'))
        
        c_label = ttk.Label(master, text="Tomatoes:", anchor=tk.W)
        self.tomatoes = 0
        
        def on_choose_tomato(i):
            self.tomatoes = i
            tomatoes = [get_image('tomato_red')]*i + [get_image('tomato_dim')]*(5-i)
            tomatobox.config(tomatoes=tomatoes)
        tomatobox = TomatoBox(master, [get_image('tomato_dim')]*5, on_choose_tomato)
        
        self.long_session_var = tk.StringVar(value='-')
        session_type_label = ttk.Label(master, text="Duration", anchor=tk.W)
        long_session_btn = ttk.Radiobutton(master, text="Long",
            variable=self.long_session_var, value='=')
        short_session_btn = ttk.Radiobutton(master, text="Short", 
            variable=self.long_session_var, value='-')
        
        parent_list = ["None", *(task.description for task in self.tasks)]
        parent_label = ttk.Label(master, text="Parent", anchor=tk.W)
        self.parent_widget = ttk.Combobox(master, values = parent_list)
        self.parent_widget.current(0)
        self.parent_widget.state(['readonly'])
        
        self.date_var = tk.StringVar()
        date_label = ttk.Label(master, text="Date", anchor=tk.W)
        date_entry = ttk.Entry(master, textvariable=self.date_var)
        
        self.repeat_var = tk.StringVar()
        repeat_label = ttk.Label(master, text="Repeat", anchor=tk.W)
        repeat_entry = ttk.Entry(master, textvariable=self.repeat_var)
        
        self.error_var = tk.StringVar()
        error_label = ttk.Label(master, textvariable=self.error_var, foreground='red', anchor=tk.W)
        
        rows = [[t_label,              self.t_entry,          self.t_entry],
                [c_label,              tomatobox,                tomatobox],
                [session_type_label,   long_session_btn, short_session_btn],
                [parent_label,         self.parent_widget, self.parent_widget],
                [date_label,           date_entry,          date_entry ],
                [repeat_label,          repeat_entry,       repeat_entry],
                [error_label,          error_label,           error_label]]
        grid_layout(master, rows, 0, padx=3, pady=5)
        return self.t_entry
        
    def apply(self):
        # the options specified in title has priority over setting in the gui field
        selected_parent_index = self.parent_widget.current()
        parent_id = None if selected_parent_index == 0 else self.tasks[selected_parent_index].id
        parent_title = self.task_option.get('parent', None)
        parent_id = self.search_task_title(parent_title)
                
        title = self.task_option['title']            
        tomato = self.task_option.get('tomato', self.tomatoes)
        task_type = self.task_option.get('type', self.long_session_var.get())
        onetime_date_spec = self.task_option.get('once', self.date_var.get())
        repeat_spec = self.task_option.get('repeat', self.repeat_var.get())
        
        # now create the tasks
        if onetime_date_spec or repeat_spec:
            # create a ScheduledTask
            today = datetime.today()
            onetime_date = parse_date_spec(onetime_date_spec, today).toordinal()
            pattern_str = ' '.join(str(i) for i in parse_repeat_pattern(repeat_spec, today))
            
            self.result = ScheduledTask.create(
                title=title.capitalize(),
                tomato = tomato,
                type=task_type,
                once=onetime_date,
                pattern=pattern_str
            )
        elif task_type == '.':
            # create todo task
            self.result = models.Todo.create(title, 0)
        else:
            # create normal task
            self.result = models.Task.create(
                description = title.capitalize(),
                tomato = tomato,
                long_session = task_type == '=',
                parent = parent_id
            )
    
    def validate(self):
        self.task_option = parse_task_description(self.t_entry.get('0.0', tk.END))
        if len(self.task_option.get('title', '')) == 0:
            self.error_var.set("Task description can't be empty .")
            return False
        if self.tomatoes == 0 and self.task_option.get('tomato', 0) == 0 and self.task_option['type'] != '.':
            self.error_var.set("Normal task must specify the number of tomatoes.")
            return False
        self.error_var.set('')
        return True

    def search_task_title(self, title_prefix):
        if title_prefix:
            title_prefix = title_prefix.lower()
            for task in self.tasks:
                if task.description.lower().startswith(title_prefix):
                    return task.id
        return None