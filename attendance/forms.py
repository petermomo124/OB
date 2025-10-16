from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .models import LeaveRequest, Holiday, Attendance

class LeaveRequestForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Add form-control class to all fields
        for field_name, field in self.fields.items():
            if field.widget.attrs.get('class') is None:
                if isinstance(field.widget, forms.Select):
                    field.widget.attrs['class'] = 'form-select'
                else:
                    field.widget.attrs['class'] = 'form-control'
    
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'leave_type': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control',
                'min': timezone.now().strftime('%Y-%m-%d')  # Prevent past dates
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control',
                'min': timezone.now().strftime('%Y-%m-%d')  # Prevent past dates
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Please provide a reason for your leave...',
                'required': 'required'
            }),
        }
        labels = {
            'leave_type': _('Type of Leave'),
            'start_date': _('Start Date'),
            'end_date': _('End Date'),
            'reason': _('Reason for Leave (required)'),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            today = timezone.now().date()
            if start_date < today:
                raise forms.ValidationError("Start date cannot be in the past.")
            if end_date < start_date:
                raise forms.ValidationError("End date must be after start date.")
                
            # Check for overlapping leave requests
            user = getattr(self, 'user', None)
            if user and user.is_authenticated:
                overlapping = LeaveRequest.objects.filter(
                    user=user,
                    status__in=['pending', 'approved'],
                    start_date__lte=end_date,
                    end_date__gte=start_date
                )
                
                if self.instance and self.instance.pk:
                    overlapping = overlapping.exclude(pk=self.instance.pk)
                    
                if overlapping.exists():
                    raise forms.ValidationError(
                        "You already have a leave request that overlaps with these dates. "
                        "Please check your existing leave requests."
                    )
        
        return cleaned_data

class AbsenceForm(forms.Form):
    """Form for staff to report an absence"""
    date = forms.DateField(
        label=_('Date of Absence'),
        widget=forms.DateInput(attrs={
            'type': 'date', 
            'class': 'form-control',
            'max': timezone.now().strftime('%Y-%m-%d')
        }),
        initial=timezone.now().date()
    )
    reason = forms.CharField(
        label=_('Reason for Absence'),
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 3,
            'placeholder': _('Please provide a reason for your absence...')
        })
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_date(self):
        date = self.cleaned_data['date']
        if date > timezone.now().date():
            raise forms.ValidationError(_("You cannot report a future absence. Please use the leave request form instead."))
            
        if self.user:
            # Check if user already has an attendance record for this date
            if Attendance.objects.filter(user=self.user, date=date).exists():
                raise forms.ValidationError(_("You already have an attendance record for this date."))
                
        return date


class HolidayForm(forms.ModelForm):
    class Meta:
        model = Holiday
        fields = ['name', 'date', 'description', 'is_recurring']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control',
                'min': '2000-01-01',
                'max': '2100-12-31'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('E.g., New Year\'s Day')
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': _('Optional description or notes about the holiday')
            }),
            'is_recurring': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'data-toggle': 'toggle',
                'data-on': _('Yes'),
                'data-off': _('No'),
                'data-onstyle': 'success',
                'data-offstyle': 'secondary'
            }),
        }
