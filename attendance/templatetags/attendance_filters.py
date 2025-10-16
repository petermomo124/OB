from django import template
from datetime import datetime, date

register = template.Library()

@register.filter
def get_attendance_status(percentage):
    """
    Returns a Bootstrap color class based on attendance percentage
    """
    if percentage is None:
        return 'secondary'
    
    percentage = float(percentage)
    if percentage >= 80:
        return 'success'
    elif percentage >= 60:
        return 'info'
    elif percentage >= 40:
        return 'warning'
    else:
        return 'danger'

@register.filter
def days_between(start_date, end_date):
    """
    Calculate the number of days between two dates, inclusive.
    """
    if not all([start_date, end_date]):
        return 0
    if isinstance(start_date, datetime):
        start_date = start_date.date()
    if isinstance(end_date, datetime):
        end_date = end_date.date()
    delta = end_date - start_date
    return delta.days + 1  # +1 to include both start and end dates

@register.filter
def get_item(dictionary, key):
    """
    Template filter to get a dictionary value by key.
    Usage: {{ my_dict|get_item:key }}
    """
    if not dictionary:
        return None
    return dictionary.get(key)
