from subprocess import run
from tkinter.constants import E
from .simpledialog import Dialog
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import font
from tkinter import filedialog
import time
import datetime

from model import tasks
from asset import get_asset_pool, AssetPool
from utils import format_date, parse_date
from gui.utils import *
from .newtaskdialog import NewTaskDialog
from .tomatobox import TomatoBox
from .todowindow import TodoListWindow

##
# GUI Components and Dialogs
##
    
def render_app_window(app, title="", geom=""):
    """Create the root window, configure some stylings and assets."""    
    root = app.window
    root.title(title)
    if geom:
        root.geometry(geom)
    root.rowconfigure(0,weight=1)
    root.columnconfigure(0,weight=1)
    content = add_content_frame(root)
    # add assets
    asset_pool = AssetPool(root)
    
    #    font
    normal = font.nametofont('TkDefaultFont')
    strikeout = normal.copy()
    strikeout['overstrike'] = 1
    asset_pool.add_font('normal', normal)
    asset_pool.add_font('strikeout', strikeout)
    asset_pool.add_font('text', font.nametofont('TkTextFont'))
    asset_pool.set_font_property('size', app.config.get_font_size())
    
    #    images
    asset_pool.add_img('tomato_red', AssetPool.COLOR, 'image/tomato_red.png')
    asset_pool.add_img('tomato_bw', AssetPool.COLOR, 'image/tomato_bw.png')
    asset_pool.add_img('tomato_dim', AssetPool.COLOR, 'image/tomato_dim.png')
    asset_pool.add_img('new_icon', AssetPool.COLOR, 'image/plus.png')
    asset_pool.add_img('tomato_green', AssetPool.COLOR, 'image/tomato_green.png')
    asset_pool.add_img('clock', AssetPool.COLOR, 'image/clock.png')
    asset_pool.add_img('setting', AssetPool.COLOR, 'image/setting.png')
    asset_pool.add_img('doc', AssetPool.COLOR, 'image/doc.png')
    
    # attach asset_pool to root, so all other widgets can access it
    root.asset_pool = asset_pool
    
    # set appearance
    style = ttk.Style()
    style.configure('Treeview', rowheight=30)
    style.configure('TCheckbutton', relief=tk.FLAT, indicatormargin=20)
    style.configure('TButton', relief=tk.FLAT)
    style.configure('Normal.TButton', relief=tk.RAISED)
    style.configure('.', background="#eeeeeeeee")
    root.iconphoto(True, asset_pool.get_image('tomato_red'))
    
    # GUI components. Layout:
    
    #        2021-04-01        [#]
    #  -----------------------------
    #  |     task list ...         |
    #  |                           |
    
    today_var = tk.StringVar()
    def set_date():
        """Update the date every 1 hour."""
        today = datetime.datetime.today()
        today_var.set(today.strftime("%Y-%m-%d"))
        root.after(3600000, set_date)
    set_date()
    # title bar that show date
    titlebar = ttk.Label(content, textvariable=today_var, anchor=tk.CENTER,
        font=('Monospace', 20), padding=15)
    
    #     config button
    ttk.Button(titlebar, image=asset_pool.get_image('setting'),  # type: ignore (it's OK for image to be None)
        command=lambda: open_config_window(root, app.config)).pack(side=tk.RIGHT)
        
    # task list
    task_frame = TaskListFrame(content,
        app.task_list, app.todo_task, app.start_session, app.session_running,
        padx=7, pady=3)
    grid_layout(content, [[titlebar], [task_frame]], start_row=0, padx=15)  

