"""Manage instance of task list, todo list, and scheduled tasks, corrdinate their
interactions.
"""
from model import tasks
from model.scheduledtask import ScheduledTask
import db

class DataManager:
    def __init__(self, db_name):
        db.open_database(db_name)
        
        self.task_list = tasks.TaskList()
        todo_task = tasks.Task.get_or_create_todo_task()
        self.todo_task = tasks.TodoTask(todo_task.id)
        
    def load_data(self, today):
        task_list = tasks.Task.load_list({'description <>': ''}, done=0)
        self.task_list.set_task_list(task_list)
        self.todo_task.load_todo_from_db()
        
        for schdedule in ScheduledTask.query_db():
            new_task = schdedule.get_task_for_date(today)
            if isinstance(new_task, tasks.Todo):
                self.todo_task.add_todo(new_task)
            elif isinstance(new_task, tasks.Task):
                self.task_list.add(new_task)
