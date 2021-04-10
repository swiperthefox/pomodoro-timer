from dataclasses import dataclass
from typing import ClassVar, Set

from observable import Observable
import db


@dataclass
class Task(Observable):
    """A single task entry."""
    description: str
    tomato: int = 1
    long_session: bool = False
    progress: int = 0
    done: bool = False
    id: int = 0
    global_can_start: ClassVar[bool] = True
    subscribable_topics: ClassVar[Set[str]] = set(['change'])
    
    def remaining_pomodoro(self):
        return self.tomato - self.progress
        
    def incr_progress(self):
        self.progress += 1
        db.update_task(self, progress=self.progress)
        self.notify('change', self)
        
    def can_start(self):
        return Task.global_can_start and self.remaining_pomodoro() > 0 and not self.done
        
    def set_done(self, flag):
        if self.done == flag: return
        self.done = flag
        db.update_task(self, done=flag)
        self.notify('change', self)
                    
class TaskList(Observable):
    subscribable_topics = ['change', 'add']
    
    def __init__(self):
        self.tasks = []
        
    def load_from_db(self):
        tasks_data = db.load_task_list()
        self.tasks = [Task(**data) for data in tasks_data]
        self.notify('change', self.tasks)
            
    def add_task(self, task):
        self.tasks.append(task)
        task.id_ = db.insert_task(task)
        self.notify('add', task)