from django.urls import reverse
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest, HttpResponseNotAllowed
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.db.models import Q, Count, F, Case, When, Value, IntegerField
from django.db.models.functions import ExtractWeekDay, ExtractHour, Coalesce
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.timezone import localdate, make_aware, is_naive, get_current_timezone
from datetime import datetime, timedelta, time as dt_time, date
import calendar
import logging
import json
import pytz

from core.models import User, Office  # Removed Department, LeaveType, CompanyPolicy as they don't exist
from .models import (
    Attendance, 
    LeaveRequest,
    Holiday
)
from .forms import LeaveRequestForm  # Only import forms that exist
from .utils import (calculate_working_hours, get_holidays_between_dates,
                   get_leave_days, get_weekend_dates, is_weekend)
from .templatetags.attendance_filters import get_item

# Create logger instance
logger = logging.getLogger(__name__)

@login_required
def dashboard(request):
    """Main dashboard view for the attendance app."""
    try:
        # Get today's attendance for the current user
        today = timezone.now().date()
        today_attendance = Attendance.objects.filter(
            user=request.user,
            timestamp__date=today
        ).order_by('timestamp')
        
        # Get recent attendance history
        recent_attendance = Attendance.objects.filter(
            user=request.user
        ).order_by('-timestamp')[:5]
        
        # Get pending leave requests
        pending_requests = LeaveRequest.objects.filter(
            user=request.user,
            status='pending'
        ).order_by('-created_at')
        
        # Get upcoming holidays
        upcoming_holidays = Holiday.objects.filter(
            date__gte=today
        ).order_by('date')[:3]
        
        # Get today's attendance status
        has_checked_in = today_attendance.filter(attendance_type='check_in').exists()
        has_checked_out = today_attendance.filter(attendance_type='check_out').exists()
        
        context = {
            'today_attendance': today_attendance,
            'recent_attendance': recent_attendance,
            'pending_requests': pending_requests,
            'upcoming_holidays': upcoming_holidays,
            'has_checked_in': has_checked_in,
            'has_checked_out': has_checked_out,
            'today': today,
        }
        
        return render(request, 'attendance/dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Error in dashboard view: {str(e)}")
        messages.error(request, "An error occurred while loading the dashboard.")
        return render(request, 'attendance/dashboard.html', {})

def get_todays_attendance(user):
    """Helper function to get today's attendance for a user"""
    today = timezone.now().date()
    today_attendance = Attendance.objects.filter(
        user=user,
        timestamp__date=today
    ).order_by('timestamp')
    
    # Check if user is currently checked in
    last_check_in = today_attendance.filter(attendance_type='check_in').last()
    last_check_out = today_attendance.filter(attendance_type='check_out').last()
    
    # Determine current status and clock in/out state
    current_status = "Checked In" if last_check_in and (not last_check_out or last_check_in.timestamp > last_check_out.timestamp) else "Checked Out"
    can_clock_in = not (current_status == "Checked In")
    
    # Calculate today's working hours
    today_hours = "0:00"
    if last_check_in and last_check_out and last_check_out.timestamp > last_check_in.timestamp:
        duration = last_check_out.timestamp - last_check_in.timestamp
        hours, remainder = divmod(duration.seconds, 3600)
        minutes = remainder // 60
        today_hours = f"{hours}:{minutes:02d}"
    
    return {
        'today_attendance': today_attendance,
        'last_check_in': last_check_in,
        'last_check_out': last_check_out,
        'current_status': current_status,
        'can_clock_in': can_clock_in,
        'today_hours': today_hours
    }

def get_dashboard_context(request):
    """Helper function to get dashboard context"""
    try:
        # Get today's attendance for the user
        attendance_data = get_todays_attendance(request.user)
        today = timezone.now().date()
        
        # Get present staff count
        present_today = Attendance.objects.filter(
            timestamp__date=today,
            attendance_type='check_in'
        ).values('user').distinct().count()
        
        # Get pending leave requests
        pending_requests = LeaveRequest.objects.filter(
            user=request.user,
            status='pending'
        ).order_by('-created_at')
        
        # Get recent activity (last 5 records)
        recent_activity = Attendance.objects.filter(
            user=request.user
        ).order_by('-timestamp')[:5]
        
        # Get upcoming holidays (next 30 days)
        upcoming_holidays = Holiday.objects.filter(
            date__gte=today
        ).order_by('date')[:5]
        
        # Get total staff count
        total_staff = User.objects.filter(is_staff=True).count()
        
        context = {
            **attendance_data,
            'total_staff': total_staff,
            'present_today': present_today,
            'pending_requests': pending_requests,
            'recent_activity': recent_activity,
            'upcoming_holidays': upcoming_holidays,
            'today': today,
        }
        return context
        
    except Exception as e:
        logger.error(f"Error in get_dashboard_context: {str(e)}")
        return {
            'today_attendance': Attendance.objects.none(),
            'pending_requests': LeaveRequest.objects.none(),
            'recent_activity': Attendance.objects.none(),
            'upcoming_holidays': Holiday.objects.none(),
            'today': timezone.now().date(),
            'total_staff': 0,
            'present_today': 0,
        }

@login_required
def clock_in_out(request):
    """Handle clock in/out actions"""
    if request.method == 'POST':
        now = timezone.now()
        today = now.date()
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')
        
        try:
            # Get all of today's attendance records for this user - check both date fields
            today_attendances = Attendance.objects.filter(
                Q(user=request.user) & 
                (Q(date=today) | Q(timestamp__date=today))
            ).order_by('timestamp')
            
            # Get the most recent attendance record
            last_attendance = today_attendances.last()
            
            # Debug information
            print(f"Found {today_attendances.count()} attendance records for today")
            if last_attendance:
                print(f"Last attendance: {last_attendance.attendance_type} at {last_attendance.timestamp}")
            
            # Determine if user is checking in or out
            if last_attendance and last_attendance.attendance_type == 'check_in':
                # User is checking out
                # Check if they've already checked out today
                if today_attendances.filter(attendance_type='check_out').exists():
                    messages.warning(request, 'You have already checked out for today.')
                    return redirect('attendance:dashboard')
                
                # Create check-out record
                Attendance.objects.create(
                    user=request.user,
                    date=today,  # Use the date object directly
                    attendance_type='check_out',
                    ip_address=ip_address,
                    notes=f'Checked out at {now.strftime("%I:%M %p")} via web interface',
                    location=request.META.get('HTTP_CF_IPCOUNTRY', 'Unknown'),
                    status='auto',
                    recorded_by=request.user
                )
                messages.success(request, 'Successfully checked out!')
                print(f"Created check-out record for user {request.user.id}")
                
            else:
                # User is checking in
                # Check if they've already checked in today
                if today_attendances.filter(attendance_type='check_in').exists():
                    messages.warning(request, 'You have already checked in today.')
                    return redirect('attendance:dashboard')
                
                # Create check-in record
                Attendance.objects.create(
                    user=request.user,
                    date=today,  # Use the date object directly
                    attendance_type='check_in',
                    ip_address=ip_address,
                    notes=f'Checked in at {now.strftime("%I:%M %p")} via web interface',
                    location=request.META.get('HTTP_CF_IPCOUNTRY', 'Unknown'),
                    status='auto',
                    recorded_by=request.user
                )
                messages.success(request, 'Successfully checked in!')
                print(f"Created check-in record for user {request.user.id}")
            
            return redirect('attendance:dashboard')
            
        except Exception as e:
            print(f"Error in clock_in_out view: {str(e)}")
            messages.error(request, 'An error occurred while processing your request. Please try again.')
            return redirect('attendance:dashboard')
    
    return redirect('attendance:dashboard')

@login_required
def request_leave(request):
    """Handle leave requests with validation for overlapping dates"""
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST, user=request.user)
        print("Form data:", request.POST)  # Debug log
        print("Form is valid:", form.is_valid())  # Debug log
        
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.user = request.user
            
            # Debug log
            print(f"Processing leave request from {leave_request.start_date} to {leave_request.end_date}")
            
            # Check for overlapping leave requests
            overlapping_requests = LeaveRequest.objects.filter(
                user=request.user,
                status__in=['pending', 'approved'],
                start_date__lte=leave_request.end_date,
                end_date__gte=leave_request.start_date
            )
            
            if overlapping_requests.exists():
                error_msg = 'You already have a leave request that overlaps with these dates.'
                print(f"Overlap found: {overlapping_requests}")  # Debug log
                messages.error(request, error_msg)
            else:
                try:
                    leave_request.save()
                    messages.success(request, 'Leave request submitted successfully!')
                    print("Leave request saved successfully")  # Debug log
                    return redirect('attendance:dashboard')
                except Exception as e:
                    print(f"Error saving leave request: {str(e)}")  # Debug log
                    messages.error(request, f'Error saving leave request: {str(e)}')
        else:
            # Log form errors for debugging
            print("Form errors:", form.errors)
            
            # Handle non-field errors (__all__)
            if '__all__' in form.errors:
                for error in form.errors['__all__']:
                    messages.error(request, error)
            
            # Handle field-specific errors
            for field in form.errors:
                if field != '__all__':  # Skip __all__ as we've already handled it
                    for error in form.errors[field]:
                        if field in form.fields:
                            messages.error(request, f"{form.fields[field].label}: {error}")
                        else:
                            messages.error(request, f"Error in form: {error}")
    else:
        form = LeaveRequestForm(user=request.user)
    
    # Get user's leave history for reference
    leave_history = LeaveRequest.objects.filter(
        user=request.user
    ).order_by('-start_date')[:5]  # Show last 5 leave requests
    
    return render(request, 'attendance/request_leave.html', {
        'form': form,
        'leave_history': leave_history
    })

