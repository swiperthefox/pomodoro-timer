from datetime import datetime, date, timedelta
from enum import IntEnum

class Weekdays(IntEnum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6
    
def format_date(d):
    if d == 0:
        return ''
    date = datetime.fromtimestamp(d)
    today = datetime.today().toordinal()
    diff = date.toordinal() - today
    if diff < 0:
        return "past"
    elif diff == 0:
        return "today"
    elif diff == 1:
        return "tomorrow"
    elif diff < 7:
        return f"in {diff} days"
    else:
        return date.strftime("%m-%d")

def parse_date(s):
    return 0
    
def parse_date_complex(s, base=date.today()):
    return 15

def lastest_valid_date_before(year, month, day) -> datetime:
    month = min(12, max(1, month))
    while True:
        try:
            return datetime(year, month, day, 1, 0, 0)
        except ValueError:
            day -= 1
            
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
        
    def next_occurrance_after(self, start):
        """Return the next occurrance of a day that matches the pattern and no before than the day `start`.
        """
        year, month, day, weekday = start.year, start.month, start.day, start.weekday()
        cycle_type = self.get_type()
        if cycle_type is None:
            return None
        elif cycle_type == 'o':
            the_day = lastest_valid_date_before(self.year, self.month, self.day)
            print('the day is', the_day, start)
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