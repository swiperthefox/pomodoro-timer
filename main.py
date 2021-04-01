from tkinter.messagebox import askyesno
import gui
import time
import tasks
import db


# The root window
app = None

class ApplicationConfig:
    long_session = (50, 10)
    short_session = (25, 5)
    long_rest = 30
    maximum_work_time_before_long_rest = 120
    center = (1920//2, 1080//2)
    @classmethod
    def get_work_time(cls, long_session):
        return cls.long_session[0] if long_session else cls.short_session[0]
    
    @classmethod
    def get_rest_time(cls, long_session):
        return cls.long_session[1] if long_session else cls.short_session[1]

def show_progress_window(info, duration, geom, callback):
    """Show a progress window, which shows the given `info` and a progress bar.
    
    The window will show for `duration` minutes, after that, call the `callback` function.
    """
    window = gui.ProgressWindow(None, info, duration, geom)

    def tick(win, start_time, duration):
        elapsed = int((time.time() - start_time)/60)
        win.progress.set(elapsed)
        if elapsed < duration:
            app.after(60100, tick, win, start_time, duration)
        else:
            window.destroy()
            app.after(1, callback)
    tick(window, time.time(), duration)
    
running_pomodoro = False

def start_pomodoro(task):
    work_time = ApplicationConfig.get_work_time(task.long_session)
    #set_window_position(app, center=False, top=False)
    app.withdraw()
    global running_pomodoro
    running_pomodoro = True
    start_time = int(time.time())
    
    show_progress_window(task.description, work_time, '+1640+0', 
        lambda: end_of_pomodoro(task, start_time))

def end_of_pomodoro(task, start_time):
    # start rest period, show a rest window
    break_time = ApplicationConfig.get_rest_time(task.long_session)
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
    show_progress_window(
        break_message_template % break_time,
        break_time,
        '+600+280',
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
        
def main(db_name):
    global app
    db.open_database(db_name)
    app, task_frame = gui.create_app_window("Pomodoro Timer", "+600+400")
    app.protocol('WM_DELETE_WINDOW', lambda: on_exit(app))
    task_list = tasks.load_task_list()
    task_frame.attach_task_list(task_list, start_pomodoro)
    app.mainloop()

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 2:
        db_name = sys.argv[1]
    else:
        db_name = 'pomodoru.sqlite'
    main(db_name)