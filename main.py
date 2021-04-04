from tkinter.messagebox import askyesno
import gui
import time
import tasks
import db


# The root window
app = None

import json

class ApplicationConfig:
    def __init__(self, config_file) -> None:
        with open(config_file) as f:
            self.config = json.load(f)

    def get_work_time(self, long_session):
        s_type = 'long' if long_session else 'short'
        return self.config['session'][s_type]['work']
    
    def get_rest_time(self, long_session):
        s_type = 'long' if long_session else 'short'
        return self.config['session'][s_type]['rest']
        
running_pomodoro = False

def start_pomodoro(task):
    work_time = app_config.get_work_time(task.long_session)

    app.withdraw()
    global running_pomodoro
    running_pomodoro = True
    start_time = int(time.time())
    
    window = gui.ProgressWindow(app, task.description, work_time, geometry='+1640+0')
    window.start(lambda: end_of_pomodoro(task, start_time))

def end_of_pomodoro(task, start_time):
    # start rest period, show a rest window
    break_time = app_config.get_rest_time(task.long_session)
    start_rest(break_time)
    app.update_idletasks()
    
    global running_pomodoro
    running_pomodoro = False
    end_time = time.time()
    
    # at the same time, allow user enter a short note about last session
    note_editor = gui.SessionNoteDialog(app, task.description, "Session Note")
    note = note_editor.result.strip() if note_editor.result else  ""
    db.insert_session(task.id, start_time, end_time, note)
    task.incr_progress()
    
def start_rest(break_time):
    break_message_template = """\
    Take a %d minutes break.
    Walk a bit, drink some water, and relax.
    """
    window = gui.ProgressWindow(app, 
        break_message_template % break_time,
        break_time,
        '+600+280')
    window.start(
        app.deiconify
    )

def on_exit(app):
    warning = "There is a running Pomodoro session, are you sure to close the app?"
    if running_pomodoro:
        close = askyesno(title="Quit", message=warning)
        if close:
            app.quit()
    else:
        app.quit()
import tkinter as tk

mode = 'dev'
def main(db_name):
    global app
    db.open_database(db_name)
    title = "Pomodoro Timer" + ("(dev)" if mode=='dev' else "")
    app, task_frame = gui.create_app_window(title, "+600+400")
    app.protocol('WM_DELETE_WINDOW', lambda: on_exit(app))
    task_list = tasks.TaskList()
    task_list.load_from_db()
    task_frame.attach_task_list(task_list, start_pomodoro)
    app.mainloop()

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 2:
        db_name = sys.argv[1]
    else:
        db_name = 'test.sqlite'
    app_config = ApplicationConfig('config.json')
    print(app_config)
    main(db_name)