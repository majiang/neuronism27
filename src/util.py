from datetime import date, timedelta

min_date = date.min
max_date = date.max

def today():
    return date.today()

def firstday(year, month):
    return date(year=year, month=month, day=1)

def yesterday(today):
    return today - timedelta(days=1)

def tomorrow(today):
    return today + timedelta(days=1)

long_ago = date(year=2001, month=1, day=1)
