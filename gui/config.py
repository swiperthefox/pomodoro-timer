import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

from .utils import grid_layout, add_content_frame, number_field, boolean_field, text_field

def open_config_window(master, config):
    config_win = ConfigWindow(master, "Settings", config, grid_opt={'padx': 7, 'pady': 3})
    config_win.transient(master)
    
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
        notebook = self.body(frame, config)
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
        
    def body(self, master, config):
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
    
    def create_buttons(self, master):
        frame = ttk.Frame(master)
        cancel = ttk.Button(frame, text="Cancel", command=self.cancel)
        ok = ttk.Button(frame, text="OK", command=self.ok)
        apply = ttk.Button(frame, text="Apply", command=self.apply)
        grid_layout(frame, [[cancel, ok, apply]], **self.grid_opt)
        return frame
        
    def session_frame(self, master, config):
        nb_page = ttk.Frame(master)
        section_frames = []
        # allowed ranges for each session length opt
        opt_paths = {
            'short': [
                ['work', [20, 45]],
                ['rest', [5, 15]]
            ],
            'long': [
                ['work', [40, 80]],
                ['rest', [10, 20]]
            ],
            'multiple': [
                ['minimum work time', [120, 160]],
                ['rest', [30, 60]]
            ]
        }
        first_input = None
        for section in opt_paths:
            # build section frame
            section_name = section.capitalize() + ' session'
            section_frame = ttk.LabelFrame(nb_page, text=section_name)
            section_frames.append(section_frame)
            rows = []
            for opt_name, [minv, maxv] in opt_paths[section]:
                path = ['session', section, opt_name]
                widget_row, vars = number_field(section_frame, opt_name.capitalize(), list(range(minv, maxv+1, 5)),
                    self.app_config.get_config(path))
                if first_input is None:
                    first_input = widget_row[1]
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