@login_required
def my_leave_requests(request):
    """View all leave requests for the current user"""
    try:
        # Debug: Print user info
        print(f"User: {request.user}, ID: {request.user.id}")
        
        # Get leave requests with error handling
        leave_requests = LeaveRequest.objects.filter(
            user=request.user
        ).select_related('reviewed_by').order_by('-created_at')
        
        # Debug: Print count of leave requests and their statuses
        total_requests = leave_requests.count()
        print(f"Found {total_requests} leave requests")
        
        # Create a more reliable status count
        status_count = {
            'pending': 0,
            'approved': 0,
            'rejected': 0,
            'cancelled': 0
        }
        
        for req in leave_requests:
            print(f"- ID: {req.id}, Status: {req.status}, Type: {req.leave_type}, Dates: {req.start_date} to {req.end_date}")
            if req.status in status_count:
                status_count[req.status] += 1
        
        # Convert to list of dicts for template
        status_counts = [{'status': k, 'count': v} for k, v in status_count.items() if v > 0]
        print(f"Status counts: {status_counts}")
        
        context = {
            'leave_requests': leave_requests,
            'status_counts': status_counts,
            'debug': settings.DEBUG,
            'has_pending_requests': status_count['pending'] > 0
        }
        
        return render(request, 'attendance/my_leave_requests.html', context)
        
    except Exception as e:
        # Log the full error for debugging
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in my_leave_requests: {str(e)}\n{error_trace}")
        
        # Return a 500 response with error details in development
        if settings.DEBUG:
            return HttpResponse(f"<h1>Error</h1><pre>{str(e)}\n\n{error_trace}</pre>", status=500)
        # In production, show a user-friendly error page
        return render(request, '500.html', status=500)

import logging
logger = logging.getLogger(__name__)

