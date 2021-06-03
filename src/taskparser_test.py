from model.scheduledtask import ScheduledTask
import unittest
from datetime import date, datetime

from taskparser import FIRST_DAY, parse_repeat_pattern, parse_date_spec, parse_task_description

class TaskDescriptionParserTest(unittest.TestCase):
    def test_task_parser(self):
        today = datetime(2021, 5, 29)
        task = "Task title. #3 @Mon *m =. ^parent title^"
        options = parse_task_description(task)
        self.assertEqual(options['title'], 'Task title', 'capture task title')
        self.assertEqual(options['tomato'], 3, 'capture tomato')
        self.assertEqual(options['pattern'], '*m', 'capture repeat pattern')
        self.assertEqual(options['once'], '@Mon', 'capture schedule date')
        self.assertEqual(options['parent'], 'parent title', 'capture parent')
        self.assertEqual(options['type'], ScheduledTask.TODO, 'capture the task type')
        
class RepeatPatternParserTest(unittest.TestCase):
    def test_repeat_pattern_parser(self):
        today = date(2021, 5, 29)
        cases = [
            ['*w', [-1, -1, -1, 5], 'weekly task on Sat. (implicit start)'],
            ['*m', [-1, -1, 29, -1], 'monthly task on 29th (implicit start)'],
            ['*y', [-1, 5, 29, -1], 'yearly on 5/29 (implicit start)'],
            ['*Mon', [-1, -1, -1, 0], 'weekly task on Mon. (explicit start)'],
            ['*m12', [-1, -1, 12, -1], 'monthly task on 12th (explicit start)'],
            ['*12', [-1, -1, 12, -1], 'monthly task (explicit start, omitting m)'],
            ['*y4-19', [-1,4,19,-1], 'yearly task (explicit start)'],
            ['*4-19', [-1, 4, 19, -1], 'yearly task (explicit start, omitting y)'],
            ['*invalid', [], 'invalid input']
        ]
        for pattern, expected, msg in cases:
            result = parse_repeat_pattern(pattern, today)
            self.assertEqual(result, expected, msg)
        
class DateParserTest(unittest.TestCase):
   def test_date_spec_parser(self):
        today = datetime(2021, 5, 29)
        cases = [
            ['@+2', date(2021,5,31), 'offset in days'],
            ['@+3', date(2021, 6, 1), 'offset in days, cross month'],
            ['@+2d', date(2021, 5, 31), 'optional d surffix for day offsets'],
            ['@+1w', date(2021, 6, 5), 'offset in weeks'],
            ['@+1m', date(2021, 6, 29), 'offset in monthes'],
            ['@+9m', date(2022, 2, 28), 'offset in monthes (advance the date if invalid)'],
            ['@+2y', date(2023, 5, 29), 'offset in years'],
            ['@30', date(2021, 5, 30), 'next given day (in current month)'],
            ['@15', date(2021, 6, 15), 'next given day (in next month)'],
            ['@32', date(2021, 5, 31), 'next given day (advance the date if invalid)'],
            ['@6-15', date(2021, 6, 15), 'next given mm/dd (in current year)'],
            ['@4-15', date(2022, 4,15), 'next given mm/dd (in next year)'],
            ['@5-32', date(2021, 5, 31), 'next given mm/dd (advance the date if invalid)'],
            ['@5-15-2021', FIRST_DAY.date(), 'date has passed'],
            ['@Mon', date(2021, 5, 31), 'next given day of week']
        ]
        for day, expected, msg in cases:
            result = parse_date_spec(day, today)
            if result is not None:
                result = result.date()
            self.assertEqual(result, expected, msg) 