from django.db import models
from django.conf import settings
from core.models import User # Import the custom User model

class ChatHistory(models.Model):
    # Use settings.AUTH_USER_MODEL for best practice, or directly core.User
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    is_from_bot = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Chat History"
        ordering = ['timestamp']

    def __str__(self):
        role = "Bot" if self.is_from_bot else self.user.get_full_name()
        return f"{role}: {self.message[:50]}"