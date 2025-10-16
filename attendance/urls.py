from django.urls import path
from django.contrib.auth.decorators import login_required, user_passes_test
from . import views

def admin_required(login_url='login'):
    return user_passes_test(lambda u: u.is_superuser, login_url=login_url)

app_name = 'attendance'

urlpatterns = [
    # Staff URLs
    path('', login_required(views.dashboard), name='dashboard'),
    path('clock-in-out/', login_required(views.clock_in_out), name='clock_in_out'),
    path('request-leave/', login_required(views.request_leave), name='request_leave'),
    # Leave requests
    path('my-leave-requests/', login_required(views.my_leave_requests), name='my_leave_requests'),
    path('leave-requests/delete-all/', login_required(views.delete_all_leave_requests), name='delete_all_leave_requests'),
    path('leave-requests/<int:pk>/view/', login_required(views.view_leave_request), name='view_leave_request_modal'),
    # Leave request management
    path('leave-request/<int:pk>/', login_required(views.view_leave_request), name='view_leave_request'),
    path('leave-request/<int:pk>/edit/', login_required(views.edit_leave_request), name='edit_leave_request'),
    path('leave-request/<int:pk>/delete/', login_required(views.cancel_leave_request), name='cancel_leave_request'),
    path('history/', login_required(views.attendance_history), name='history'),
    path('history/user/<int:user_id>/', login_required(views.attendance_history), name='user_attendance_history'),
    path('clear-history/', login_required(views.clear_attendance_history), name='clear_history'),
    path('mark-absence/', login_required(views.mark_absence), name='mark_absence'),

    # Admin URLs
    path('admin/dashboard/', login_required(admin_required()(views.admin_dashboard)), name='admin_dashboard'),
    path('admin/leave/<int:pk>/', login_required(admin_required()(views.manage_leave_request)), name='manage_leave'),
    path('admin/report/', login_required(admin_required()(views.admin_attendance_report)), name='admin_attendance_report'),
    path('admin/leave-requests/', login_required(admin_required()(views.admin_leave_requests)), name='admin_leave_requests'),
    path('admin/staff-attendance/', login_required(admin_required()(views.all_staff_attendance)), name='all_staff_attendance'),
    path('admin/staff-attendance/<int:user_id>/', login_required(admin_required()(views.staff_attendance_history)), name='staff_attendance_history'),
    path('admin/holidays/', login_required(admin_required()(views.manage_holidays)), name='admin_manage_holidays'),
    path('admin/holidays/add/', login_required(admin_required()(views.add_holiday)), name='admin_add_holiday'),
    path('admin/holidays/<int:pk>/edit/', login_required(admin_required()(views.edit_holiday)), name='admin_edit_holiday'),
    path('admin/holidays/<int:pk>/delete/', login_required(admin_required()(views.delete_holiday)), name='admin_delete_holiday'),
]
