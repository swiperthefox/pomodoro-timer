from datetime import date, datetime, timedelta
import re

from utils import lastest_valid_date_before, weekday_dict
from model.scheduledtask import ScheduledTask

def parse_task_description(task_description, today):
    """Parse the extended task description, return a dict of the options.
    
    A task can be specified in an "extended task description" format. The format is as follows:
    
    task_title #n [optional fields]
    
    where `task_title` is the description of the task and `n` is the number of session assigned.
    
    The optional fields are some fields that starts with some special characters. The fields could
    appear in any order.
    
    - @show_time: When to list the task in the task list. Multiple show times will be combined.
    
    Possible format: 
    1. @04-15: show at the given date. If the date is not valid, use the latest day that is prior
    to the given date (for example: @4-32 will be transferred to the last day of April.)
    2. @Mon (Tue, Wed, Thu, Fri, Sat, Sun): show at the upcoming given day of week.
    3. @+10, @+2w, @+1m: a day relative to today.
    
    - *repeat_pattern: Repeatedly show the task in the given pattern.
    
    Possible format:
    1. *w, *m, *y: repeat every week, month or year, start from today.
    2. *Mon, *m12, *y04-13: these formats combine the show time with repeat time (Monday on every week,
    on 12th every month, or April 13 every year.). If there are also @fields, all the show times will be
    combined.
    
    - =duration: The duration type of session. Default is short session.
    
    Possible format:
    "==" for long session, "=-" for short session and "=." for todos.
    
    - ^parent_title^: specifies the parent task. The first task in current list that matches the given
    `parent_title` will be the parent of this task. Repeated tasks can't have parent task, if `*` field
    is given, this field will be ignored.
    """
    # options are substrings that do not contain spaces, begins with one of the 
    # "@#*="
    single_word_option = r'[@#*=][\S]+'
    #  or the substring that surrounded by "^". 
    multi_word_option = r'\^[^^]+\^'
    
    # title is any substring that starts from beginning and does not contain the 
    # special chars
    title_pat = '^[^^@*=#]+'
    
    pattern = f'{single_word_option}|{multi_word_option}|{title_pat}'
    parts = re.findall(pattern, task_description)
    
    options = {}
    for part in parts:
        name = part[0]
        option_body = part[1:]
        if name == '@':
            options['once'] = part
        elif name == '*':
            options['pattern'] = part
        elif name == '#':
            options['tomato'] = min(5, max(int(option_body), 1))
        elif name == '=':
            # task_type = {'=': ScheduledTask.LONG, '-': ScheduledTask.SHORT, '.': ScheduledTask.TODO}[option_body]
            options['type'] = option_body
        elif name == '^':
            options['parent'] = part[1:-1].lower()
        else:
            options['title'] = part.strip()
    return options

def parse_repeat_pattern(pattern, start: date):
    """Parse pattern into a tuple of four integers (y, m, d, w)."""
    if start is None: start = datetime.today()
    
    if pattern == '*w':
        return [-1, -1, -1, start.weekday()]
    elif pattern == '*m':
        return [-1, -1, start.day, -1]
    elif pattern == '*y':
        return [-1, start.month, start.day, -1]
    else:
        # *Mon
        weekday_name = pattern[1:4].lower()
        if weekday_name in weekday_dict:
            return [-1, -1, -1, weekday_dict[weekday_name]]
        
        # *m12, *12
        monthly_pat = r'^\*m?([0-9]+)$'
        m = re.match(monthly_pat, pattern)
        if m:
            day = int(m.group(1))
            if 1 <= day <= 31:
                return [-1, -1, day, -1]
            else:
                return []
        
        # *y4-15, *4-15
        yearly_pat = r'^\*y?([0-9]+).([0-9]+)$'
        m = re.match(yearly_pat, pattern)
        if m:
            month = int(m.group(1))
            day = int(m.group(2))
            if 1 <= month <= 12 and 1 <= day <= 31:
                return [-1, int(m.group(1)), int(m.group(2)), -1]
            else:
                return []
        
        return []

# FIRST_DAY is the `first day`, way back in the past. it serves as None
# since we are dealing future events here.
FIRST_DAY = datetime.fromordinal(1)

def parse_date_spec(pattern, start: datetime=None) -> datetime:
    """Parse date specs described in `parse_task_description`.
    
    Return a date, or the `FIRST_DAY` if the pattern is not well formed. 
    """
    if start is None: start = datetime.today()
    if pattern and pattern[0] == '@': pattern = pattern[1:]
    
    # for patterns that specify an offset
    offset_pat = r'^\+(?P<offset>[0-9]+)(?P<unit>[dwmy])?$'
    # for patterns that specify a day (optionally with a month and a year)
    date_pat = r'^(?:(?P<month>[0-9]+).)?(?P<day>[0-9]+)(?:.(?P<year>[0-9]+))?$'
    # for patterns that specify a day of week
    week_day_pat = r'^(?P<weekday>[a-zA-Z]+)$'
    
    all_pat = f'{offset_pat}|{date_pat}|{week_day_pat}'
    m = re.match(all_pat, pattern)
    
    if not m:
        return FIRST_DAY
    else:
        matched_parts = m.groupdict()
        if matched_parts['offset']: # offset format
            unit = matched_parts['unit'] or 'd'
            quantity = int(matched_parts['offset'])
            if unit == 'w':
                unit = 'd'
                quantity *= 7
            
            if unit == 'd':
                return (start + timedelta(days=quantity))
            elif unit == 'm':
                month = start.month + quantity
                year = start.year + (month-1) // 12 # month is 1 based
                month = (month - 1) % 12 + 1
                return lastest_valid_date_before(year, month, start.day)    
            else:
                return lastest_valid_date_before(
                    start.year + quantity, start.month, start.day)
        elif matched_parts['weekday']:
            target_dow = weekday_dict[matched_parts['weekday'].lower()]
            return start + timedelta((target_dow - start.weekday())%7)
        else: # date format
            y, m, d = [matched_parts[name] for name in ['year', 'month', 'day']]
            year = start.year if y is None else int(y)
            month = start.month if m is None else int(m)
            day = int(d)
            
            if y is not None:
                # the date is fully specified, only adjust the year if needed
                if year < 100:
                    year += 2000
            elif m is not None:
                # only the month and day are given, if it's too late for this year,
                # schedule it for next year
                if month < 1 or month > 12:
                    return FIRST_DAY
                if month < start.month or (m == start.month and day < start.day):
                    year += 1
            else:
                # only the day is given. If it's too late for this month,
                # schedule it for next month.
                if day < start.day:
                    month += 1
                    if month > 12:
                        year += 1
                        month -= 12
                
            the_day = lastest_valid_date_before(year, month, day)
                
            return FIRST_DAY if the_day < start else the_day
            
                        
   