from taskparser import parse_date_spec
import tkinter as tk
from tkinter import ttk

from .utils import subscribe, add_content_frame, grid_layout
from model import tasks
from asset import get_asset_pool
from utils import format_date, parse_date

class TodoListWindow(tk.Toplevel):
    todo_window = None
    
    def __init__(self, master, todo_task: tasks.TodoTask):
        super().__init__(master)
        self['bg'] = 'black'
        self.minsize(width=500, height=400)
        self.title('Misc Todo List')
        self.todo_task = todo_task
        self.frame = add_content_frame(self, padding=(20, 20, 20, 20))
        self.render_todos(todo_task)
        subscribe(todo_task, self.frame, 'change', self.render_todos)
        subscribe(todo_task, self.frame, 'add', self.render_todo)
    
        self.frame.columnconfigure(1, weight=1)
        self.new_todo_widgets = None
        self.bind('<Escape>', lambda e: self.destroy())
        
    # Todo List Layout:
    # 
    # Todos              [+]
    # ------------------------
    # [ ]   Pay bill    04-15
    # ...
    #
    
    def render_todos(self, todo_task):
        self.render_header(todo_task)
        for todo in todo_task.todos:
            self.render_todo(todo)
            
    def render_header(self, todo_task):
        ##
        # Create widgets
        ##
        asset_pool = get_asset_pool(self)
        new_todo_button = ttk.Button(self.frame, image=asset_pool.get_image('new_icon'), command=self.show_new_todo_widget)        
        todo_label = ttk.Label(self.frame, text='Todos')
        due_label = ttk.Label(self.frame, text="Due")
        grid_layout(self.frame, [[new_todo_button, todo_label, due_label]], start_row=0, padx=7, pady=3)
        
        ##
        # Update widget state
        ##
        
    def render_todo(self, todo: tasks.Todo):
        ##
        # Create widgets
        ##
        done_state_var = tk.BooleanVar(value=todo.done)
        def toggle_done():
            self.todo_task.set_todo_state(todo.id, done_state_var.get())
        done_button = ttk.Checkbutton(self.frame, command=toggle_done, variable=done_state_var)
        title_label = ttk.Label(self.frame, text=todo.description)
        deadline_label = ttk.Label(self.frame, text=format_date(todo.deadline))
        grid_layout(self.frame, [[done_button, title_label, deadline_label]], start_row='end', padx=7, pady=3)
        
        ##
        #  Update widgets
        ##
        def on_todo_state_change(todo):
            asset_pool = get_asset_pool(self.frame)
            font_type = 'strikeout' if todo.done else 'normal'
            title_label.config(font = asset_pool.get_font(font_type)) 
        subscribe(todo, title_label, 'state-change', on_todo_state_change)
        
    def confirm_new_todo(self, e):
        todo = tasks.Todo.create(self.new_todo_title.get(), parse_date_spec(self.new_todo_deadline.get()))
        self.clear_new_todo_widgets(e)
        self.todo_task.add_todo(todo)
        
    def clear_new_todo_widgets(self, e):
        self.new_todo_title.set('')
        self.new_todo_deadline.set('')
        for child in self.new_todo_widgets:
            child.grid_forget()
        
    def show_new_todo_widget(self):
        if not self.new_todo_widgets:
            done_state_var = tk.BooleanVar(value=False)
            done_button = ttk.Checkbutton(self.frame, variable=done_state_var, state=tk.DISABLED)
            self.new_todo_title = tk.StringVar()
            self.new_todo_deadline = tk.StringVar()
            title_entry = ttk.Entry(self.frame, textvariable=self.new_todo_title)
            deadline_entry = ttk.Entry(self.frame, textvariable=self.new_todo_deadline)
            self.new_todo_widgets = [done_button, title_entry, deadline_entry]
            for entry in [title_entry, deadline_entry]:
                entry.bind('<Return>', self.confirm_new_todo)
                entry.bind('<Escape>', self.clear_new_todo_widgets)
        grid_layout(self.frame, [self.new_todo_widgets], start_row='end', padx=7, pady=3)
        self.new_todo_widgets[1].focus_set()
    
    @classmethod
    def show_todo_window(cls, master, todo_task):
        if cls.todo_window is None or not tk.Toplevel.winfo_exists(cls.todo_window):
            cls.todo_window = cls(master, todo_task)
        cls.todo_window.transient(master.winfo_toplevel())
