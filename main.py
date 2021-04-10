import tkinter
from tkinter.messagebox import askyesno
import time
import json

import gui
import tasks
import db
import observable
import audio

class JsonBasedConfig(observable.Observable):
    subscribable_topics = ['change']
    def __init__(self, config_file) -> None:
        with open(config_file) as f:
            self.config = json.load(f)
        #self.app = app
        self.config_file = config_file
        
    def save(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
            
    def get_config(self, path):
        current = self.try_path(self.config, path)
        if current is None:
            return self.get_default_config(path)
        else:
            return current
            
    def get_default_config(self, path):
        return self.try_path(self.config['default'], path)
        
    def set_config(self, path, value):
        d = self.config
        for k in path[:-1]:
            d = d.setdefault(k, {})
        d[path[-1]] = value
        self.save()
        self.notify('change', path, value)
    
    @staticmethod
    def try_path(d, path):
        for k in path:
            if k in d:
                d = d[k]
            else:
                return None
        return d
        
class PomodoroTimerConfig(JsonBasedConfig):
    def get_time(self, long_session, type):
        s_type = 'long' if long_session else 'short'
        return self.get_config(['session', s_type, type])
    def get_font_size(self):
        return self.get_config(['appearance', 'font', 'size'])
    def get_progress_on_top(self):
        return self.get_config(['appearance', 'progress_on_top'])
    def get_minimal_progress_window(self):
        return self.get_config(['appearance', 'minimal_progress_window'])
    def get_main_window_on_top(self):
        return self.get_config(['appearance', 'main_window_on_top'])
    def show_note_editor(self):
        return self.get_config(['notification', 'show_note_editor'])
    def use_audio_alert(self):
        return self.get_config(['notification', 'use_audio'])
    def get_audio_file(self):
        return self.get_config(['notification', 'audio_file'])
        
class App:
    def __init__(self, db_name, title):
        # data
        self.config = PomodoroTimerConfig('config.json')
        db.open_database(db_name)        
        self.task_list = tasks.TaskList()
        self.task_list.load_from_db()
        
        # gui
        self.window = tkinter.Tk()
        self.running_session = tkinter.BooleanVar(value=False)
        gui.render_app_window(self, title, "+600+400")
        self.window.protocol('WM_DELETE_WINDOW', self.on_exit)
        
        def on_font_change(path, value):
            # If the font is changed, we need to apply it to the app now
            if path[-2] == 'font':
                self.window.asset_pool.set_font_property(path[-1], value)
        self.config.subscribe('change', on_font_change)
        
        #task_frame.attach_task_list(task_list, self.start_session, self.running_session)
       
        self.show_main_window()
        self.window.mainloop()

    def start_session(self, task):
        work_time = self.config.get_time(task.long_session, 'work')
        
        #self.window.withdraw()
        self.window.attributes('-topmost', False)
        self.running_session.set(True)
        
        window = gui.ProgressWindow(self.window, task.description, work_time, geometry='+1640+3',
            keep_on_top=self.config.get_progress_on_top(),
            minimize=self.config.get_minimal_progress_window())
        window.start(lambda: self.end_of_session(task, start_time = int(time.time())))

    def end_of_session(self, task, start_time):
        self.running_session.set(False)
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
            note_editor = gui.SessionNoteDialog(self.window, task.description, "Session Note")
            note = note_editor.result.strip() if note_editor.result else  ""
        else:
            note = ""
        db.insert_session(task.id, start_time, end_time, note)
    
    def start_rest(self, break_time):
        break_message_template = """\
        Take a %d minutes break.
        Walk a bit, drink some water, and relax.
        """
        window = gui.ProgressWindow(self.window, 
            break_message_template % break_time,
            break_time,
            '+600+280',
            keep_on_top=self.config.get_progress_on_top())
        window.start(self.show_main_window)
        
    def show_main_window(self):
        self.window.deiconify()
        keep_main_window_on_top = self.config.get_main_window_on_top()
        self.window.attributes('-topmost', keep_main_window_on_top)
    
    def on_exit(self):
        if self.running_session.get():
            warning = "There is a running Pomodoro session, are you sure to close the app?"
            close = askyesno(title="Quit", message=warning)
            if close:
                self.window.quit()
        else:
            self.window.quit()

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 2:
        db_name = sys.argv[1]
        title = "Pomodoro Timer"
    else:
        db_name = 'test.sqlite3'
        title = "Pomodoro Timer (dev)"
    App(db_name, title)