from django import forms
from .models import Subscriber, Newsletter


class SubscriberForm(forms.ModelForm):
    """
    Form for new users to subscribe to the newsletter.
    Includes fields for personal information and preferences.
    """

    # Define email as a separate field to control its validation.
    # The 'unique=True' check from the model will be handled manually in the view.
    email = forms.EmailField(
        label='Email',
        max_length=254,
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

    # A MultipleChoiceField with CheckboxSelectMultiple widget for preferences
    preferences = forms.MultipleChoiceField(
        choices=CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Subscriber
        # Include all fields from the model, including the individual boolean preference fields
        fields = ['first_name', 'last_name', 'email', 'audit', 'tax', 'consulting', 'forensic_service',
                  'managed_service', 'technology_solution', 'advisory']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set all fields except preferences to be required
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True

        # Set the initial value for the email field if an instance is provided
        if self.instance and self.instance.email:
            self.fields['email'].initial = self.instance.email

        # Set the initial values for the custom preferences field based on the model instance's boolean fields
        if self.instance.pk:
            initial_preferences = []
            for choice_value, _ in self.CHOICES:
                if getattr(self.instance, choice_value):
                    initial_preferences.append(choice_value)
            self.fields['preferences'].initial = initial_preferences

    def clean(self):
        cleaned_data = super().clean()

        # Check if at least one preference is selected
        preferences = cleaned_data.get('preferences')
        if not preferences:
            self.add_error('preferences', 'You must select at least one newsletter preference.')

        return cleaned_data

    def save(self, commit=True):
        # Save the basic form data first, but don't commit yet
        subscriber = super().save(commit=False)

        # Get the selected preferences from the form's cleaned data
        selected_preferences = self.cleaned_data.get('preferences', [])

        # Loop through all possible preference choices and update the boolean fields on the subscriber object
        for choice_value, _ in self.CHOICES:
            # The boolean field is set to True if its value is in the selected preferences, otherwise False
            setattr(subscriber, choice_value, choice_value in selected_preferences)

        # Finally, save the subscriber object with the updated preferences
        if commit:
            subscriber.save()
        return subscriber

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