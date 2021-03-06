import tkinter
from tkinter.messagebox import askyesno
import time
from datetime import date
import os

from gui.app import render_app_window
from gui.progresswindow import ProgressWindow
from gui.sessionnotedialog import SessionNoteDialog
from gui.help import HelpWindow

from model import appconfig, models
import audio
from datamanager import DataManager

APP_DB = 'app.sqlite3'
class App:
    def __init__(self, db_name, title):
        # data
        self.config = appconfig.PomodoroTimerConfig('config.json')
        first_run = not os.path.exists(db_name)
        self.dm = DataManager(db_name)

        # gui
        self.window = tkinter.Tk(className='Pomodoro Timer')
        self.session_running = tkinter.BooleanVar(value=False)
        render_app_window(self, title, "+700+400")
        self.window.protocol('WM_DELETE_WINDOW', self.on_exit)
        
        def on_font_change(path, value):
            # If the font is changed, we need to apply it to the app now
            if path[-2] == 'font':
                self.window.asset_pool.set_font_property(path[-1], value) # type: ignore
        self.config.subscribe('change', on_font_change)
        self.show_main_window()
        self.start_cron()
        if first_run:
            help = HelpWindow(self.window, "Quick Start")
        self.window.mainloop()

    def start_session(self, task):
        work_time = self.config.get_time(task.long_session, 'work')
        
        #self.window.withdraw()
        self.window.attributes('-topmost', False)
        self.window.lower()
        self.session_running.set(True)
        
        window = ProgressWindow(self.window, task.description, work_time, geometry=self.config.get_progress_position(),
            keep_on_top=self.config.get_progress_on_top(),
            minimize=self.config.get_minimal_progress_window())
        start_time = int(time.time())
        window.start(lambda: self.end_of_session(task, start_time))

    def end_of_session(self, task, start_time):
        default_audio_alert = "snd/egg_timer.mp3"
        if self.config.use_audio_alert():
            audio.playsound(self.config.get_audio_file() or default_audio_alert, block=True)
        
        # start rest period, show a progress window
        break_time = self.config.get_time(task.long_session, 'rest')
        self.start_rest(break_time)
        self.window.update_idletasks()
        
        task.incr_progress()
        
        end_time = int(time.time())
        if self.config.show_note_editor():
            # at the same time, allow the user enter a short note about last session
            note_editor = SessionNoteDialog(self.window, task.description, "Session Note")
            note = note_editor.result.strip() if note_editor.result else  ""
        else:
            note = ""
        models.Session.create(task.id, start_time, end_time, note)
    
    def start_rest(self, break_time):
        break_message_template = """\
        Take a %d minutes break.
        Walk a bit, drink some water, and relax.
        """
        window = ProgressWindow(self.window, 
            break_message_template % break_time,
            break_time,
            '+600+280',
            keep_on_top=False)
        window.start(self.show_main_window)
        
    def show_main_window(self):
        self.session_running.set(False)
        self.window.deiconify()
        keep_main_window_on_top = self.config.get_main_window_on_top()
        self.window.attributes('-topmost', keep_main_window_on_top)
    
    def on_exit(self):
        if self.session_running.get():
            warning = "There is a running Pomodoro session, are you sure to close the app?"
            close = askyesno(title="Quit", message=warning)
            if close:
                self.window.quit()
        else:
            self.window.quit()

    def start_cron(self):
        def reload_task(last_reload_date):
            today = date.today().toordinal()
            if today != last_reload_date:
                self.dm.load_data(today)
                last_reload_date = today
            self.window.after(3600000, reload_task, last_reload_date) # 3600000 = 1 hour
        reload_task(0)
        
if __name__ == '__main__':
    import sys, os

    if sys.flags.dev_mode or 'DEBUG' in os.environ:
        db_name = 'test.sqlite3'
        title = "Pomodoro Timer (dev)"
    else:
        db_name = "app.sqlite3"
        title = "Pomodoro Timer"
    App(db_name, title)