def show_session_history_for_task(master, task: tasks.Task):
    if not task._showing_sessions:
        task._showing_sessions = True
        sessions = tasks.Session.load_sessions_for_task(task.id)
        SessionHistoryWindow(master, sessions, task)
    
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
            if new_task_dialog.result is not None:
                self.task_list.add(new_task_dialog.result)
        asset_pool = get_asset_pool(self)        
        
        rows = []
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
        self.running_session_flag.trace_add(['write'], 
            lambda v,i, m: update_start_button_state(self.running_session_flag.get()))
        
        on_task_update(task)
        for subtask in task.subtasks:
            rows.extend(self.render_task(subtask, indent+4))
        return rows
        
    def render_todo_task(self):
        """Render the special task "Misc. todos".
        
        Differences between the gui of this task and others:
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
            todo_window = TodoListWindow.show_todo_window(self, self.todo_task)
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
        # update widget states
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
        
        subscribe(task, self, 'task-state-change', on_task_update)
        self.running_session_flag.trace_add(['write'], 
            lambda v,i, m: update_start_button_state(self.running_session_flag.get()))
        
        on_task_update(task)
        return row

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

def open_config_window(master, config):
    config_win = ConfigWindow(master, "Settings", config, grid_opt={'padx': 7, 'pady': 3})
    
class ConfigWindow(tk.Toplevel):
    def __init__(self, master, title, config, grid_opt = {}, **kw):
        super().__init__(master, **kw)
        self.title(title)
        self.app_config = config
        self.grid_opt = grid_opt
        self.resizable(False, False)
        # when ok or apply is clicked, the actions in `on_ok_actions`
        # will collect values from the widgets and set it in config
        self.on_ok_actions = []
        
        frame = add_content_frame(self, padding=(20, 20, 20, 20))
        notebook = self.body(frame, config, **self.grid_opt)
        buttons = self.create_buttons(frame)
        notebook.grid(row=0, column=0, **grid_opt)
        buttons.grid(row=1, column=0, **grid_opt)

    
    def make_callback_func(self, var, path):
        """build a callback func, which will sync `var` and the configuration under `path`."""
        def callback():
            current_config = self.app_config.get_config(path)
            current_value = var.get()
            if current_config != current_value:
                self.app_config.set_config(path, current_value)
        return callback
        
    def body(self, master, config, **grid_option):
        n = ttk.Notebook(master)
        session_frame, session_focus = self.session_frame(n, config)
        n.add(session_frame, text='Session')
        session_focus.focus_set()
        appearance_frame, apprearance_focus = self.appearance_frame(n, config)
        n.add(appearance_frame, text='Appearance')
        apprearance_focus.focus_set()
        notification_frame, notification_focus = self.notification_frame(n, config)
        n.add(notification_frame, text='Notification')
        notification_focus.focus_set()
        return n
    
    def create_buttons(self, master, **grid_option):
        frame = ttk.Frame(master)
        cancel = ttk.Button(frame, text="Cancel", command=self.cancel)
        ok = ttk.Button(frame, text="OK", command=self.ok)
        apply = ttk.Button(frame, text="Apply", command=self.apply)
        grid_layout(frame, [[cancel, ok, apply]], **self.grid_opt)
        return frame
        
        
    def session_frame(self, master, config):
        nb_page = ttk.Frame(master)
        section_frames = []
        opt_paths = {
            'short': [
                ['work', 20, 45],
                ['rest', 5, 15]
            ],
            'long': [
                ['work', 40, 80],
                ['rest', 10, 20]
            ],
            'multiple': [
                ['minimum work time', 120, 160],
                ['rest', 30, 60]
            ]
        }
        first_input = None
        for section in opt_paths:
            # build section frame
            section_name = section.capitalize() + ' session'
            section_frame = ttk.LabelFrame(nb_page, text=section_name)
            section_frames.append(section_frame)
            rows = []
            for opt_name, minv, maxv in opt_paths[section]:
                path = ['session', section, opt_name]
                widget_row, vars = number_field(section_frame, opt_name.capitalize(), list(range(minv, maxv+1, 5)),
                    self.app_config.get_config(path))
                if first_input is None:
                    first_input = widget_row[1]
                #var = vars['value']
                self.on_ok_actions.append(
                    self.make_callback_func(vars['value'], path)
                )
                rows.append(widget_row)
            grid_layout(section_frame, rows, start_row=0, **self.grid_opt)
            # end section frame
            
        grid_layout(nb_page, [section_frames], start_row=0, **self.grid_opt)
        return nb_page, first_input
        
    def appearance_frame(self, master, config):
        nb_page = ttk.Frame(master)
        path_root = ['appearance']
        widget_rows = []
        # font size
        font_path = path_root + ['font', 'size']
        font_size = config.get_config(font_path)
        font_widgets, vars = number_field(nb_page, "Font size", list(range(12,20)), font_size)
        widget_rows.append(font_widgets)
        self.on_ok_actions.append(
            self.make_callback_func(vars['value'], font_path)
        )
        
        # screen size
        screen_size_path = path_root + ['screen_size']
        screen_size = config.get_config(screen_size_path)
        screen_size_widgets, vars = text_field(nb_page, "Screen Size (width x height)", screen_size)
        widget_rows.append(screen_size_widgets)
        self.on_ok_actions.append(
            self.make_callback_func(vars['value'], screen_size_path)
        )
        
        # three boolean setting:  "progress_window_on_top", "minimal_progress_window", "main_window_on_top"
        for setting_name, prompt in [
            ["progress_window_on_top", "Keep progress window on top?"],
            ["minimal_progress_window", "Use a minimal progress window?"],
            ["main_window_on_top", "Keep main window on top after session finished?"]]:
            opt_path = path_root + [setting_name]
            opt_value = config.get_config(opt_path)            
            opt_widget, vars = boolean_field(nb_page, "", prompt, opt_value)
            widget_rows.append(opt_widget)
            self.on_ok_actions.append(
                self.make_callback_func(var=vars['value'], path=opt_path)
            )
       
        grid_layout(nb_page, widget_rows, start_row=0, **self.grid_opt)
        return nb_page, font_widgets[1]
        
    def notification_frame(self, master, config):
        nb_page = ttk.Frame(master)
        widget_rows = []
        path_root = ['notification']
        
        opt_list = [
            ['show_note_editor', "Show note editor after session?"],
            ['use_audio', "Play sound as notification?"],
        ]
        for p_name, prompt in opt_list:
            opt_path = path_root + [p_name]
            opt = config.get_config(opt_path)
            opt_widget, vars = boolean_field(nb_page, "", prompt, opt)
            widget_rows.append(opt_widget)
            self.on_ok_actions.append(
                self.make_callback_func(vars['value'], opt_path)
            )
        
        audio_path = path_root + ['audio_file']
        audio_file_label = ttk.Label(nb_page, text="Alarm File:")
        audio_file = config.get_config(audio_path)
        audio_file_var = tk.StringVar()
        audio_file_var.set(audio_file)
        audio_file_entry = ttk.Entry(nb_page, textvariable=audio_file_var)
        def choose_file():
            selected = filedialog.askopenfilename(title="Select an audio file", parent=nb_page, filetypes=[("MP3 file", "*.mp3")])
            if selected:
                audio_file_var.set(selected)
        file_chooser_btn = ttk.Button(nb_page, text="File...", command=choose_file
            , style='Normal.TButton')
        widget_rows.append([audio_file_label, audio_file_entry, file_chooser_btn])
        self.on_ok_actions.append(
            self.make_callback_func(audio_file_var, audio_path)
        )
        
        grid_layout(nb_page, widget_rows, start_row=0, **self.grid_opt)
        return nb_page, widget_rows[0][0]
    
    def cancel(self):
        self.destroy()
        
    def ok(self):
        self.apply()
        self.destroy()
        
    def apply(self):
        for action in self.on_ok_actions:
            action()
        
class SessionHistoryWindow(tk.Toplevel):
    def __init__(self, master, sessions, task: tasks.Task):
        super().__init__(master)
        self.frame = add_content_frame(self)
        self.title(f'Session History: {task.description}') # type: ignore
        self.render_sessions(sessions)
        self.transient(master)
        self.bind('<Escape>', lambda e: self.destroy())
        def on_close(e):
            task._showing_sessions = False
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
        
class HelpWindow(Dialog):
    def body(self, master):
        asset_pool = get_asset_pool(master)
        content = ttk.Label(master, image=asset_pool.get_image('doc'))
        content.pack()
        self.transient(self.master.winfo_toplevel())
        
    