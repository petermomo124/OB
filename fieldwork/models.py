from django.db import models
from django.contrib.auth.models import User
from core.models import User as CustomUser
import uuid
from django.utils import timezone
from django.core.exceptions import ValidationError


class FieldJob(models.Model):
    CATEGORY_CHOICES = [
        ('Forensic Service', 'Forensic Service'),
        ('Audit', 'Audit'),
        ('Tax', 'Tax'),
        ('Consulting', 'Consulting'),
        ('Advisory', 'Advisory'),
        ('Technology', 'Technology'),
        ('Managed Service', 'Managed Service'),
    ]

    job_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    site_address = models.TextField()
    date_of_job = models.DateTimeField()  # Changed from DateField to DateTimeField
    summary_of_work = models.TextField()
    client_name = models.CharField(max_length=255)
    poc_name = models.CharField(max_length=255)
    poc_email = models.EmailField()
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_field_jobs')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client_name} - {self.category} - {self.date_of_job.strftime('%Y-%m-%d %H:%M')}"

    def clean(self):
        """Validate that job date is not in the past"""
        super().clean()
        if self.date_of_job:
            # Make both datetimes timezone-aware for comparison
            current_time = timezone.now()
            if timezone.is_naive(self.date_of_job):
                # If date_of_job is naive, make it aware using the default timezone
                self.date_of_job = timezone.make_aware(self.date_of_job)

            if self.date_of_job < current_time:
                raise ValidationError({
                    'date_of_job': 'Job date and time cannot be in the past. Please select a future date and time.'
                })

    def save(self, *args, **kwargs):
        """Override save to ensure validation runs"""
        self.full_clean()
        super().save(*args, **kwargs)


class FieldJobAssignment(models.Model):
    field_job = models.ForeignKey(FieldJob, on_delete=models.CASCADE, related_name='assignments')
    staff = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='field_assignments')
    poc_approval_code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_code_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['field_job', 'staff']

    def __str__(self):
        # Safe way to get full name with fallback
        try:
            staff_name = self.staff.get_full_name()
        except AttributeError:
            staff_name = f"{self.staff.first_name} {self.staff.last_name}".strip() or self.staff.email
        return f"{staff_name} - {self.field_job.client_name}"


class FieldReport(models.Model):
    assignment = models.OneToOneField(FieldJobAssignment, on_delete=models.CASCADE, related_name='field_report')
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    site_visit_complete = models.BooleanField(default=False)
    revisit_required = models.BooleanField(default=False)
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    summary_of_work_performed = models.TextField(blank=True)
    fe_signature = models.CharField(max_length=255, blank=True)
    submission_location_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    submission_location_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    submission_location_address = models.TextField(blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        # Safe way to get full name with fallback
        try:
            staff_name = self.assignment.staff.get_full_name()
        except AttributeError:
            staff_name = f"{self.assignment.staff.first_name} {self.assignment.staff.last_name}".strip() or self.assignment.staff.email
        return f"Report - {staff_name} - {self.assignment.field_job.client_name}"