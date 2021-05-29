from dataclasses import dataclass, field
from typing import ClassVar, List, Set
from datetime import datetime
import time

from .observable import Observable
from .noorm import Model
import db
from utils import PeriodicScheduler

@dataclass
class Task(Observable, Model):
    """A single task entry."""
    _fields = {
        'description': str,
        'tomato': int,
        'long_session': bool,
        'progress': int,
        'done': bool,
        'id': int,
        'parent': int
    }
    
    _showing_sessions = False 
    _topics: ClassVar[Set[str]] = set(['task-state-change'])
    subtasks: List = field(default_factory=list, init=False, hash=False)
    
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
        if flag:
            for task in self.subtasks:
                task.set_done(flag)
        self.notify('task-state-change', self)
        
    @classmethod
    def load_list(cls, **kw):
        tasks = cls.query_db(**kw)
        sessions = Session.load_sessions_of_today()
        for task in tasks:
            task.progress = sessions.get(task.id, 0)
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
    
    def __iter__(self):
        return iter(self.entities)
    
    def __getitem__(self, index):
        return self.entities[index]
            
class TaskList(EntityList):
    def __init__(self):
        super().__init__(Task)
        self.todo_task_id = None
        
    def load_from_db(self, **where):
        super().load_from_db(**where)
        self.todo_task_id = self.find_or_create_todo_task()
        self.tasks = {}
        for task in self.entities:
            self.add(task)
        
    def find_or_create_todo_task(self):
        """Find the special todo task from task_list, remove it from the list and return the task's id.
        If the task doesn't exist, create a new special task and return it's id.
        """
        for i, task in enumerate(self.entities):
            # The special todo task has an empty description. It's not possible for users to create such 
            # kind of task (see NewTaskDialog), so this is a reliable way to identify the task.
            if task.description == "":
                return self.entities.pop(i).id

        todo_task = Task.create(description="", tomato=5, long_session=False)
        return todo_task.id
        
    def __iter__(self):
        return iter(self.tasks.values())
        
    def add(self, task):
        if task.parent is None:
            self.tasks[task.id] = task
        else:
            self.tasks[task.parent].subtasks.append(task)
        self.notify('change', self)
        
class TodoTask(Task):
    _topics: ClassVar[Set[str]] = set(['change', 'add', 'task-state-change'])
    
    def __init__(self, task_id, todo_list: EntityList):
        super().__init__(description="Misc. todos", tomato=5) # type: ignore
        self.todos = todo_list
        self.id = task_id
        
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
    def __init__(self, description, deadline = 0, create_time = 0, done = False, complete_time = 0, id = None):
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
    
    @classmethod
    def load_sessions_of_today(cls):
        today = datetime.today()
        start_of_today = datetime(today.year, today.month, today.day, 1, 0, 0).timestamp()
        sql = 'SELECT task, count(*) FROM session WHERE start > ? GROUP BY task'
        session_count = db.execute_query(sql, (int(start_of_today),))
        return {task: c for task, c in session_count}

class ScheduledTask(Model):
    _table_name = "repeated_task"
    _fields = {
        'title': str,
        'tomato': int,
        'schedule': str,
        'last_scheduled': int,
        'type': int
    }
    LONG = 3
    SHORT = 2
    TODO = 1
    def __init__(self, title, tomato, schedule, last_scheduled, type, id):
        self.title = title
        self.tomato = tomato
        self.schedule = schedule,
        self.last_scheduled = last_scheduled
        self.type = type
        self.id = id
        
    def get_new_task(self, today: datetime):
        "Get the (possibly) new task for `today`."
        scheduler = PeriodicScheduler(self.schedule)
        today = datetime.today()
        last_schedule_date = datetime.fromtimestamp(self.last_scheduled)
        if today.date() == last_schedule_date.date(): # just scheduled for today
            return None
            
        if scheduler.should_schedule(today):
            return dict(description=self.title, tomato = self.tomato, type=self.type) 
        else:
            return None
        
    def update_last_schedule_date(self):
        today = datetime.today()
        self.last_scheduled = int(today.timestamp())
        self.save_to_db(['last_scheduled'])
        
def timestamp_to_string(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")

def parse_task(task_description):
    """Parse the extended task description, return a Task.
    
    A task can be specified in an "extended task description" format. The format is as follows:
    
    task_title #n [optional fields]
    
    where `task_title` is the description of the task and `n` is the number of session assigned.
    
    The optional fields are some fields that starts with some special characters. The fields could
    appear in any order.
    
    - @show_time: When to list the task in the task list. Multiple show times will be combined.
    
    Possible format: 
    1. @04-15: show at the given date. If the date is not valid, use the latest day that is prior
    to the given date (for example: @4-32 will be transferred to the last day of April.)
    2. @Mon (Tue, Wed, Thu, Fri, Sat, Sun): show at the upcoming given day of week.
    3. @+10, @+2w, @+1m: a day relative to today.
    
    - *repeat_pattern: Repeatedly show the task in the given pattern.
    
    Possible format:
    1. *w, *m, *y: repeat every week, month or year.
    2. *Mon, *m12, *y04-13: these formats combine the show time with repeat time (Monday on every week,
    on 12th every month, or April 13 every year.). If there are also @fields, all the show times will be
    combined.
    
    - =duration: The duration type of session. Default is short session.
    
    Possible format:
    "==" for long session, "=-" for short session and "=." for todos.
    
    - ^parent_title^: specifies the parent task. The first task in current list that matches the given
    `parent_title` will be the parent of this task. Repeated tasks can't have parent task, if `*` field
    is given, this field will be ignored.
    """