@login_required
def view_leave_request(request, pk):
    """View details of a specific leave request"""
    logger.debug(f"View leave request {pk} - User: {request.user}")
    
    try:
        leave_request = LeaveRequest.objects.get(pk=pk)
        logger.debug(f"Found leave request: {leave_request}")
    except LeaveRequest.DoesNotExist:
        logger.error(f"Leave request {pk} not found")
        return HttpResponseNotFound("Leave request not found")
    
    # Ensure the user can only view their own requests unless they're an admin
    if leave_request.user != request.user and not request.user.is_staff:
        logger.warning(f"Permission denied for user {request.user} to view leave request {pk}")
        return HttpResponseForbidden("You don't have permission to view this request.")
    
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    logger.debug(f"Is AJAX request: {is_ajax}")
    
    context = {'leave_request': leave_request}
    
    if is_ajax:
        logger.debug("Returning modal content template")
        return render(request, 'attendance/partials/leave_request_modal_content.html', context)
    
    # Full page view (fallback for non-AJAX requests)
    logger.debug("Returning full page template")
    return render(request, 'attendance/view_leave_request.html', context)

@login_required
def update_leave_request(request, pk):
    """Update a leave request (only for pending requests)"""
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    
    # Ensure the user can only update their own pending requests
    if leave_request.user != request.user or leave_request.status != 'pending':
        return JsonResponse({'success': False, 'error': 'You can only update your own pending leave requests.'}, status=403)
    
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST, instance=leave_request)
        if form.is_valid():
            updated_request = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Leave request updated successfully.'
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

@login_required
def delete_all_leave_requests(request):
    """
    Delete all leave requests for the current user.
    Handles both AJAX and non-AJAX requests.
    """
    # Only accept POST requests for security
    if request.method != 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(
                {'success': False, 'message': 'Method not allowed'}, 
                status=405
            )
        return HttpResponseNotAllowed(['POST'])
    
    # Get all leave requests for the current user
    user_leave_requests = LeaveRequest.objects.filter(user=request.user)
    count = user_leave_requests.count()
    
    if count == 0:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(
                {'success': False, 'message': 'No leave requests found to delete'}, 
                status=404
            )
        messages.info(request, 'No leave requests found to delete.')
        return redirect('attendance:my_leave_requests')
    
    try:
        # Delete all leave requests
        deleted_count, _ = user_leave_requests.delete()
        
        # Log the deletion
        logger.info(
            f"User {request.user.email} deleted all ({deleted_count}) of their leave requests"
        )
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Successfully deleted {deleted_count} leave request(s)',
                'deleted_count': deleted_count
            })
            
        messages.success(request, f'Successfully deleted {deleted_count} leave request(s)')
        return redirect('attendance:my_leave_requests')
        
    except Exception as e:
        # Log the error
        logger.error(f"Error deleting all leave requests for user {request.user.email}: {str(e)}", 
                    exc_info=True)
        
        error_message = 'An error occurred while deleting leave requests. Please try again.'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(
                {'success': False, 'message': error_message}, 
                status=500
            )
            
        messages.error(request, error_message)
        return redirect('attendance:my_leave_requests')


@login_required
def cancel_leave_request(request, pk):
    """
    Allow users to delete their own leave requests, and staff/admins to delete any request.
    Handles both AJAX and non-AJAX requests.
    """
    print(f"=== CANCEL_LEAVE_REQUEST DEBUG ===")
    print(f"User: {request.user.email}")
    print(f"User role: {getattr(request.user, 'role', 'NO ROLE ATTRIBUTE')}")

    # Accept POST, DELETE, and GET (for non-JS fallback)
    if request.method not in ['POST', 'DELETE', 'GET']:
        return JsonResponse(
            {'success': False, 'message': 'Method not allowed'},
            status=405
        )

    try:
        # SIMPLIFIED DATABASE QUERY - Remove select_related to reduce query complexity
        leave_request = LeaveRequest.objects.get(pk=pk)
        print(f"Leave request found - Owner: {leave_request.user.email}")

    except LeaveRequest.DoesNotExist:
        print("Leave request not found")
        return JsonResponse(
            {'success': False, 'message': 'Leave request not found.'},
            status=404
        )
    except OperationalError as e:
        print(f"Database connection error: {e}")
        return JsonResponse(
            {'success': False, 'message': 'Database connection issue. Please try again.'},
            status=503
        )

    # Check permissions - THIS IS WORKING CORRECTLY!
    user_can_delete = (
            request.user.is_superuser or
            getattr(request.user, 'role', None) == 'admin' or
            getattr(request.user, 'role', None) == 'staff' or
            leave_request.user == request.user
    )

    print(f"User can delete: {user_can_delete}")

    if not user_can_delete:
        print("PERMISSION DENIED")
        return JsonResponse(
            {'success': False, 'message': 'You do not have permission to delete this request.'},
            status=403
        )

    # Handle the deletion
    try:
        # Store request details for the success message
        request_details = (
            f"{leave_request.leave_type} request from "
            f"{leave_request.start_date.strftime('%b %d, %Y')} to "
            f"{leave_request.end_date.strftime('%b %d, %Y')} ({leave_request.status})"
        )

        print(f"Deleting leave request: {request_details}")

        # Delete the leave request
        leave_request.delete()

        print("SUCCESS: Leave request deleted")

        # Return success response
        response_data = {
            'success': True,
            'message': 'Leave request deleted successfully',
            'request_details': request_details,
            'redirect_url': reverse('attendance:my_leave_requests')
        }

        # For AJAX requests, return JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(response_data)

        # For non-AJAX requests, use messages and redirect
        messages.success(request, response_data['message'])
        return redirect('attendance:my_leave_requests')

    except Exception as e:
        print(f"ERROR during deletion: {str(e)}")
        error_message = 'An error occurred while deleting the leave request.'

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(
                {'success': False, 'message': error_message},
                status=500
            )

        messages.error(request, error_message)
        return redirect('attendance:my_leave_requests')
