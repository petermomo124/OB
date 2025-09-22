# newsletter/models.py

from django.db import models
from django.utils import timezone


class Subscriber(models.Model):
    """
    Stores a subscriber's information and newsletter preferences.
    """
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=4, blank=True, null=True)

    # Newsletter preferences (boolean fields)
    audit = models.BooleanField(default=False)
    tax = models.BooleanField(default=False)
    consulting = models.BooleanField(default=False)
    forensic_service = models.BooleanField(default=False)
    managed_service = models.BooleanField(default=False)
    technology_solution = models.BooleanField(default=False)
    advisory = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email


from django.db import models

class Newsletter(models.Model):
    """
    Stores newsletter content created by the admin.
    """
    title = models.CharField(max_length=255)
    message = models.TextField()

    # Newsletter preferences (boolean fields for targeting)
    audit = models.BooleanField(default=False)
    tax = models.BooleanField(default=False)
    consulting = models.BooleanField(default=False)
    forensic_service = models.BooleanField(default=False)
    managed_service = models.BooleanField(default=False)
    technology_solution = models.BooleanField(default=False)
    advisory = models.BooleanField(default=False)

    sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_preferences(self):
        """
        Returns a list of selected preferences as human-readable strings.
        """
        preferences = []
        if self.audit:
            preferences.append('Audit')
        if self.tax:
            preferences.append('Tax')
        if self.consulting:
            preferences.append('Consulting')
        if self.forensic_service:
            preferences.append('Forensic Service')
        if self.managed_service:
            preferences.append('Managed Service')
        if self.technology_solution:
            preferences.append('Technology Solution')
        if self.advisory:
            preferences.append('Advisory')
        return preferences

    def __str__(self):
        return self.title