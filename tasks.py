from dataclasses import dataclass, field
from typing import Callable, Dict
from observable import Observable
import db

@dataclass
class Task(Observable):
    """A single task entry."""
    # def __init__(self, description, tomato, long_session, progress, done, id):
    #     self.description = description
    #     self.tomato = tomato
    #     self.long_session = long_session
    #     self.progress = progress
    #     self.done = done
    #     self.id = id
    #     self._observer_id = 0
    #     self._observers = {}
    description: str
    tomato: int = 1
    long_session: bool = False
    progress: int = 0
    done: bool = False
    id: int = 0
    # _observer_id: int = 0
    # _observers: Dict[int, Callable] = field(default_factory=dict)
    
    def remaining_pomodoro(self):
        return self.tomato - self.progress
        
    def incr_progress(self):
        self.progress += 1
        db.update_task(self, progress=self.progress)
        self.notify()
        
    def can_start(self):
        return self.remaining_pomodoro() > 0 and not self.done
        
    def set_done(self, flag):
        if self.done == flag: return
        self.done = flag
        db.update_task(self, done=flag)
        self.notify()
                    
class TaskList:
    def __init__(self, tasks):
        self.tasks = tasks
        
    def add_task(self, task):
        self.tasks.append(task)
        task.id_ = db.insert_task(task)
        
def load_task_list():
    tasks = db.load_task_list()
    return TaskList([Task(**data) for data in tasks])
