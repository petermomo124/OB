from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import FieldJob, FieldJobAssignment, FieldReport
from core.models import User


class FieldJobForm(forms.ModelForm):
    staff_members = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(role='staff', is_active=True, is_approved=True),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=True
    )

    class Meta:
        model = FieldJob
        fields = [
            'category', 'site_address', 'date_of_job',
            'summary_of_work', 'client_name', 'poc_name', 'poc_email'
        ]
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'site_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_of_job': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'min': timezone.localtime(timezone.now()).strftime('%Y-%m-%dT%H:%M')
            }),
            'summary_of_work': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'client_name': forms.TextInput(attrs={'class': 'form-control'}),
            'poc_name': forms.TextInput(attrs={'class': 'form-control'}),
            'poc_email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Order staff by first name for better UX
        self.fields['staff_members'].queryset = self.fields['staff_members'].queryset.order_by('first_name',
                                                                                               'last_name')

        # Set minimum datetime for the date picker (in local time)
        current_datetime = timezone.localtime(timezone.now()).strftime('%Y-%m-%dT%H:%M')
        self.fields['date_of_job'].widget.attrs['min'] = current_datetime

        # Set initial value to current datetime + 1 hour if creating new job
        if not self.instance.pk:
            one_hour_later = timezone.localtime(timezone.now() + timezone.timedelta(hours=1))
            self.fields['date_of_job'].initial = one_hour_later.strftime('%Y-%m-%dT%H:%M')

    def clean_date_of_job(self):
        """Validate that job date is not in the past"""
        date_of_job = self.cleaned_data.get('date_of_job')

        if date_of_job:
            # Convert naive datetime from form to aware datetime
            if timezone.is_naive(date_of_job):
                date_of_job = timezone.make_aware(date_of_job)

            current_time = timezone.now()

            # Compare both as aware datetimes
            if date_of_job < current_time:
                raise ValidationError(
                    'Job date and time cannot be in the past. Please select a future date and time.'
                )

            # Additional validation: cannot be more than 1 year in the future
            one_year_from_now = timezone.now() + timezone.timedelta(days=365)

            if date_of_job > one_year_from_now:
                raise ValidationError(
                    'Job date cannot be more than 1 year in the future. Please select a date within the next year.'
                )

        return date_of_job

    def clean(self):
        """Additional form-wide validation"""
        cleaned_data = super().clean()
        date_of_job = cleaned_data.get('date_of_job')

        # Ensure date_of_job is not in the past (additional check)
        if date_of_job:
            # Convert naive datetime from form to aware datetime
            if timezone.is_naive(date_of_job):
                date_of_job = timezone.make_aware(date_of_job)

            current_time = timezone.now()

            if date_of_job < current_time:
                self.add_error('date_of_job',
                               'Cannot schedule a job in the past. Please select a future date and time.')

        return cleaned_data


from django import forms
from .models import FieldReport


class FieldReportForm(forms.ModelForm):
    # ADD THIS FIELD - it's form-only, not saved to the model
    poc_signature = forms.CharField(
        max_length=255,
        required=True,
        label="POC Approval Signature",
        help_text="Enter the approval code provided by the Point of Contact",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter POC approval code'
        })
    )

    class Meta:
        model = FieldReport
        fields = [
            'summary_of_work_performed',
            'site_visit_complete',
            'revisit_required',
            'hours_worked',
            'fe_signature'
            # Note: poc_signature is NOT included here since it's form-only
        ]
        widgets = {
            'summary_of_work_performed': forms.Textarea(attrs={
                'rows': 4,
                'required': True,
                'class': 'form-control'
            }),
            'hours_worked': forms.NumberInput(attrs={
                'required': True,
                'step': '0.01',
                'class': 'form-control',
                'min': '0'
            }),
            'fe_signature': forms.TextInput(attrs={
                'required': True,
                'class': 'form-control'
            }),
            'site_visit_complete': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'revisit_required': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields required except for checkboxes
        self.fields['summary_of_work_performed'].required = True
        self.fields['hours_worked'].required = True
        self.fields['fe_signature'].required = True
        self.fields['poc_signature'].required = True  # ADD THIS LINE
        # These two remain optional
        self.fields['site_visit_complete'].required = False
        self.fields['revisit_required'].required = False