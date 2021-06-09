from dataclasses import dataclass, field
from tkinter.constants import S
from typing import ClassVar, List, Set
from datetime import datetime
import time
# import re
from collections import Counter

from .observable import Observable
from .noorm import Model
# import db

@dataclass
class Task(Observable, Model):
    """A single task entry."""
    _fields = {
        'description': str,
        'tomato': int,
        'long_session': bool,
        'progress': int,
        'done': bool,
        'deadline': int,
        'complete_time': int,
        'id': int,
        'parent': int
    }
    
    _showing_sessions = False 
    _topics: ClassVar[Set[str]] = set(['task-state-change'])
    subtasks: List = field(default_factory=list, init=False, hash=False)
    
    def remaining_pomodoro(self):
        return self.tomato - self.progress
        
    def incr_progress(self):
        self.progress += 1
        self.notify('task-state-change', self)
        
    def can_start(self):
        return self.remaining_pomodoro() > 0 and not self.done
        
    def set_done(self, flag):
        self.done = flag
        self.complete_time = ( datetime.today().toordinal()
            if flag
            else None)
        self.save_to_db(['done', 'complete_time'])
        if flag:
            for task in self.subtasks:
                task.set_done(flag)
        self.notify('task-state-change', self)
        
    @classmethod
    def load_list(cls, where=None, **kw):
        tasks = cls.query_db(where, **kw)
        sessions = Session.load_session_count_of_today()
        for task in tasks:
            task.progress = sessions.get(task.id, 0)
        return tasks

    @classmethod
    def get_or_create_todo_task(cls):
        todo_data = cls.query_db(description='')
        if not todo_data:
            return Task.create(description="", tomato=5, long_session=False, parent=None)
        else:
            return todo_data[0]
            
    def __type_hint(self):
        self.description = ''
        self.tomato=0
        
class TaskList(Observable):
    """TaskList keeps the tasks in a parent-child hierarchy."""
    _topics = ['change', 'add']
    def __init__(self):
        self.tasks = {}
        
    def set_task_list(self, task_list):
        for task in sorted(task_list, key=lambda task: task.id):
            self.add(task, False)
        self.notify('change', self)
        
    def __iter__(self):
        return iter(self.tasks.values())
        
    def add(self, task, notify=True):
        if task.parent is None:
            self.tasks[task.id] = task
        else:
            self.tasks[task.parent].subtasks.append(task)
        if notify:
            self.notify('change', self)
        
class TodoTask(Task):
    _topics: ClassVar[Set[str]] = set(['change', 'add', 'task-state-change'])
    
    def __init__(self, task_id):
        super().__init__(description="Misc. todos", tomato=5, parent=None) # type: ignore
        self.todos = []
        self.id = task_id
        
    @property
    def done(self):
        "A TodoTask is done if there is no unfinished todos."
        return self.unfinished == 0
    
    @done.setter
    def done(self, v):
        pass
        
    def set_done(self, flag): # type: ignore
        "Can't change todo task's state to done."
        pass
    
    @property
    def unfinished(self):
        return sum((not todo.done for todo in self.todos), 0)
        
    def add_todo(self, todo):
        self.todos.append(todo)
        self.notify('add', todo)
        # add a new todo item may also change the task's state from "done" to "not done"
        self.notify('task-state-change', self)
        
    def todo_state_changed(self, todo_id, state):
        self.notify('task-state-change', self)
        
    def set_done(self):
        raise NotImplemented
        
    def load_todo_from_db(self):
        self.todos = Todo.load_list(done=0)
        self.notify('task-state-change', self)
        
class Todo(Model, Observable):
    _fields = {
        'description': str,
        'deadline': int,
        'create_time': int,
        'done': bool,
        'complete_time': int
    }
    _topics = set(['state-change'])
    def __init__(self, description, deadline=0, create_time=0, done=False, complete_time=0, id=None):
        self.description = description
        self.deadline = deadline
        self.create_time = create_time if create_time != 0 else int(time.time())
        self.done = done
        self.complete_time = complete_time
        self.id = id
    
    def set_done_state(self, state):
        self.done = state
        if state:
            self.complete_time = int(time.time())
        self.notify('state-change', self)
        self.save_to_db()
    
    @classmethod
    def load_list(cls, **where):
        return cls.query_db(**where)


class Session(Model):
    _fields = {
        'start': int,
        'end': int,
        'note': str,
        'task': int
    }

    def __init__(self, task, start, end, note):
        self.task = task
        self.start = start
        self.end = end
        self.note = note
        
    @classmethod
    def load_sessions_for_task(cls, task_id):
        def _format_task_session(session):
            start, end, note = session
            time_format = "%Y-%m-%d %H:%M"
            return timestamp_to_string(start, time_format), timestamp_to_string(end, time_format), note
        rows = cls.query_db_fields(['start', 'end', 'note'], task=task_id)
        return [_format_task_session(row) for row in rows]
    
    @classmethod
    def load_session_history_for_today(cls):
        def _format_daily_session(session):
            task, start, end, note = session
            time_format = "%H:%M"
            return timestamp_to_string(start, time_format), timestamp_to_string(end, time_format), str(task) or "Misc. todos", note
        
        today = datetime.today()
        start_of_today = datetime(today.year, today.month, today.day, 1, 0, 0).timestamp()
        sql = """SELECT t.description, s.start, s.end, s.note 
                FROM session as s, task as t 
                WHERE s.start > ? AND s.task = t.id"""
        sessions = Session.execute_query(sql, (start_of_today,))
        return [_format_daily_session(s) for s in sessions]
    
    @classmethod
    def load_session_count_of_today(cls):
        return Counter(s[0] for s in cls.load_session_history_for_today())
        
def timestamp_to_string(timestamp, time_format):
    return datetime.fromtimestamp(timestamp).strftime(time_format)
