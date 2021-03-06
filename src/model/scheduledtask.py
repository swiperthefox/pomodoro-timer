from dataclasses import dataclass
from datetime import datetime, timedelta, date

from .noorm import Model
from dateutils import lastest_valid_date_before
from model import models 

@dataclass
class ScheduledTask(Model):
    """A ScheduledTask is a task template to generate a task on a certain day
    (repeatedly or not).

    Other than the information of the desired task, it keeps the following data
    for event schedule:

    once: a single day on which the task will be generated. It stores the
    ordinal of that day.

    pattern: a repeat pattern for repeatedly occurred task. It's a string of 4
    comma seprated ints. (see PeriodicScheduler for more detail of the format.) 

    next_event: it's just a cache that saves the calculated next event, so that
    before the next_event happends, the schedular will not be called again.

    last_gen: the day on which this task is examined, to prevent from generating
    the same task multiple times in one day.
    """
    _table_name = "repeated_task"
    _fields = {
        'id': int,
        # info for when to generate
        'once': int,    
        'pattern': str, 
        'next_event': int,
        'last_gen': int,
        'done': bool,
        # info for new task
        'title': str,
        'tomato': int,
        'type': str
    }
    LONG = '='
    SHORT = '-'
    TODO = '.'
    
    def get_task_for_date(self, day_ordinal):
        "Get the (possibly) new task for `today`."
        
        # check if we have tried for today
        if self.last_gen >= day_ordinal:
            return None
            
        # A ScheduledTask may generate a new task for one of two reasons:
        # 1. the onetime schedule applies
        onetime_applies = self.once == day_ordinal
        
        # 2. the "repeat" setting applies
        if self.next_event >= day_ordinal: # the cache is still valid
            next_event = self.next_event
        else:
            scheduler = PeriodicScheduler.from_string(self.pattern)
            next_event = scheduler.next_occurrance_after(day_ordinal)
        repeat_pattern_applies = next_event == day_ordinal

        should_schedule = onetime_applies or repeat_pattern_applies
        result = self.make_task() if should_schedule else None
        
        # bookkeeping
        changed_fields = ['last_gen']
        self.last_gen = day_ordinal
        
        has_future_event = next_event >= day_ordinal
        has_one_time_schedule = self.once > day_ordinal
        if not (has_one_time_schedule or has_future_event):
            self.done = True
            changed_fields.append('done')
        elif has_future_event and next_event != self.next_event:
            self.next_event = next_event
            changed_fields.append('next_event')
        else:
            pass
        self.save_to_db(changed_fields)
        return result
    
    def make_task(self):
        if self.type == self.TODO:
            return models.Todo.create(description=self.title)
        else:
            return models.Task.create(
                description=self.title,
                tomato=int(self.tomato),
                long_session=self.type == self.LONG
            )
    def __type_hint(self):
        """this method is never used, it just provide the type info of the generated fields."""
        self.title = ''
        self.tomato = 0
        self.type = ''
        self.once = 1
        self.pattern =''
        
class PeriodicScheduler:
    """Specify a repeat pattern of days.
    
    The pattern is described with four fields: year, month, day, week. Each field can be appropriate
    number for that field or -1 for unspecified.
    """
    def __init__(self, year = -1, month = -1, day = -1, weekday = -1):
        self.year = year
        self.month = month
        self.day = day
        self.weekday = weekday
        
    def next_occurrance_after(self, start_ordianl):
        """Return the next occurrance of a day that matches the pattern and no before than the day `start`.
        """
        start = date.fromordinal(start_ordianl)
        year, month, day, weekday = start.year, start.month, start.day, start.weekday()
        cycle_type = self.get_type()
        if cycle_type is None:
            return None
        elif cycle_type == 'o':
            the_day = lastest_valid_date_before(self.year, self.month, self.day)
            if the_day.date() >= start:
                return the_day
            else:
                return None # too late, we missed the day
        elif cycle_type == 'y':
            if month > self.month or (month == self.month and day > self.day): # too late for this year
                year += 1
            return lastest_valid_date_before(year, self.month, self.day)
        elif cycle_type == 'm':
            if day > self.day: # too late for this month
                month += 1
                if month == 13:
                    year += 1
                    month = 1
            return lastest_valid_date_before(year, month, self.day)
        elif cycle_type == 'w':
            delta = (self.weekday - weekday) % 7
            the_day = start + timedelta(delta)
            return datetime(the_day.year, the_day.month, the_day.day, 1, 0, 0)
        else:
            return None # should not happen
            
    def should_schedule(self, day):
        return self.next_occurrance_after(day) == day
            
    def get_type(self):
        #          y    m   d   w 
        # weekly:  -1   -1  -1  1 
        # once:    2021 4   15  -1
        # yearly:  -1   4   15  -1
        # monthly: -1   -1  15  -1
        if self.weekday != -1:
            return 'w'
        elif self.year != -1:
            return 'o'
        elif self.month != -1:
            return 'y'
        elif self.day != -1:
            return 'm'
        else:
            return None
            
    def __str__(self):
        return f'{self.year} {self.month} {self.day} {self.weekday}'
    
    @classmethod
    def from_string(cls, s):
        pattern = [int(v) for v in s.split()]
        if len(pattern) != 4:
            pattern = [-1]*4
        return cls(*pattern)