@login_required
def edit_leave_request(request, pk):
    """Allow users to edit their own pending leave requests"""
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    
    # Ensure the user can only edit their own pending requests
    if leave_request.user != request.user:
        return HttpResponseForbidden("You don't have permission to edit this request.")
        
    if leave_request.status != 'pending':
        messages.error(request, 'Only pending leave requests can be edited.')
        return redirect('attendance:my_leave_requests')
    
    if request.method == 'POST':
        form = LeaveRequestForm(
            request.POST, 
            request.FILES, 
            instance=leave_request,
            user=request.user
        )
        if form.is_valid():
            updated_request = form.save(commit=False)
            updated_request.updated_at = timezone.now()
            updated_request.save()
            messages.success(request, 'Your leave request has been updated.')
            return redirect('attendance:view_leave_request', pk=leave_request.id)
    else:
        form = LeaveRequestForm(instance=leave_request, user=request.user)
    
    return render(request, 'attendance/request_leave.html', {
        'form': form,
        'title': 'Edit Leave Request',
        'editing': True
    })

@login_required
@login_required
def mark_absence(request):
    """Allow staff to mark themselves as absent with a reason"""
    if request.method == 'POST':
        form = AbsenceForm(request.POST)
        if form.is_valid():
            absence_date = form.cleaned_data['date']
            
            # Check if user already has an attendance record for this date
            existing = Attendance.objects.filter(
                user=request.user,
                date=absence_date
            ).exists()
            
            if existing:
                messages.warning(request, 'You already have an attendance record for this date.')
            else:
                # Create absent record
                Attendance.objects.create(
                    user=request.user,
                    date=absence_date,
                    attendance_type=Attendance.ABSENT,
                    status='manual',
                    notes=form.cleaned_data['reason'],
                    recorded_by=request.user
                )
                messages.success(request, f'Successfully recorded absence for {absence_date}')
                return redirect('attendance:dashboard')
    else:
        form = AbsenceForm()
    
    return render(request, 'attendance/mark_absence.html', {'form': form})

@login_required
def clear_attendance_history(request):
    """Clear attendance history for the current user"""
    if request.method == 'POST':
        try:
            # Only delete records older than today
            today = timezone.now().date()
            deleted_count = Attendance.objects.filter(
                user=request.user,
                timestamp__date__lt=today
            ).delete()
            
            messages.success(request, f'Successfully cleared {deleted_count[0]} attendance records.')
        except Exception as e:
            messages.error(request, f'Error clearing attendance history: {str(e)}')
    
    return redirect('attendance:history')

@login_required
def attendance_history(request, user_id=None):
    """View attendance history with filtering options"""
    # If user_id is provided and current user is staff, show that user's attendance
    if user_id and request.user.is_staff:
        user = get_object_or_404(User, id=user_id, is_active=True, is_staff=True)
        is_own_profile = (user == request.user)
    else:
        user = request.user
        is_own_profile = True
    
    # Get date range from request or use default (last 30 days)
    end_date = timezone.now().date()
    start_date = end_date - timezone.timedelta(days=30)
    
    if 'start_date' in request.GET and 'end_date' in request.GET:
        try:
            start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
            end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
            # Ensure end_date is not in the future
            if end_date > timezone.now().date():
                end_date = timezone.now().date()
            # Ensure date range is not too large (max 1 year)
            if (end_date - start_date).days > 365:
                messages.warning(request, "Date range is too large. Showing maximum of 1 year of data.")
                start_date = end_date - timezone.timedelta(days=365)
        except (ValueError, TypeError) as e:
            messages.error(request, "Invalid date format. Please use YYYY-MM-DD format.")
    
    # Get all attendance records (both check-in and check-out) for the user and date range
    attendance_records = Attendance.objects.filter(
        Q(user=user) &
        (
            (Q(date__isnull=False) & Q(date__range=[start_date, end_date])) |
            (Q(timestamp__date__range=[start_date, end_date]))
        )
    ).order_by('timestamp')
    
    # Debug information
    print(f"Found {attendance_records.count()} attendance records between {start_date} and {end_date}")
    
    # Create a dictionary to store attendance by date
    attendance_by_date = {}
    
    # Process each record
    for record in attendance_records:
        # Use date from record or fallback to timestamp date
        record_date = record.date if record.date else record.timestamp.date()
        
        # Initialize date entry if it doesn't exist
        if record_date not in attendance_by_date:
            attendance_by_date[record_date] = {
                'check_in': None,
                'check_out': None,
                'duration': None
            }
        
        # Update check-in or check-out
        if record.attendance_type == 'check_in':
            attendance_by_date[record_date]['check_in'] = record.timestamp
        elif record.attendance_type == 'check_out':
            attendance_by_date[record_date]['check_out'] = record.timestamp
        
        # Calculate duration if both check-in and check-out exist
        current = attendance_by_date[record_date]
        if current['check_in'] and current['check_out']:
            duration = current['check_out'] - current['check_in']
            hours, remainder = divmod(duration.total_seconds(), 3600)
            minutes, _ = divmod(remainder, 60)
            current['duration'] = f"{int(hours)}h {int(minutes)}m"
    
    # Convert to a sorted list of dates
    sorted_dates = sorted(attendance_by_date.keys(), reverse=True)
    attendance_days = {date: attendance_by_date[date] for date in sorted_dates}
    
    # Calculate summary statistics
    total_days = (end_date - start_date).days + 1
    present_days = len([d for d, data in attendance_by_date.items() if data['check_in']])
    attendance_percentage = round((present_days / total_days * 100), 2) if total_days > 0 else 0
    
