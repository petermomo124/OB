from django.contrib import admin
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.auth import get_user_model
from .models import LeaveRequest, Attendance, Holiday

User = get_user_model()

class StatusFilter(admin.SimpleListFilter):
    title = 'status'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return [
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('cancelled', 'Cancelled'),
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'leave_type_display', 'date_range', 'get_duration_days', 'status_badge', 'created_at', 'action_buttons')
    list_filter = (StatusFilter, 'leave_type', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'reason')
    list_per_page = 20
    actions = ['approve_selected_leave', 'reject_selected_leave']
    readonly_fields = ('created_at', 'updated_at', 'reviewed_at', 'get_duration_days')
    
    fieldsets = (
        ('Leave Information', {
            'fields': ('user', 'leave_type', 'start_date', 'end_date', 'get_duration_days', 'reason')
        }),
        ('Status', {
            'fields': ('status', 'response_notes', 'reviewed_by', 'reviewed_at')
        }),
        ('System Information', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(user=request.user)
        return qs
    
    def leave_type_display(self, obj):
        return obj.get_leave_type_display()
    leave_type_display.short_description = 'Leave Type'
    
    def date_range(self, obj):
        return f"{obj.start_date.strftime('%b %d, %Y')} - {obj.end_date.strftime('%b %d, %Y')}"
    date_range.short_description = 'Date Range'
    
    def get_duration_days(self, obj):
        return (obj.end_date - obj.start_date).days + 1
    get_duration_days.short_description = 'Duration (Days)'
    
    def status_badge(self, obj):
        status_colors = {
            'pending': 'warning',
            'approved': 'success',
            'rejected': 'danger',
            'cancelled': 'secondary'
        }
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            status_colors.get(obj.status, 'secondary'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def action_buttons(self, obj):
        buttons = []
        if obj.status == 'pending':
            buttons.append(
                f'<a href="#" class="btn btn-sm btn-success approve-leave" data-id="{obj.id}">Approve</a>'
            )
            buttons.append(
                f'<a href="#" class="btn btn-sm btn-danger reject-leave" data-id="{obj.id}">Reject</a>'
            )
        return format_html(' '.join(buttons))
    action_buttons.short_description = 'Actions'
    action_buttons.allow_tags = True
    
    def approve_selected_leave(self, request, queryset):
        updated = queryset.filter(status='pending').update(
            status='approved',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f'Successfully approved {updated} leave request(s).', messages.SUCCESS)
    approve_selected_leave.short_description = 'Approve selected leave requests'
    
    def reject_selected_leave(self, request, queryset):
        updated = queryset.filter(status='pending').update(
            status='rejected',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f'Successfully rejected {updated} leave request(s).', messages.SUCCESS)
    reject_selected_leave.short_description = 'Reject selected leave requests'
    
    class Media:
        js = (
            'admin/js/vendor/jquery/jquery.min.js',  # Ensure jQuery is loaded first
            'attendance/js/admin/leave_actions.js',
        )
        css = {
            'all': (
                'admin/css/forms.css',  # For consistent form styling
            )
        }

# Register other models
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'attendance_type', 'status', 'timestamp')
    list_filter = ('attendance_type', 'status', 'date')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    list_per_page = 50

@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'is_recurring')
    list_filter = ('is_recurring',)
    search_fields = ('name', 'description')
    date_hierarchy = 'date'
