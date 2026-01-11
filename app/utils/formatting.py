from datetime import datetime, date, time

def parse_date(date_str: str) -> date:
    """Parses date string in DD.MM.YYYY format."""
    return datetime.strptime(date_str, "%d.%m.%Y").date()

def parse_time(time_str: str) -> time:
    """Parses time string in HH:MM format."""
    return datetime.strptime(time_str, "%H:%M").time()

def format_date(d: date) -> str:
    return d.strftime("%d.%m.%Y")

def format_time(t: time) -> str:
    return t.strftime("%H:%M")
