import tkinter as tk
from tkinter import ttk
from datetime import datetime

from asset import get_asset_pool
from .utils import trace, subscribe, grid_layout
from .newtaskdialog import new_task
from .tomatobox import TomatoBox
from .todowindow import TodoListWindow
from .sessionhistorywindow import SessionHistoryWindow
from model import models
from model.scheduledtask import ScheduledTask

class TaskListFrame(ttk.Frame):
    def __init__(self, master, task_list, todo_list, start_pomodoro, running_session_flag, **grid_opt):
        super().__init__(master)
        self.grid_opt = grid_opt
        self.asset_pool = get_asset_pool(self)
        self.columnconfigure(2, weight=4)
        self.columnconfigure(3, weight=1)
        
        self.task_list = task_list
        self.todo_task = todo_list
        self.start_pomodoro_command = start_pomodoro
        self.running_session_flag = running_session_flag
        subscribe(task_list, 'change', self.display_task_list, self)
        subscribe(task_list, 'add', self.display_new_task, self)
    
        self.display_task_list(task_list)
                    
    def display_task_list(self, task_list):
        self.clear()
        rows = self.render_header()
        rows.append(self.render_todo_task())
        for task in task_list:
            rows.extend(self.render_task(task))
        grid_layout(self, rows, **self.grid_opt)
    
    def display_new_task(self, task):
        row = self.render_task(task)
        grid_layout(self, [row], **self.grid_opt)
    
    def clear(self):
        for child in self.winfo_children():
            child.destroy()

    def render_header(self):
        
        # Layout: 
        # [+]  Done  Tasks          Sessions
        # ---  ----- -------------  ---------
        
        # newTaskBtn handler
        def add_task():
            task = new_task(self.winfo_toplevel(), self.task_list)
            if isinstance(task, models.Todo):
                self.todo_task.add_todo(task)
            elif isinstance(task, models.Task):
                self.task_list.add(task)
            else:
                pass # new task for today
                    
        rows = []
        
        asset_pool = get_asset_pool(self)        
        # header widgets
        newTaskBtn = ttk.Button(self, image=asset_pool.get_image('new_icon'),
            command=add_task)
        done_label = ttk.Label(self, text="Done")
        title = ttk.Label(self, text = "Task", anchor=tk.CENTER)
        session_header = ttk.Label(self, text="Sessions")
        show_sessions_for_today = make_session_history_displayer(self, None)
        session_header.bind('<Button-1>', show_sessions_for_today)
        rows.append([newTaskBtn, done_label, title, session_header])
        rows.append([ttk.Separator(self, orient=tk.HORIZONTAL) for i in range(4)])
        
        return rows
        
    def render_task(self, task, indent=0):
        get_image = self.asset_pool.get_image
        
        ## Create widgets 
        # Layout:
        #
        #     [start] [done] task_title     RRGGG
        #
        #  where  [xxx] are buttons, R and G are red and green tomato images
        ##
        start_btn = ttk.Button(self, image=get_image('clock'), 
            command=lambda: self.start_pomodoro_command(task))
            
        state_var = tk.BooleanVar(value=task.done)
        done_btn = ttk.Checkbutton(self, variable=state_var,  
            command=lambda: task.set_done(state_var.get()))
        
        title_label = ttk.Label(self, text=' '*indent + task.description, anchor=tk.W)
        
        tomato_list = ([get_image('tomato_red')]*task.progress + 
            [get_image('tomato_green')]*task.remaining_pomodoro())
        show_session_history = make_session_history_displayer(self, task)
        # tk does not propagate events from child widget to its master, so we need to bind the action
        # to both the tomato images and the container.
        tomato_box = TomatoBox(self, tomato_list, show_session_history)
        tomato_box.bind('<Button-1>', show_session_history)
    
        rows = [[start_btn, done_btn, title_label, tomato_box]]

        ##
        # update widget states
        ## 
        
        # observer for task's state changes
        def on_task_update(task=task):
            """update the presentation of the new task state"""
            font_type = 'strikeout' if task.done else 'normal'
            title_label.config(font = self.asset_pool.get_font(font_type))
            update_start_button_state(self.running_session_flag.get())
            tomato_list = ([get_image('tomato_red')]*task.progress + 
                [get_image('tomato_green')]*task.remaining_pomodoro())
            tomato_box.config(tomatoes=tomato_list)
            
        # observer for the changes of `running_session_flag`
        def update_start_button_state(has_running_session):
            can_start = not has_running_session and task.can_start()
            start_btn.config(state = tk.NORMAL if can_start else tk.DISABLED)
        
        subscribe(task, 'task-state-change', on_task_update, title_label)    
        trace(self.running_session_flag, 
            ['write'], 
            lambda v,i, m: update_start_button_state(self.running_session_flag.get()),
            title_label)
        
        ##
        # finish up
        ##
        on_task_update(task)
        for subtask in task.subtasks:
            rows.extend(self.render_task(subtask, indent+4))
        return rows
        
    def render_todo_task(self):
        """Render the special task "Misc. todos".

        Differences between the gui of this task and gui of others:

        1. This task can't mark as `done`. Whether this task is `done` depends
           on how many unfinished todos left. `Done` button is replaced with a
           label showing the number of unfinished todos.

        2. Click on the task title will open a todo list.
        """
        ##
        # Create Widget
        # 
        # [start]  5  Misc. todos  RRGGG
        ##
        todo_task: models.TodoTask = self.todo_task 
        get_image = get_asset_pool(self).get_image
        
        def show_todo_window(e):
            TodoListWindow.show_todo_window(self, todo_task)
        
        def start_todo_task():
            show_todo_window(None)
            self.start_pomodoro_command(todo_task)
            
        start_btn = ttk.Button(self, image=get_image('clock'), command=start_todo_task)
        
        self.todo_count_var = tk.IntVar(value=todo_task.unfinished) # must keep a reference of the var
        todo_count_label = ttk.Label(self, textvariable=self.todo_count_var, anchor=tk.CENTER)
        todo_count_label.bind('<1>', show_todo_window)
        
        title_label = ttk.Label(self, text=todo_task.description)
        title_label.bind('<1>', show_todo_window)
        
        tomato_list = ([get_image('tomato_red')]*todo_task.progress + 
            [get_image('tomato_green')]*todo_task.remaining_pomodoro())
        show_session_history = make_session_history_displayer(self, todo_task)
        # tk does not propagate events from child widget to its master, so we need to bind the action
        # to both the tomato images and the container.
        tomato_box = TomatoBox(self, tomato_list, show_session_history)
        tomato_box.bind('<Button-1>', show_session_history)
        tomato_box.config(relief="raise")
        row = [start_btn, todo_count_label, title_label, tomato_box]

        ##
        # update widget according to states
        ##
        # observer for task's state changes
        def on_task_update(task=todo_task):
            """update the presentation of the new task state
            
            start_btn, todo_count and tomato_box need to be updated.
            """
            update_start_button_state(self.running_session_flag.get())
            self.todo_count_var.set(task.unfinished)
            tomato_list = ([get_image('tomato_red')]*task.progress + 
                [get_image('tomato_green')]*task.remaining_pomodoro())
            tomato_box.config(tomatoes=tomato_list)
            
        # observer for change of `running_session_flag`
        def update_start_button_state(has_running_session):
            can_start = not has_running_session and todo_task.can_start()
            start_btn.config(state = tk.NORMAL if can_start else tk.DISABLED)
        
        subscribe(todo_task, 'task-state-change', on_task_update, title_label)
        trace(self.running_session_flag, 
            ['write'], 
            lambda v,i, m: update_start_button_state(self.running_session_flag.get()),
            title_label)
        
        ## finish up
        on_task_update(todo_task)
        return row

def make_session_history_displayer(master, task: models.Task = None):
    showing = [False]
    if task:
        session_loader = lambda: models.Session.load_sessions_for_task(task.id)
        title = task.description
    else:
        session_loader = models.Session.load_session_history_for_today
        title = "Today"
    def toggle_session_window(e):
        if not showing[0]:
            showing[0] = True
            # sessions = models.Session.load_sessions_for_task(task and task.id)
            SessionHistoryWindow(master, session_loader(), title, showing, show_first_column=task is None)
    return toggle_session_window
  