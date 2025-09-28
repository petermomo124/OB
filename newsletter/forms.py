from django import forms
from .models import Subscriber, Newsletter

from django import forms
from .models import Subscriber, Newsletter  # assuming you need Subscriber model access


class SubscriberForm(forms.Form):
    """
    Form modified to accept the 'instance' argument for initialization,
    while still inheriting from forms.Form to avoid unique validation.
    """
    first_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your first name'})
    )
    last_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your last name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your email'})
    )

    # Choices for newsletter preferences
    CHOICES = [
        ('audit', 'Audit'),
        ('tax', 'Tax'),
        ('consulting', 'Consulting'),
        ('forensic_service', 'Forensic Service'),
        ('managed_service', 'Managed Service'),
        ('technology_solution', 'Technology Solution'),
        ('advisory', 'Advisory'),
    ]

    preferences = forms.MultipleChoiceField(
        choices=CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    def __init__(self, *args, **kwargs):
        # 1. Intercept and retrieve the 'instance' before calling super().__init__
        instance = kwargs.pop('instance', None)

        # 2. Call the parent constructor (which doesn't accept 'instance')
        super().__init__(*args, **kwargs)

        # 3. If an instance was passed, use its data to set the initial values
        if instance:
            self.fields['first_name'].initial = instance.first_name
            self.fields['last_name'].initial = instance.last_name
            self.fields['email'].initial = instance.email

            # Set initial values for the preferences checkboxes based on the model instance's boolean fields
            self.fields['preferences'].initial = [
                pref[0] for pref in self.CHOICES if getattr(instance, pref[0], False)
            ]

    def clean(self):
        cleaned_data = super().clean()
        preferences = cleaned_data.get('preferences')
        if not preferences:
            self.add_error('preferences', 'You must select at least one newsletter preference.')
        return cleaned_data
class OTPForm(forms.Form):
    """
    Form for users to enter the OTP sent to their email.
    """
    otp = forms.CharField(
        label='Enter OTP',
        max_length=4,
        min_length=4,
        widget=forms.TextInput(attrs={'placeholder': 'e.g., 1234'})
    )


class NewsletterForm(forms.ModelForm):
    """
    Form for admins to create or update a newsletter.
    Includes fields for title, message, and preferences for targeting subscribers.
    """

    # Choices for targeting preferences
    CHOICES = [
        ('audit', 'Audit'),
        ('tax', 'Tax'),
        ('consulting', 'Consulting'),
        ('forensic_service', 'Forensic Service'),
        ('managed_service', 'Managed Service'),
        ('technology_solution', 'Technology Solution'),
        ('advisory', 'Advisory'),
    ]

    # A MultipleChoiceField with CheckboxSelectMultiple widget for preferences
    preferences = forms.MultipleChoiceField(
        choices=CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Newsletter
        fields = ['title', 'message', 'audit', 'tax', 'consulting', 'forensic_service', 'managed_service',
                  'technology_solution', 'advisory']

    def __init__(self, *args, **kwargs):
        """
        Initializes the form and sets the initial value of the preferences field
        when editing an existing Newsletter object.
        """
        super().__init__(*args, **kwargs)
        if self.instance:
            # Set initial values for the checkboxes based on the model instance's boolean fields
            self.fields['preferences'].initial = [
                pref[0] for pref in self.CHOICES if getattr(self.instance, pref[0])
            ]