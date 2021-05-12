import re
from datetime import datetime, date, timedelta

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