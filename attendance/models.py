from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Attendance(models.Model):
    """
    Model to track staff attendance (clock in/out)
    """
    CHECK_IN = 'check_in'
    CHECK_OUT = 'check_out'
    ABSENT = 'absent'
    PRESENT = 'present'
    
    ATTENDANCE_TYPES = [
        (CHECK_IN, 'Check In'),
        (CHECK_OUT, 'Check Out'),
        (ABSENT, 'Absent'),
        (PRESENT, 'Present'),
    ]
    
    STATUS_CHOICES = [
        ('auto', 'Automatic'),
        ('manual', 'Manual'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    timestamp = models.DateTimeField(auto_now_add=True)
    attendance_type = models.CharField(max_length=10, choices=ATTENDANCE_TYPES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='auto')
    notes = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                  related_name='recorded_attendances')
    
    class Meta:
        ordering = ['-date', '-timestamp']
        unique_together = ('user', 'date', 'attendance_type')
    
    def save(self, *args, **kwargs):
        # Set the date field to the date part of timestamp if not set
        if not self.date and self.timestamp:
            self.date = self.timestamp.date()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Attendance Records'

    def __str__(self):
        user_identifier = getattr(self.user, 'username', None) or getattr(self.user, 'email', str(self.user.id))
        return f"{user_identifier} - {self.get_attendance_type_display()} at {self.timestamp}"


class LeaveRequest(models.Model):
    """
    Model for staff to request time off
    """
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
        (CANCELLED, 'Cancelled'),
    ]
    
    LEAVE_TYPES = [
        ('annual', 'Annual Leave'),
        ('sick', 'Sick Leave'),
        ('maternity', 'Maternity/Paternity'),
        ('unpaid', 'Unpaid Leave'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES, default='annual')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='reviewed_leave_requests'
    )
    response_notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        permissions = [
            ('can_approve_leave', 'Can approve leave requests'),
        ]
    
    def save(self, *args, **kwargs):
        # Set reviewed_at timestamp when status changes from pending
        if self.pk:
            old_instance = LeaveRequest.objects.get(pk=self.pk)
            if old_instance.status == 'pending' and self.status != 'pending':
                self.reviewed_at = timezone.now()
        super().save(*args, *kwargs)
        
        # If approved, mark user as absent for these dates
        if self.status == 'approved':
            from django.db.models import Q
            from datetime import timedelta
            
            # Delete any existing absent records for these dates to avoid duplicates
            Attendance.objects.filter(
                user=self.user,
                date__range=[self.start_date, self.end_date],
                attendance_type=Attendance.ABSENT
            ).delete()
            
            # Create absent records for each day of leave
            current_date = self.start_date
            while current_date <= self.end_date:
                # Skip weekends (optional)
                if current_date.weekday() < 5:  # 0=Monday, 6=Sunday
                    Attendance.objects.update_or_create(
                        user=self.user,
                        date=current_date,
                        attendance_type=Attendance.ABSENT,
                        defaults={
                            'status': 'manual',
                            'notes': f'On approved {self.get_leave_type_display()}: {self.reason}',
                            'recorded_by': self.reviewed_by
                        }
                    )
                current_date += timedelta(days=1)

    class Meta:
        ordering = ['-created_at']

    @property
    def duration_days(self):
        """Calculate the total number of days between start_date and end_date (inclusive)"""
        return (self.end_date - self.start_date).days + 1

    def __str__(self):
        return f"{self.user.email} - {self.start_date} to {self.end_date} ({self.get_status_display()})"


class Holiday(models.Model):
    """
    Model to track public holidays
    """
    name = models.CharField(max_length=100)
    date = models.DateField(unique=True)
    description = models.TextField(blank=True, null=True)
    is_recurring = models.BooleanField(default=False, help_text="Does this holiday occur every year?")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.name} ({self.date})"