# Get all staff for the staff selector (admin only)
    staff_list = []
    if request.user.is_staff:
        staff_list = User.objects.filter(is_staff=True, is_active=True).order_by('first_name', 'last_name')
    
    # Debug output
    print(f"Processed {len(attendance_days)} days with attendance data")
    print(f"Present days: {present_days}, Total days: {total_days}, Attendance: {attendance_percentage}%")
    
    context = {
        'attendance_records': attendance_records,
        'attendance_days': attendance_days,
        'start_date': start_date,
        'end_date': end_date,
        'total_days': total_days,
        'present_days': present_days,
        'absent_days': total_days - present_days,
        'attendance_percentage': attendance_percentage,
        'staff_list': staff_list,
        'selected_user': user,
        'is_own_profile': is_own_profile,
    }
    
    template = 'attendance/admin/staff_attendance_history.html' if request.user.is_staff else 'attendance/history.html'
    return render(request, template, context)


@login_required
def admin_dashboard(request):
    """Admin dashboard for managing attendance - OPTIMIZED VERSION"""
    if not request.user.is_staff:
        return redirect('attendance:dashboard')

    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())

    try:
        # OPTIMIZATION 1: Use more efficient queries with limits and defer unnecessary fields
        print("Starting admin dashboard queries...")

        # Get pending leave requests (limit to 10 for dashboard)
        pending_requests = LeaveRequest.objects.filter(
            status='pending'
        ).select_related('user').only(
            'id', 'user__first_name', 'user__last_name', 'user__email',
            'leave_type', 'start_date', 'end_date', 'created_at'
        ).order_by('-created_at')[:10]  # Limit to 10 most recent

        print(f"Found {pending_requests.count()} pending requests")

        # Count active staff - simple count query
        total_staff = User.objects.filter(is_active=True, is_staff=True).count()
        print(f"Total staff: {total_staff}")

        # Get today's check-ins (optimized with only necessary fields)
        recent_checkins = Attendance.objects.filter(
            timestamp__date=today,
            attendance_type='check_in'
        ).select_related('user').only(
            'id', 'user__first_name', 'user__last_name', 'timestamp',
            'user__email', 'attendance_type'
        ).order_by('-timestamp')[:5]

        print(f"Found {recent_checkins.count()} recent checkins")

        # Get today's attendance summary (simplified - just count)
        today_attendance_count = Attendance.objects.filter(
            timestamp__date=today
        ).count()

        # Get upcoming holidays (limited)
        upcoming_holidays = Holiday.objects.filter(
            date__gte=today
        ).only('id', 'name', 'date').order_by('date')[:5]

        # Get recent past holidays (limited)
        past_holidays = Holiday.objects.filter(
            date__lt=today
        ).only('id', 'name', 'date').order_by('-date')[:5]

        # OPTIMIZATION 2: Simplify staff attendance summary - use direct queries
        staff_attendance_summary = []

        # Get active staff members
        staff_members = User.objects.filter(
            is_active=True,
            is_staff=True
        ).only('id', 'first_name', 'last_name', 'email')[:10]  # Limit to 10 staff

        for staff in staff_members:
            # Get week check-ins count using the correct related name 'attendances'
            week_checkins_count = Attendance.objects.filter(
                user=staff,
                timestamp__date__range=[start_of_week, today],
                attendance_type='check_in'
            ).count()

            # Get last check-in for this staff member
            last_check_in = Attendance.objects.filter(
                user=staff,
                attendance_type='check_in'
            ).only('timestamp').order_by('-timestamp').first()

            staff_attendance_summary.append({
                'staff': staff,
                'present_days': week_checkins_count,
                'total_days': (today - start_of_week).days + 1,
                'last_check_in': last_check_in,
            })

        print("All queries completed successfully")

        context = {
            'today_attendance_count': today_attendance_count,
            'pending_requests': pending_requests,
            'upcoming_holidays': upcoming_holidays,
            'past_holidays': past_holidays,
            'staff_attendance': staff_attendance_summary,
            'recent_checkins': recent_checkins,
            'total_staff': total_staff,
            'today': today,
            'start_of_week': start_of_week,
        }

        return render(request, 'attendance/admin/dashboard.html', context)

    except Exception as e:
        logger.error(f"Error in admin_dashboard view: {str(e)}")
        # Return a simplified context if there's an error
        context = {
            'today_attendance_count': 0,
            'pending_requests': [],
            'upcoming_holidays': [],
            'past_holidays': [],
            'staff_attendance': [],
            'recent_checkins': [],
            'total_staff': 0,
            'today': timezone.now().date(),
            'start_of_week': timezone.now().date() - timedelta(days=timezone.now().date().weekday()),
            'error': str(e)
        }
        messages.error(request, "An error occurred while loading the admin dashboard. Some data may be unavailable.")
        return render(request, 'attendance/admin/dashboard.html', context)
@login_required
def manage_leave_request(request, pk):
    """Approve/Reject leave requests with admin notes"""
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    
    if request.method == 'POST':
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"POST data: {dict(request.POST)}")
        
        action = request.POST.get('action')
        response_notes = request.POST.get('response_notes', '').strip()
        
        logger.info(f"Action: {action}, Response Notes: {response_notes}")
        
        if action == 'approved':
            leave_request.status = 'approved'
            success_message = 'Leave request approved successfully.'
        elif action == 'rejected':
            leave_request.status = 'rejected'
            success_message = 'Leave request rejected.'
        else:
            messages.error(request, 'Invalid action.')
            return redirect('attendance:admin_leave_requests')
            
        # Update leave request with admin details and notes
        leave_request.response_notes = response_notes
        leave_request.processed_by = request.user
        leave_request.processed_at = timezone.now()
        leave_request.save()
        
        # Add success message with the action taken
        messages.success(request, success_message)
        
        # If it's an AJAX request, return JSON response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Get the user's full name or email
            processed_by_name = (
                getattr(leave_request.processed_by, 'get_full_name', None) and 
                leave_request.processed_by.get_full_name()
            ) or getattr(leave_request.processed_by, 'email', 'System')
            
            return JsonResponse({
                'success': True,
                'message': success_message,
                'status': leave_request.get_status_display(),
                'processed_at': leave_request.processed_at.strftime('%b %d, %Y %I:%M %p'),
                'processed_by': processed_by_name
            })
            
        return redirect('attendance:admin_leave_requests')
        
    return render(request, 'attendance/admin/manage_leave.html', {'leave_request': leave_request})

