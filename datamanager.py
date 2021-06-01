"""Manage instance of task list, todo list, and scheduled tasks, corrdinate their
interactions.
"""
from model import models
from model.scheduledtask import ScheduledTask
import db

class DataManager:
    def __init__(self, db_name):
        db.open_database(db_name)
        
        self.task_list = models.TaskList()
        todo_task = models.Task.get_or_create_todo_task()
        self.todo_task = models.TodoTask(todo_task.id)
        
    def load_data(self, today):
        task_list = models.Task.load_list({'description <>': ''}, done=0)
        self.task_list.set_task_list(task_list)
        self.todo_task.load_todo_from_db()
        
        for schdedule in ScheduledTask.query_db():
            new_task = schdedule.get_task_for_date(today)
            if isinstance(new_task, models.Todo):
                self.todo_task.add_todo(new_task)
            elif isinstance(new_task, models.Task):
                self.task_list.add(new_task)
