from .simpledialog import Dialog
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import font
import datetime

from asset import AssetPool
from gui.utils import *
from .tasklistframe import TaskListFrame
from .config import open_config_window

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
    asset_pool.add_img('tomato_dim', AssetPool.COLOR, 'image/tomato_dim.png')
    asset_pool.add_img('tomato_green', AssetPool.COLOR, 'image/tomato_green.png')
    asset_pool.add_img('tomato_red_small', AssetPool.COLOR, 'image/tomato_red_small.png')
    asset_pool.add_img('tomato_green_small', AssetPool.COLOR, 'image/tomato_green_small.png')
    asset_pool.add_img('new_icon', AssetPool.COLOR, 'image/plus.png')
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
    dm = app.dm
    task_frame = TaskListFrame(content,
        dm.task_list, dm.todo_task, app.start_session, app.session_running,
        padx=7, pady=3)
    grid_layout(content, [[titlebar], [task_frame]], start_row=0, padx=15)  



    