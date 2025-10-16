from datetime import timedelta, date
from django.utils import timezone

def calculate_working_hours(check_in, check_out):
    """Calculate working hours between check-in and check-out times."""
    if not check_in or not check_out:
        return 0
    
    # Ensure both are timezone-aware
    if timezone.is_naive(check_in):
        check_in = timezone.make_aware(check_in)
    if timezone.is_naive(check_out):
        check_out = timezone.make_aware(check_out)
    
    # Calculate difference in hours
    delta = check_out - check_in
    return round(delta.total_seconds() / 3600, 2)  # Convert seconds to hours

def get_holidays_between_dates(start_date, end_date):
    """Get all holidays between two dates."""
    from .models import Holiday
    
    return Holiday.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    )

def get_leave_days(start_date, end_date):
    """Calculate number of leave days between two dates (inclusive)."""
    if not start_date or not end_date:
        return 0
    
    # Ensure we have date objects
    if hasattr(start_date, 'date'):
        start_date = start_date.date()
    if hasattr(end_date, 'date'):
        end_date = end_date.date()
    
    # Calculate total days (inclusive)
    delta = end_date - start_date
    total_days = delta.days + 1  # +1 to include both start and end dates
    
    # Get all holidays in the date range
    holidays = get_holidays_between_dates(start_date, end_date)
    holiday_dates = [h.date for h in holidays]
    
    # Count working days (Monday=0, Sunday=6)
    working_days = 0
    for day in range(total_days):
        current_date = start_date + timedelta(days=day)
        # Count only weekdays (0-4 = Monday-Friday)
        if current_date.weekday() < 5:  # 0=Monday, 6=Sunday
            if current_date not in holiday_dates:
                working_days += 1
    
    return working_days

def get_weekend_dates(start_date, end_date):
    """Get all weekend dates between two dates."""
    if not start_date or not end_date:
        return []
    
    # Ensure we have date objects
    if hasattr(start_date, 'date'):
        start_date = start_date.date()
    if hasattr(end_date, 'date'):
        end_date = end_date.date()
    
    # Calculate total days (inclusive)
    delta = end_date - start_date
    total_days = delta.days + 1  # +1 to include both start and end dates
    
    # Get all weekend dates
    weekend_dates = []
    for day in range(total_days):
        current_date = start_date + timedelta(days=day)
        if current_date.weekday() >= 5:  # 5=Saturday, 6=Sunday
            weekend_dates.append(current_date)
    
    return weekend_dates

def is_weekend(date_obj):
    """Check if a given date is a weekend (Saturday or Sunday)."""
    if hasattr(date_obj, 'date'):
        date_obj = date_obj.date()
    return date_obj.weekday() >= 5  # 5=Saturday, 6=Sunday
