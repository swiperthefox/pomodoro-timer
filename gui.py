from subprocess import run
from tkinter.simpledialog import Dialog
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import font
from tkinter import filedialog
import time

import tasks
from asset import get_asset_pool, AssetPool, get_root

##
#  General helper functions
##
def grid_layout(parent, children_grid, start_row = tk.END, **opt):
    """Put a set of children in a grid layout.
    
    Repeated elements implies span, None for empty cell. For example:
    
    [[a, a, b, c],
     [a, a, d, e],
     [None, None, f, g]]
     
    means a.grid(row=0, col=0, rowspan=2, columnspan=2), b.grid(row=0,col=2), ....
    
    if the rows have different length, the last elments of shorter row will span over
    the rest of columns.
    """
    if start_row == tk.END:
        start_row = parent.grid_size()[1]

    seen = set()
    max_row_length = max(len(row) for row in children_grid)
    for row in children_grid:
        row.extend([row[-1]]*(max_row_length - len(row)))
        
    for r, row in enumerate(children_grid):
        for c, w in enumerate(row):
            if w is None or w in seen:
                continue
            row_span = 0
            while r + row_span < len(children_grid) and w == children_grid[r+row_span][c]:
                row_span += 1
            col_span = 0
            while c + col_span < len(row) and w == row[c+col_span]:
                col_span += 1
            
            w.grid(row=r+start_row, column = c, rowspan=row_span, columnspan=col_span, sticky='news', **opt)
            seen.add(w)
def text_field(master, prompt, initial):
    label = ttk.Label(master, text=prompt)
    var = tk.StringVar()
    var.set(initial)
    entry = ttk.Entry(master, textvariable=var)
    return [label, entry], {'value': var}
    
def boolean_field(master, prompt, info, initial):
    label = ttk.Label(master, text=prompt)
    var = tk.BooleanVar()
    var.set(initial)
    button = ttk.Checkbutton(master, variable=var, text=info)
    return [label if prompt else button, button], {'value': var}
    
def radio_field(master, prompt, options, initial):
    widgets = []
    label = ttk.Label(master, text=prompt)
    widgets.append(label)
    var = tk.StringVar()
    var.set(initial)
    if len(options[0]) == 1:
        options = [(opt, opt) for opt in options]
    for text, value in options:
        button = ttk.Radiobutton(master, text=text, value=value, variable=var)
        widgets.append(button)
    return widgets, {'value': var}
    
def number_field(master, prompt, choices, initial):
    label = ttk.Label(master, text=prompt)
    var = tk.IntVar()
    var.set(initial)
    combbox = ttk.Combobox(master, values=choices, textvariable=var, width=4)
    return [label, combbox], {'value': var}

##
# GUI Components and Dialogs
##

def render_app_window(app, title="", geom=""):
    """Create the root window, configure some stylings and assets."""
    # configuration of the appearance
    app_config = app.config
    
    root = app.window
    root.title(title)
    if geom:
        root.geometry(geom)
    root.rowconfigure(0,weight=1)
    root.columnconfigure(0,weight=1)
    
    # set appearance
    style = ttk.Style()
    style.configure('TButton', relief=tk.FLAT)
    
    # add assets
    asset_pool = AssetPool(root)
    
    #    font
    normal = font.nametofont('TkDefaultFont')
    strikeout = normal.copy()
    strikeout['overstrike'] = 1
    asset_pool.add_font('normal', normal)
    asset_pool.add_font('strikeout', strikeout)
    asset_pool.add_font('text', font.nametofont('TkTextFont'))
    asset_pool.set_font_property('size', app_config.get_font_size())
    
    #    images
    asset_pool.add_img('tomato_red', AssetPool.COLOR, 'image/tomato_red.png')
    asset_pool.add_img('tomato_bw', AssetPool.COLOR, 'image/tomato_bw.png')
    asset_pool.add_img('tomato_dim', AssetPool.COLOR, 'image/tomato_dim.png')
    asset_pool.add_img('new_icon', AssetPool.COLOR, 'image/plus.png')
    asset_pool.add_img('tomato_green', AssetPool.COLOR, 'image/tomato_green.png')
    asset_pool.add_img('clock', AssetPool.COLOR, 'image/clock.png')
    
    # attach asset_pool to root, so every widget can access it
    root.asset_pool = asset_pool

    root.iconphoto(True, asset_pool.get_image('tomato_red'))
    
    # create GUI components
    ttk.Button(root, text="Setting", command=lambda: open_config_window(root, app_config)).grid(row=0, column=1)
    task_frame = TaskListFrame(root, padx=7, pady=3)
    task_frame.grid(row=0, column=0, sticky='snew', padx=15, pady=15)    
    task_frame.attach_task_list(app.task_list, app.start_session, app.running_session)

