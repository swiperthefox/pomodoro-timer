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

weekday_dict = dict((v, i) for i, v in enumerate(
    ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
))

def format_date(d):
    if d == 0:
        return ''
    today = datetime.today().toordinal()
    diff = d - today
    if diff < 0:
        return "past"
    elif diff == 0:
        return "today"
    elif diff == 1:
        return "tomorrow"
    elif diff < 7:
        return f"in {diff} days"
    else:
        day = date.fromordinal(d)
        return day.strftime("%m-%d")

def parse_date(s):
    return 0
    

def lastest_valid_date_before(year, month, day):
    month = max(1, min(month, 12))
    while True:
        try:
            return datetime(year, month, day, 1, 0, 0)
        except ValueError:
            day -= 1
            
