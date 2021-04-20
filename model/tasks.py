from dataclasses import dataclass, field
from typing import ClassVar, Set
from datetime import datetime
import time

from .observable import Observable
from .noorm import Model

@dataclass
class Task(Observable, Model):
    """A single task entry."""
    _fields = {
        'description': str,
        'tomato': int,
        'long_session': bool,
        'progress': int,
        'done': bool,
        'id': int
    }
    
    _topics: ClassVar[Set[str]] = set(['task-state-change'])
    
    def remaining_pomodoro(self):
        return self.tomato - self.progress # type: ignore
        
    def incr_progress(self):
        self.progress += 1
        self.notify('task-state-change', self)
        
    def can_start(self):
        return self.remaining_pomodoro() > 0 and not self.done
        
    def set_done(self, flag):
        self.done = flag
        self.save_to_db()
        self.notify('task-state-change', self)
        
    @classmethod
    def load_list(cls, **kw):
        tasks = cls.query_db(**kw)
        for task in tasks:
            task.progress = 0
        return tasks

class EntityList(Observable):
    _topics = ['change', 'add']
    
    def __init__(self, entity_class) -> None:
        super().__init__()
        self.entity_class = entity_class
        self.entities = []
    
    def load_from_db(self, **where):
        self.entities = self.entity_class.load_list(**where)
        self.notify('change', self.entities)
        
    def add(self, entity):
        self.entities.append(entity)
        self.notify('add', entity)

class TodoTask(Task):
    _topics: ClassVar[Set[str]] = set(['change', 'add', 'task-state-change'])
    
    def __init__(self, todo_list: EntityList):
        super().__init__(description="Misc. todos", tomato=5) # type: ignore
        self.todos = todo_list
        self.id = 0 # an id that not possible for other auto generated ones, sqlite3 specific.
        
    @property
    def done(self):
        "TodoTask's is done if there is no todos unfinished."
        return self.unfinished == 0
    
    @done.setter
    def done(self, v):
        pass
        
    def set_done(self, flag): # type: ignore
        "Can't change todo task's state to done."
        pass
    
    @property
    def unfinished(self):
        return sum((not todo.done for todo in self.todos.entities), 0)
        
    def add_todo(self, todo):
        self.todos.add(todo)
        self.notify('add', todo)
        # add a new todo item may also change the task's state from "done" to "not done"
        self.notify('task-state-change', self)
        
    def set_todo_state(self, todo_id, state):
        "Change the `done` state of the given todo."
        for todo in self.todos.entities:
            if todo.id == todo_id:
                todo.set_done_state(state)
                break
        self.notify('task-state-change', self)
        
    def set_done(self):
        raise NotImplemented
        
class Todo(Model, Observable):
    _fields = {
        'description': str,
        'deadline': int,
        'create_time': int,
        'done': bool,
        'complete_time': int
    }
    _topics = set(['state-change'])
    def __init__(self, description, deadline = 0, create_time = 0, done = False, complete_time = 0, id = 0):
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
    start = 0
    end = 0
    note = ''
    task = 0
    
    def __init__(self, task, start, end, note):
        self.task = task
        self.start = start
        self.end = end
        self.note = note
        
    @staticmethod
    def format_session(session):
        start, end, note = session
        return timestamp_to_string(start), timestamp_to_string(end), note
    
    @classmethod
    def load_sessions_for_task(cls, task_id):
        rows = cls.query_db_fields(['start', 'end', 'note'], task=task_id)
        return [cls.format_session(row) for row in rows]
    
    @classmethod
    def insert_session(cls, *args, **kw):
        cls.create(*args, **kw)
                
def timestamp_to_string(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")