class TaskListFrame(tk.Frame):
    def __init__(self, master, **grid_opt):
        super().__init__(master)
        self.task_list = None
        self.grid_opt = grid_opt
        self.asset_pool = get_asset_pool(self)
        self.columnconfigure(2, weight=4)
        self.columnconfigure(3, weight=1)
    
    def clear(self):
        for child in self.winfo_children():
            child.destroy()
            
    def attach_task_list(self, task_list, start_pomodoro, running_session_flag):
        # 
        if self.task_list:
            self.task_list.unsubscribe('change', observer=self.render_list)
            self.task_list.unsubscribe('add', observer=self.render_task)
            
        self.task_list = task_list
        task_list.subscribe('change', self.render_task_list)
        task_list.subscribe('add', self.render_task)
        self.start_pomodoro_command = start_pomodoro
        self.running_session_flag = running_session_flag
        self.render_list(task_list)

    def render_list(self, task_list):
        self.clear()
        self.render_header()
        for task in task_list.tasks:
            self.render_task(task)
        
    def render_header(self):
        # newTaskBtn handler
        def add_task():
            new_task_dialog = NewTaskDialog(self.winfo_toplevel(), "Add Task")
            if new_task_dialog.result is not None:
                self.task_list.add_task(new_task_dialog.result)
        asset_pool = get_asset_pool(self)        
        
        rows = []
        # header widgets
        newTaskBtn = ttk.Button(self, image=asset_pool.get_image('new_icon'),
            command=add_task)
        done_label = ttk.Label(self, text="Done")
        title = ttk.Label(self, text = "Task", anchor=tk.CENTER)
        pomodoro_header = ttk.Label(self, text="Pomodoros")
        
        rows.append([newTaskBtn, done_label, title, pomodoro_header])
        rows.append([ttk.Separator(self, orient=tk.HORIZONTAL) for i in range(4)])
        
        grid_layout(self, rows, start_row=0, **self.grid_opt)
    
    def render_task_list(self, tasks):
        for task in tasks:
            self.render_task(task)
            
    def render_task(self, task):
        get_image = self.asset_pool.get_image
        
        # the layout for a task is as follows
        #     [start] [done] task title  RRGGG
        # where  [button] is a button, R and G are red and green tomato images
        start_btn = ttk.Button(self, image=get_image('clock'), 
            state = tk.NORMAL if task.can_start() else tk.DISABLED,
            command=lambda: self.start_pomodoro_command(task))
            
        state_var = tk.IntVar()
        done_btn = tk.Checkbutton(self, variable=state_var, 
            command=lambda: task.set_done(state_var.get()))
        
        titleLabel = ttk.Label(self, text=task.description, anchor=tk.W)
        
        tomato_list = ([get_image('tomato_red')]*task.progress + 
            [get_image('tomato_green')]*task.remaining_pomodoro())
        tomatoes = TomatoBox(self, tomato_list)
        
        row = [start_btn, done_btn, titleLabel, tomatoes]
        grid_layout(self, [row], start_row=tk.END, **self.grid_opt)
        
        # register observers that will update the components on app state change
        
        # observer for changes of task
        def on_task_update(task=task):
            """update the presentation of the new task state"""
            font_type = 'strikeout' if task.done else 'normal'
            titleLabel.config(font = self.asset_pool.get_font(font_type))
            update_start_button_state(self.running_session_flag.get())
            tomato_list = ([get_image('tomato_red')]*task.progress + 
                [get_image('tomato_green')]*task.remaining_pomodoro())
            tomatoes.config(tomatoes=tomato_list)
        # observer for change of `running_session_flag`
        def update_start_button_state(has_running_session):
            can_start = not has_running_session and task.can_start()
            start_btn.config(state = tk.NORMAL if can_start else tk.DISABLED)
            
        task.subscribe('change', on_task_update)
        self.running_session_flag.trace_add(['write'], 
            lambda v,i, m: update_start_button_state(self.running_session_flag.get()))