@login_required
def admin_attendance_report(request):
    """Generate attendance reports for admin"""
    today = timezone.now().date()
    start_date = request.GET.get('start_date', (today - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.GET.get('end_date', today.strftime('%Y-%m-%d'))
    
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        start_date = today - timedelta(days=30)
        end_date = today
    
    # Get all active staff users
    users = User.objects.filter(is_active=True, is_staff=True).order_by('first_name', 'last_name')
    
    # Get attendance summary
    attendance_summary = []
    for user in users:
        # Get user's attendance records in the date range
        user_attendance = Attendance.objects.filter(
            user=user,
            timestamp__date__range=[start_date, end_date]
        ).order_by('timestamp')
        
        # Get unique dates with check-ins
        present_dates = user_attendance.filter(
            attendance_type='check_in'
        ).values_list('timestamp__date', flat=True).distinct()
        
        # Get all dates in the range
        all_dates = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]
        
        # Calculate present and absent days
        present_days = len(present_dates)
        total_days = len(all_dates)
        absent_days = total_days - present_days
        
        attendance_summary.append({
            'user': user,
            'present_days': present_days,
            'absent_days': absent_days,
            'total_days': total_days,
            'attendance_percentage': round((present_days / total_days * 100) if total_days > 0 else 0, 2)
        })
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'attendance_summary': attendance_summary,
        'total_users': users.count(),
    }
    
    return render(request, 'attendance/admin/attendance_report.html', context)


@login_required
def admin_leave_requests(request):
    """View all leave requests for admin, organized by status - FIXED VERSION"""
    if not request.user.is_staff:
        return redirect('attendance:dashboard')

    # Get the active tab from the request, default to 'pending'
    active_tab = request.GET.get('status', 'pending')

    # Validate the active_tab value
    if active_tab not in ['pending', 'approved', 'rejected']:
        active_tab = 'pending'

    try:
        print("Starting FIXED admin_leave_requests queries...")

        # Get counts first (lightweight queries)
        pending_count = LeaveRequest.objects.filter(status='pending').count()
        approved_count = LeaveRequest.objects.filter(status='approved').count()
        rejected_count = LeaveRequest.objects.filter(status='rejected').count()

        print(f"Counts - Pending: {pending_count}, Approved: {approved_count}, Rejected: {rejected_count}")

        # OPTIMIZATION: Use simpler queries with only necessary fields
        base_queryset = LeaveRequest.objects.select_related('user').only(
            'id', 'user__first_name', 'user__last_name', 'user__email',
            'leave_type', 'start_date', 'end_date', 'status', 'created_at',
            'reviewed_by', 'response_notes', 'reviewed_at'
        )

        # FIX: Always load data for all tabs, but with limits for performance
        pending_requests = base_queryset.filter(status='pending').order_by('-created_at')[:50]
        approved_requests = base_queryset.filter(status='approved').order_by('-created_at')[:50]
        rejected_requests = base_queryset.filter(status='rejected').order_by('-created_at')[:50]

        print(
            f"Loaded {pending_requests.count()} pending, {approved_requests.count()} approved, {rejected_requests.count()} rejected requests")

        # Prepare the context
        context = {
            'pending_requests': pending_requests,
            'approved_requests': approved_requests,
            'rejected_requests': rejected_requests,
            'pending_count': pending_count,
            'approved_count': approved_count,
            'rejected_count': rejected_count,
            'active_tab': active_tab,
        }

        print("All queries completed successfully")
        return render(request, 'attendance/admin_leave_management.html', context)

    except Exception as e:
        logger.error(f"Error in admin_leave_requests view: {str(e)}")
        # Return a simplified context if there's an error
        context = {
            'pending_requests': [],
            'approved_requests': [],
            'rejected_requests': [],
            'pending_count': 0,
            'approved_count': 0,
            'rejected_count': 0,
            'active_tab': active_tab,
            'error': str(e)
        }
        messages.error(request, "An error occurred while loading leave requests. Some data may be unavailable.")
        return (render(request, 'attendance/admin_leave_management.html', context)


@login_required)
def leave_management_dashboard(request):
    """Comprehensive leave management dashboard for admins"""
    if not request.user.is_staff:
        return redirect('attendance:dashboard')
    
    # Get all leave requests with related user data
    leave_requests = LeaveRequest.objects.select_related('user', 'reviewed_by').order_by('-created_at')
    
    # Filter by status
    pending_requests = leave_requests.filter(status='pending')
    approved_requests = leave_requests.filter(status='approved')
    rejected_requests = leave_requests.filter(status='rejected')
    
    # Get counts for each status
    pending_count = pending_requests.count()
    approved_count = approved_requests.count()
    rejected_count = rejected_requests.count()
    
    # Get recent leave requests (last 30 days)
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    recent_requests = leave_requests.filter(created_at__gte=thirty_days_ago)
    
    # Get holidays
    today = timezone.now().date()
    upcoming_holidays = Holiday.objects.filter(date__gte=today).order_by('date')
    past_holidays = Holiday.objects.filter(date__lt=today).order_by('-date')[:10]  # Recent 10 past holidays
    
    # Calculate leave statistics
    leave_stats = {
        'total_requests': leave_requests.count(),
        'avg_duration': leave_requests.aggregate(avg=Avg('duration_days'))['avg'] or 0,
        'approval_rate': (approved_requests.count() / leave_requests.count() * 100) if leave_requests.exists() else 0,
    }
    
    # Get the current tab (default to 'pending')
    active_tab = request.GET.get('tab', 'pending')
    
    context = {
        'pending_requests': pending_requests[:5],  # Show only 5 most recent
        'approved_requests': approved_requests[:5],
        'rejected_requests': rejected_requests[:5],
        'recent_requests': recent_requests[:10],
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'leave_stats': leave_stats,
        'upcoming_holidays': upcoming_holidays,
        'past_holidays': past_holidays,
        'active_tab': active_tab,
    }
    
    return render(request, 'attendance/admin_leave_management.html', context)

