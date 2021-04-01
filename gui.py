from tkinter.simpledialog import Dialog
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import font

import tasks
from asset import get_asset_pool, AssetPool

def grid_layout(children_grid, start_row = 0, **opt):
    """Put a set of children in a grid layout.
    
    Repeated elements implies span, None for empty cell. For example:
    
    [[a, a, b, c],
     [a, a, d, e],
     [None, None, f, g]]
     
    means a.grid(row=0, col=0, rowspan=2, columnspan=2), b.grid(row=0,col=2), ....
    """
    seen = set()
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

class TomatoBox(ttk.Frame):
    """Render a list of images into a row of buttons.
    
    When one button is clicked, the `click_handler` will be called with its index
    as parameter.
    """
    def __init__(self, parent, tomato_config, click_handler=None, **keywords):
        ttk.Frame.__init__(self, parent, **keywords)
        self.tomatoes = []
        self.handler = click_handler
        for i, tomato in enumerate(tomato_config):
            self.create_tomato(tomato, i, click_handler)
            
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
            tomato = ttk.Button(self, image=img, command=lambda: handler(idx))
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
        grid_layout([[task_content_label], [t_label], [self.t_entry]])
        return self.t_entry
        
    def apply(self):
        self.result = self.t_entry.get('1.0', 'end')

class NewTaskDialog(Dialog):
    def __init__(self, master, title):
        Dialog.__init__(self, master, title)
        
    def body(self, master):
        get_image = get_asset_pool(self).get_image
        
        t_label = ttk.Label(master, text="Task:", anchor=tk.W)
        self.t_entry = ttk.Entry(master)
        
        c_label = ttk.Label(master, text="Tomatoes:", anchor=tk.W)
        self.tomatoes = 0
        
        def on_choose_tomato(i):
            self.tomatoes = i + 1
            tomatoes = [get_image('tomato_red')]*(i+1) + [get_image('tomato_dim')]*(5-(i+1))
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
        grid_layout(rows, 0, padx=3, pady=5)
        return self.t_entry
        
    def apply(self):
        self.result = {'description': self.t_entry.get().capitalize(),
            'tomato': self.tomatoes,
            'long_session': self.long_session_var.get()==1
        }
    
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
    def __init__(self, master, info, duration, geometry=None):
        tk.Toplevel.__init__(self, master)
        self.protocol('WM_DELETE_WINDOW', lambda: 1)
        if geometry:
            self.geometry(geometry)
        
        frame = ttk.Frame(self, padding=(10, 10, 10, 10))
        frame.grid(row=0, column=0, sticky='news')
        
        ttk.Label(frame, text=info, anchor=tk.W)\
            .grid(row=1, column=1)
        self.progress = tk.IntVar()
        ttk.Progressbar(frame, mode='determinate', variable=self.progress, maximum=duration)\
            .grid(row=2, sticky='news', column=1)

def create_task(master):
    ntDialog = NewTaskDialog(master, "New Task")
    
    if ntDialog.result:
        return tasks.Task(**ntDialog.result)
    else:
        return None
        
class TaskListFrame(tk.Frame):
    def __init__(self, master, **grid_opt):
        super().__init__(master)
        self.grid_opt = grid_opt
        self.columnconfigure(2, weight=4)
        self.columnconfigure(3, weight=1)
    
    def clear(self):
        for child in self.winfo_children():
            child.destroy()
            
    def attach_task_list(self, task_list, start_pomodoro):
        self.clear()
        asset_pool = get_asset_pool(self)
        
        rows = []
        
        # header widgets
        def add_task():
            task_data = NewTaskDialog(self.winfo_toplevel(), "New Task").result
    
            if task_data:
                new_task = tasks.Task(**task_data)
                
                task_list.add_task(new_task)
                _, row = self.grid_size()
                grid_layout([self.render_task(new_task, asset_pool, start_pomodoro)], 
                    start_row=row, **self.grid_opt)
                
        newTaskBtn = ttk.Button(self, image=asset_pool.get_image('new_icon'),
            command=add_task)
        done_label = ttk.Label(self, text="Done")
        title = ttk.Label(self, text = "Task", anchor=tk.CENTER)
        pomodoro_header = ttk.Label(self, text="Pomodoros")
        
        rows.append([newTaskBtn, done_label, title, pomodoro_header])
        rows.append([ttk.Separator(self, orient=tk.HORIZONTAL) for i in range(4)])
        
        # render tasks
        for task in task_list.tasks:
            rows.append(self.render_task(task, asset_pool, start_pomodoro))
        
        #
        grid_layout(rows, 0, **self.grid_opt)

    
    def render_task(self, task, asset_pool, start_pomodoro):
        # widgets
        get_image = asset_pool.get_image
        
        start_btn = ttk.Button(self, image=get_image('clock'), 
            state = tk.NORMAL if task.can_start() else tk.DISABLED,
            command=lambda: start_pomodoro(task))
            
        state_var = tk.IntVar()
        done_btn = tk.Checkbutton(self, variable=state_var, 
            command=lambda: task.set_done(state_var.get()))
        
        contentLabel = ttk.Label(self, text=task.description, anchor=tk.W)
        
        tomato_list = ([get_image('tomato_red')]*task.progress + 
            [get_image('tomato_green')]*task.remaining_pomodoro())
        tomatoes = TomatoBox(self, tomato_list)
        
        # observer for `task` changes
        def on_task_update(task):
            """update the presentation of the new task state"""
            font_type = 'strikeout' if task.done else 'normal'
            contentLabel.config(font = asset_pool.get_font(font_type))
            start_btn.config(state = tk.NORMAL if task.can_start() else tk.DISABLED)
            tomato_list = ([get_image('tomato_red')]*task.progress + 
                [get_image('tomato_green')]*task.remaining_pomodoro())
            tomatoes.config(tomatoes=tomato_list)
        task.attach(on_task_update)
        
        return [start_btn, done_btn, contentLabel, tomatoes]

def create_app_window(title="", geom=""):
    """Create the root window, configure some stylings and assets.
    """
    root = tk.Tk()
    root.title(title or "Python Tkinter App")
    if geom:
        root.geometry(geom)
    
    # set appearance
    style = ttk.Style()
    style.configure('TButton', relief=tk.FLAT)
    font.nametofont('TkDefaultFont')['size'] = 16
    font.nametofont('TkTextFont')['size'] = 16
    
    # add assets
    asset_pool = AssetPool(root)
    
    #    font
    normal = font.nametofont('TkDefaultFont')
    strikeout = normal.copy()
    strikeout['overstrike'] = 1
    asset_pool.add_font('normal', normal)
    asset_pool.add_font('strikeout', strikeout)
    
    #    images
    asset_pool.add_img('tomato_red', AssetPool.COLOR, 'image/tomato_red.png')
    asset_pool.add_img('tomato_bw', AssetPool.COLOR, 'image/tomato_bw.png')
    asset_pool.add_img('tomato_dim', AssetPool.COLOR, 'image/tomato_dim.png')
    asset_pool.add_img('new_icon', AssetPool.COLOR, 'image/plus.png')
    asset_pool.add_img('tomato_green', AssetPool.COLOR, 'image/tomato_green.png')
    asset_pool.add_img('clock', AssetPool.COLOR, 'image/clock.png')
    
    # attach to root, so every widget can get access to it
    root.asset_pool = asset_pool

    task_frame = TaskListFrame(root, padx=7, pady=3)
    task_frame.grid(row=0, column=0, sticky='snew', padx=15, pady=15)

    root.iconphoto(True, asset_pool.get_image('tomato_red'))
    return root, task_frame