class TomatoBox(tk.Frame):
    """Render a list of images into a row of buttons.
    
    When one button is clicked, the `click_handler` will be called with its index
    as parameter.
    """
    def __init__(self, parent, tomato_config, click_handler=None, **keywords):
        tk.Frame.__init__(self, parent, takefocus=1, highlightthickness=1, **keywords)
        self.tomatoes = []
        self.handler = click_handler
        for i, tomato in enumerate(tomato_config):
            self.create_tomato(tomato, i, click_handler)
        self.bind("<KeyPress>", self.keypress_handler)
        
    def keypress_handler(self, e):
        keysym_map = {"1": 1, "2": 2, "3": 3, "4": 4, "5":5,
            "KP_1": 1, "KP_2": 2, "KP_3": 3, "KP_4": 4, "KP_5": 5}
        if e.keysym in keysym_map:
            self.handler(keysym_map[e.keysym])
    def configure(self, cnf={}, **kw):
        kwargs = cnf.copy()
        kwargs.update(kw)
        if 'tomatoes' in kwargs:
            tomato_config = kwargs.pop('tomatoes')
            min_l = min(len(self.tomatoes), len(tomato_config))
            for button in self.tomatoes[min_l:]: # remove the extra ones
                button.destroy()
            self.tomatoes = self.tomatoes[:min_l]
            for tomato, button in zip(tomato_config, self.tomatoes): # update the existing ones
                button.config(image=tomato)
            for j, tomato in enumerate(tomato_config[min_l:]): # add more if needed
                self.create_tomato(tomato, min_l + j, self.handler)
        super().configure(cnf=kwargs)
        
    config = configure
    
    def create_tomato(self, img, idx, handler):
        if handler is None:
            tomato = ttk.Label(self, image=img)
        else:
            tomato = ttk.Button(self, image=img, takefocus=0, command=lambda: handler(idx+1))
        self.tomatoes.append(tomato)
        tomato.pack(side=tk.LEFT)
        return tomato

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

class NewTaskDialog(Dialog):
    """A dialog for creating a new task."""
    def __init__(self, master, title):
        Dialog.__init__(self, master, title)
        
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
        session_type_label = ttk.Label(master, text="Type:", anchor=tk.W)
        long_session_btn = ttk.Checkbutton(master, text="Long session",
            variable=self.long_session_var)
        
        self.error_var = tk.StringVar()
        error_label = ttk.Label(master, textvariable=self.error_var, foreground='red', anchor=tk.W)
        
        rows = [[t_label,              self.t_entry],
                [c_label,              tomatobox],
                [session_type_label,   long_session_btn],
                [error_label,          error_label]]
        grid_layout(master, rows, 0, padx=3, pady=5)
        return self.t_entry
        
    def apply(self):
        self.result = tasks.Task(**{'description': self.t_entry.get().capitalize(),
            'tomato': self.tomatoes,
            'long_session': self.long_session_var.get()==1
        })
    
    def validate(self):
        if len(self.t_entry.get().strip()) == 0:
            self.error_var.set("Task description can't be empty .")
            return False
        if self.tomatoes == 0:
            self.error_var.set("Must choose some tomatoes.")
            return False
        self.error_var.set('')
        return True