@login_required
def manage_holidays(request):
    """View and manage holidays"""
    year = request.GET.get('year', timezone.now().year)
    holidays = Holiday.objects.filter(date__year=year).order_by('date')
    
    context = {
        'holidays': holidays,
        'current_year': int(year),
        'years': range(timezone.now().year - 5, timezone.now().year + 5),
    }
    
    return render(request, 'attendance/admin/holidays.html', context)

@login_required
def add_holiday(request):
    """Add a new holiday"""
    if request.method == 'POST':
        form = HolidayForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Holiday added successfully.')
            return redirect('attendance:admin_manage_holidays')
    else:
        form = HolidayForm()
    
    return render(request, 'attendance/admin/holiday_form.html', {
        'form': form,
        'title': 'Add Holiday'
    })

@login_required
def edit_holiday(request, pk):
    """Edit an existing holiday"""
    holiday = get_object_or_404(Holiday, pk=pk)
    
    if request.method == 'POST':
        form = HolidayForm(request.POST, instance=holiday)
        if form.is_valid():
            form.save()
            messages.success(request, 'Holiday updated successfully.')
            return redirect('attendance:admin_manage_holidays')
    else:
        form = HolidayForm(instance=holiday)
    
    return render(request, 'attendance/admin/holiday_form.html', {
        'form': form,
        'title': 'Edit Holiday',
        'holiday': holiday
    })

@login_required
def delete_holiday(request, pk):
    """Delete a holiday"""
    holiday = get_object_or_404(Holiday, pk=pk)
    
    if request.method == 'POST':
        holiday.delete()
        messages.success(request, 'Holiday deleted successfully.')
        return redirect('attendance:admin_manage_holidays')
    
    return render(request, 'attendance/admin/delete_holiday.html', {
        'holiday': holiday
    })

def working_days_count(start_date, end_date):
    """
    Returns the number of working days (Monday to Saturday) between two dates (inclusive).
    """
    days = (end_date - start_date).days + 1
    # Calculate full weeks and remaining days
    full_weeks = days // 7
    remaining_days = days % 7
    # Start with full weeks (6 working days per week - Monday to Saturday)
    working_days = full_weeks * 6
    # Add remaining working days
    start_weekday = start_date.weekday()  # Monday is 0, Sunday is 6
    for day in range(remaining_days):
        current_weekday = (start_weekday + day) % 7
        if current_weekday < 6:  # 0-5 are Monday to Saturday
            working_days += 1
    return working_days

