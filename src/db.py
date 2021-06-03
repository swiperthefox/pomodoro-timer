import sqlite3
import os

db = None

def open_database(db_name):
    global db
    if db:
        db.close()
    new_datebase = not os.path.isfile(db_name)    
    db = sqlite3.connect(db_name)
    db.row_factory = sqlite3.Row
    if new_datebase:
        cur = db.cursor()
        with open('pomodoro.sqlite3.sql') as f:
            cur.executescript(f.read())
        cur.close()

def execute_commit(sql, parameters):
    cur = db.cursor()
    cur.execute(sql, parameters)
    db.commit()
    return cur.lastrowid
    
def execute_query(sql, parameters):
    cur = db.cursor()
    cur.execute(sql, parameters)
    return cur.fetchall()