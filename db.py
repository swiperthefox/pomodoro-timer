#from tasks import Task

import sqlite3
db = sqlite3.connect('pomodoro.sqlite3')

def open_database(db_name):
    global db
    if db:
        db.close()
    db = sqlite3.connect(db_name)
    db.row_factory = sqlite3.Row
    cur = db.cursor()
    with open('pomodoro.sqlite3.sql') as f:
        cur.executescript(f.read())
    cur.close()

load_task_sql = "SELECT * FROM task WHERE done = 0"
def load_task_list():
    cur = db.cursor()
    cur.execute(load_task_sql)
    return cur.fetchall()
    
new_task_sql = ("INSERT INTO task (description, long_session, tomato, done, progress) "
    "values (?, ?, ?, ?, ?)")
def insert_task(task):
    cur = db.cursor()
    cur.execute(new_task_sql, (task.description, task.long_session, task.tomato, task.done, task.progress))
    db.commit()
    return cur.lastrowid
    
update_task_sql_tpl = "UPDATE task SET %s WHERE id =?"
def update_task(task, **kw):
    column_names = []
    values = []
    for name, value in kw.items():
        column_names.append(name + " = ?")
        values.append(value)
    values.append(task.id)
    cur = db.cursor()
    cur.execute(update_task_sql_tpl % ', '.join(column_names), values)
    db.commit()

insert_session_sql = "INSERT INTO session (task, start, end, note) VALUES (?, ?, ?, ?)"
def insert_session(tid, start_time, end_time, note):
    cur = db.cursor()
    cur.execute(insert_session_sql, (tid, start_time, end_time, note))
    db.commit()
    return cur.lastrowid
