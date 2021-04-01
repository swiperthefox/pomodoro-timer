import unittest
import tasks

class TestTaskPersistence(unittest.TestCase):
    def test_save_tasks(self):
        taskList = [
            tasks.Task("create a test", False, 1, 1)
        ]
        tasks.save_task_list(taskList)
        self.assertEqual(taskList, tasks.load_task_list())