class ProgressWindow(tk.Toplevel):
    """A window to show the progress of a session.
    
    A minimal version will only show a text like "15/45", which means 15 minutes 
    passed in a 45 minutes session.
    A normal version will show the task's description and a progress bar.
    """
    def __init__(self, master, info, duration, geometry=None, keep_on_top=False, minimize=False):
        self.duration = duration
        self.tick_interval = min(60000, duration*60000//20) # 60000 = 1 minute
        tk.Toplevel.__init__(self, master)
        self.protocol('WM_DELETE_WINDOW', lambda: 1)
        self.progress = self.text = None
        self.progress_text = tk.StringVar(value=f'00/{duration}')
        self.overrideredirect_flag = False
        self.geometry_value = geometry
        
        if geometry:
            self.geometry(geometry)
        if keep_on_top:
            self.attributes('-topmost', True)
        
        frame = ttk.Frame(self)
        frame.grid(row=0, column=0, sticky='news')
        pbar_text = ttk.Label(frame, textvariable=self.progress_text) # for "15/45"
        
        if not minimize:
            # Layout:
            # ----------------------------------
            # | The task's description         |
            # | 15/45 [----     ]              |
            # ----------------------------------
            frame.config(padding=(10,10,10,10))
            self.text = tk.StringVar(value=info)
            text = ttk.Label(frame, textvariable=self.text, anchor=tk.W)
            self.progress = tk.IntVar()
            pbar = ttk.Progressbar(frame, mode='determinate', variable=self.progress, maximum=duration)
            grid_layout(frame, [[text], [pbar_text, pbar]], start_row=0)
        else:
            # minimal layout, just
            # 15/45
            self.overrideredirect_flag = True
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
                self.progress.set(elapsed)
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
        
# def create_new_task(master):
#     task_data = NewTaskDialog(master, "New Task").result
#     if task_data:
#         return tasks.Task(**task_data)
#     else:
#         return None
        

def open_config_window(master, config):
    config_win = ConfigWindow(master, "Settings", config, grid_opt={'padx': 7, 'pady': 3})
    
def get_screen_size(w):
    w.attributes("-fullscreen", True)
    w.update_idletasks()
    geometry = w.geometry()
    w.attributes("-fullscreen", False)
    return geometry.split('+')[0]
    
class ConfigWindow(tk.Toplevel):
    def __init__(self, master, title, config, grid_opt = {}, **kw):
        super().__init__(master, **kw)
        self.title(title)
        self.config = config
        self.grid_opt = grid_opt
        
        # actions that collect values from fields and set it in config
        # when ok or apply is clicked.
        self.on_ok_actions = []
        
        frame = ttk.Frame(self)
        frame.grid(row=0, column=0)
        self.body(frame, config)
        self.create_buttons(frame)
    
    def make_callback_func(self, var, path):
        """build a callback func, which will sync `var` and the configuration under `path`."""
        def callback():
            current_config = self.config.get_config(path)
            current_value = var.get()
            if current_config != current_value:
                self.config.set_config(path, current_value)
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
        n.pack(side=tk.TOP)
        n.grid(**grid_option)
    
    def create_buttons(self, master, **grid_option):
        frame = ttk.Frame(master)
        cancel = ttk.Button(frame, text="Cancel", command=self.cancel)
        ok = ttk.Button(frame, text="OK", command=self.ok)
        apply = ttk.Button(frame, text="Apply", command=self.apply)
        grid_layout(frame, [[cancel, ok, apply]], **self.grid_opt)
        frame.grid(grid_option)
        
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
                    self.config.get_config(path))
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
        file_chooser_btn = ttk.Button(nb_page, text="File...", command=choose_file)
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
        
