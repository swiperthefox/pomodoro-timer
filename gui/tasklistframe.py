import tkinter as tk
from tkinter import ttk
from datetime import datetime

from asset import get_asset_pool
from .utils import trace, subscribe, grid_layout
from .newtaskdialog import NewTaskDialog
from .tomatobox import TomatoBox
from .todowindow import TodoListWindow
from .sessionhistorywindow import SessionHistoryWindow
from model import tasks
from model.scheduledtask import ScheduledTask

class TaskListFrame(ttk.Frame):
    def __init__(self, master, task_list, todo_list, start_pomodoro, running_session_flag, **grid_opt):
        super().__init__(master)
        self.grid_opt = grid_opt
        self.asset_pool = get_asset_pool(self)
        self.columnconfigure(2, weight=4)
        self.columnconfigure(3, weight=1)
        
        # bookkeeping setup
        self.task_list = task_list
        self.todo_task = todo_list
        self.start_pomodoro_command = start_pomodoro
        self.running_session_flag = running_session_flag
        subscribe(task_list, self, 'change', self.display_task_list)
        subscribe(task_list, self, 'add', self.display_new_task)
    
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
        # [+]  Done  Tasks          Pomodoro
        # ---  ----- -------------  ---------
        
        # newTaskBtn handler
        def add_task():
            new_task_dialog = NewTaskDialog(self.winfo_toplevel(), "Add Task", self.task_list)
            new_task = new_task_dialog.result
            if new_task is not None:
                if isinstance(new_task, ScheduledTask):
                    today = datetime.today()
                    new_task.last_gen = today.toordinal()
                    new_task.save_to_db()
                    new_task = new_task.get_task_for_date(today)
                if isinstance(new_task, tasks.Todo):
                    self.todo_task.add_todo(new_task)
                elif isinstance(new_task, tasks.Task):
                    self.task_list.add(new_task)
                else:
                    pass # new task for today
                    
        rows = []
        
        asset_pool = get_asset_pool(self)        
        # header widgets
        newTaskBtn = ttk.Button(self, image=asset_pool.get_image('new_icon'),
            command=add_task)
        done_label = ttk.Label(self, text="Done")
        title = ttk.Label(self, text = "Task", anchor=tk.CENTER)
        pomodoro_header = ttk.Label(self, text="Sessions")
        
        rows.append([newTaskBtn, done_label, title, pomodoro_header])
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
            
        state_var = tk.BooleanVar()
        done_btn = ttk.Checkbutton(self, variable=state_var,  
            command=lambda: task.set_done(state_var.get()))
        
        title_label = ttk.Label(self, text=' '*indent + task.description, anchor=tk.W)
        
        tomato_list = ([get_image('tomato_red')]*task.progress + 
            [get_image('tomato_green')]*task.remaining_pomodoro())
        def show_session_history(e):
            show_session_history_for_task(self, task)
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
            
        # observer for change of `running_session_flag`
        def update_start_button_state(has_running_session):
            can_start = not has_running_session and task.can_start()
            start_btn.config(state = tk.NORMAL if can_start else tk.DISABLED)
        
        subscribe(task, title_label, 'task-state-change', on_task_update)    
        trace(self.running_session_flag, title_label, ['write'], 
            lambda v,i, m: update_start_button_state(self.running_session_flag.get()))
        
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
        1. This task can't mark as `done`. Whether this task is `done` depends on how many unfinished
        todos left. `Done` button is replaced with a label showing the number of unfinished todos.
        2. Click on the task title will open a todo list.
        """
        ##
        # Create Widget
        # 
        # [start]  5  Misc. todos  RRGGG
        ##
        task: tasks.TodoTask = self.todo_task 
        get_image = get_asset_pool(self).get_image
        
        def show_todo_window(e):
            TodoListWindow.show_todo_window(self, self.todo_task)
        
        def start_todo_task():
            show_todo_window(None)
            self.start_pomodoro_command(task)
            
        start_btn = ttk.Button(self, image=get_image('clock'), command=start_todo_task)
        
        self.todo_count_var = tk.IntVar(value=task.unfinished) # must keep a reference of the var
        todo_count_label = ttk.Label(self, textvariable=self.todo_count_var, anchor=tk.CENTER)
        todo_count_label.bind('<1>', show_todo_window)
        
        title_label = ttk.Label(self, text=task.description)
        title_label.bind('<1>', show_todo_window)
        
        tomato_list = ([get_image('tomato_red')]*task.progress + 
            [get_image('tomato_green')]*task.remaining_pomodoro())
        def show_session_history(e):
            show_session_history_for_task(self, task)
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
        def on_task_update(task=task):
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
            can_start = not has_running_session and task.can_start()
            start_btn.config(state = tk.NORMAL if can_start else tk.DISABLED)
        
        subscribe(task, title_label, 'task-state-change', on_task_update)
        trace(self.running_session_flag, title_label, ['write'], 
            lambda v,i, m: update_start_button_state(self.running_session_flag.get()))
        
        ## finish up
        on_task_update(task)
        return row

def show_session_history_for_task(master, task: tasks.Task):
    if not task._showing_sessions:
        task._showing_sessions = True
        sessions = tasks.Session.load_sessions_for_task(task.id)
        SessionHistoryWindow(master, sessions, task)
  