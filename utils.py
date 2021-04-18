from datetime import datetime

def format_date(d):
    if d == 0:
        return ''
    date = datetime.fromtimestamp(d)
    today = datetime.today().toordinal()
    diff = date.toordinal() - today
    if diff < 0:
        return "dued"
    elif diff == 0:
        return "today"
    elif diff < 7:
        return "in a week"
    else:
        return date.strftime("%m-%d")

def parse_date(s):
    return 0