@login_required
def staff_attendance_history(request, user_id):
    """View attendance history for a specific staff member (admin only)"""
    if not request.user.is_staff:
        return redirect('attendance:dashboard')
        
    staff = get_object_or_404(User, id=user_id)
    
    # Only allow admin to view staff attendance
    if not request.user.is_superuser and request.user != staff:
        raise Http404("You don't have permission to view this page.")
    
    # Get date range from request or use default (last 30 days)
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    if 'start_date' in request.GET and 'end_date' in request.GET:
        try:
            start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
            end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
            
            # Validate date range
            if end_date < start_date:
                messages.error(request, 'End date cannot be before start date. Using default date range.')
                end_date = timezone.now().date()
                start_date = end_date - timedelta(days=30)
            # Ensure end_date is not in the future
            elif end_date > timezone.now().date():
                end_date = timezone.now().date()
                messages.warning(request, 'End date adjusted to today.')
            # Ensure date range is not too large (max 1 year)
            if (end_date - start_date).days > 365:
                start_date = end_date - timedelta(days=365)
                messages.warning(request, 'Date range limited to 1 year')
        except (ValueError, TypeError) as e:
            messages.error(request, f'Invalid date format: {str(e)}. Using default date range.')
    
    # Get all attendance records for the date range
    staff_name = f"{staff.first_name} {staff.last_name}".strip()
    print(f"\n=== Fetching attendance records ===")
    print(f"Staff: {staff_name}")
    print(f"Date Range: {start_date} to {end_date}")
    
    # Get records in chronological order for accurate processing
    attendance_records = Attendance.objects.filter(
        user=staff,
        timestamp__date__range=[start_date, end_date]
    ).order_by('timestamp')
    
    print(f"Found {attendance_records.count()} records in date range")
    
    # Initialize attendance_by_date with all working days in range (Monday to Saturday)
    attendance_by_date = {}
    current_date = start_date
    while current_date <= end_date:
        # Include Monday (0) through Saturday (5)
        if current_date.weekday() < 6:  # 0-5 = Monday-Saturday
            attendance_by_date[current_date] = {
                'check_in': None,
                'check_out': None,
                'duration': None,
                'status': 'absent'  # Default status
            }
        current_date += timedelta(days=1)
    
    # Process each record and update attendance data
    for record in attendance_records:
        record_date = record.timestamp.date()
        
        # Skip if date is outside our range (shouldn't happen due to query)
        if record_date not in attendance_by_date:
            print(f"Skipping record outside working days: {record_date}")
            continue
            
        # Update check-in or check-out time
        if record.attendance_type == 'check_in':
            if attendance_by_date[record_date]['check_in'] is None or \
               record.timestamp < attendance_by_date[record_date]['check_in']:
                attendance_by_date[record_date]['check_in'] = record.timestamp
                
        elif record.attendance_type == 'check_out':
            if attendance_by_date[record_date]['check_out'] is None or \
               record.timestamp > attendance_by_date[record_date]['check_out']:
                attendance_by_date[record_date]['check_out'] = record.timestamp
    
    # Calculate durations and status for each day
    for date_key, data in attendance_by_date.items():
        if data['check_in'] and data['check_out']:
            if data['check_out'] > data['check_in']:
                duration = data['check_out'] - data['check_in']
                hours, remainder = divmod(duration.total_seconds(), 3600)
                minutes, _ = divmod(remainder, 60)
                data['duration'] = f"{int(hours)}h {int(minutes):02d}m"
                data['status'] = 'present'
            else:
                data['status'] = 'invalid_times'
        elif data['check_in']:
            data['status'] = 'checked_in_only'
        elif data['check_out']:
            data['status'] = 'checked_out_only'
    
    # Sort dates in descending order for display
    sorted_dates = sorted(attendance_by_date.keys(), reverse=True)
    attendance_days = {date: attendance_by_date[date] for date in sorted_dates}
    
    # Calculate statistics
    present_days = sum(1 for data in attendance_days.values() if data['status'] == 'present')
    total_working_days = len(attendance_days)
    attendance_percentage = round((present_days / total_working_days * 100), 2) if total_working_days > 0 else 0
    
    # Debug information
    print("\n=== Attendance Summary ===")
    print(f"Total working days in range: {total_working_days}")
    print(f"Present days (complete check-in/out): {present_days}")
    print(f"Partial records: {sum(1 for d in attendance_days.values() if d['status'] in ['checked_in_only', 'checked_out_only'])}")
    print(f"Attendance: {present_days}/{total_working_days} = {attendance_percentage:.2f}%")
    print("=======================\n")
    
    # Calculate summary statistics
    total_working_days = working_days_count(start_date, end_date)
    present_days = len([d for d, data in attendance_days.items() if data['check_in']])
    absent_days = total_working_days - present_days
    attendance_percentage = round((present_days / total_working_days * 100), 2) if total_working_days > 0 else 0
    
    # Get staff list for the dropdown
    staff_list = User.objects.filter(is_staff=True).order_by('first_name', 'last_name')
    
    return render(request, 'attendance/admin/staff_attendance_history.html', {
        'staff': staff,
        'selected_user': staff,  # Ensure selected_user is available
        'is_own_profile': request.user == staff,
        'staff_list': staff_list,  # Staff list for dropdown
        'attendance_records': attendance_records,
        'attendance_days': attendance_days,
        'start_date': start_date,
        'end_date': end_date,
        'total_working_days': total_working_days,
        'present_days': present_days,
        'absent_days': absent_days,
        'attendance_percentage': attendance_percentage
    })

@login_required
def all_staff_attendance(request):
    """View attendance summary for all staff members (admin only)"""
    if not request.user.is_staff:
        return redirect('attendance:dashboard')
    
    # Get date range from request or use default (current month)
    today = timezone.now().date()
    start_date = request.GET.get('start_date') or today.replace(day=1).strftime('%Y-%m-%d')
    end_date = request.GET.get('end_date') or today.strftime('%Y-%m-%d')
    
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Ensure end_date is not in the future
        if end_date > today:
            end_date = today
            
        # Ensure date range is not too large (max 1 year)
        if (end_date - start_date).days > 365:
            start_date = end_date - timedelta(days=365)
            messages.warning(request, 'Date range limited to 1 year')
            
    except (ValueError, TypeError):
        start_date = today.replace(day=1)
        end_date = today
        messages.error(request, 'Invalid date format. Using current month.')
    
    # Get all active staff members
    staff_members = User.objects.filter(is_staff=True, is_active=True).order_by('first_name', 'last_name')
    
    staff_attendance = []
    for staff in staff_members:
        # Get all check-in/check-out pairs for the date range
        attendance_data = Attendance.objects.filter(
            user=staff,
            timestamp__date__range=[start_date, end_date]
        ).order_by('timestamp')
        
        # Group by date and calculate working hours
        daily_hours = {}
        for record in attendance_data:
            date_key = record.timestamp.date()
            if date_key not in daily_hours:
                daily_hours[date_key] = {'check_in': None, 'check_out': None}
            
            if record.attendance_type == 'check_in':
                daily_hours[date_key]['check_in'] = record.timestamp
            elif record.attendance_type == 'check_out':
                daily_hours[date_key]['check_out'] = record.timestamp
        
        # Calculate total working hours and present days
        total_hours = 0
        present_days = 0
        
        for date_key, times in daily_hours.items():
            if times['check_in'] and times['check_out']:
                duration = times['check_out'] - times['check_in']
                total_hours += duration.total_seconds() / 3600  # Convert to hours
                present_days += 1
        
        total_days = (end_date - start_date).days + 1
        attendance_percentage = round((present_days / total_days * 100), 2) if total_days > 0 else 0
        
        staff_attendance.append({
            'staff': staff,
            'present_days': present_days,
            'total_days': total_days,
            'attendance_percentage': attendance_percentage,
            'total_hours': round(total_hours, 2),
            'last_activity': attendance_data.last().timestamp if attendance_data.exists() else None,
        })
    
    # Sort by staff name
    staff_attendance = sorted(staff_attendance, key=lambda x: (x['staff'].first_name, x['staff'].last_name))
    
    return render(request, 'attendance/admin/all_staff_attendance.html', {
        'staff_attendance': staff_attendance,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'total_days': (end_date - start_date).days + 1,
    })
