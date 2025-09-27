from django.contrib import admin
from .models import ChatHistory


@admin.register(ChatHistory)
class ChatHistoryAdmin(admin.ModelAdmin):
    """
    Customizes the display and interaction for the ChatHistory model in the Django Admin.
    """

    # Fields to display in the list view
    list_display = ('user', 'timestamp', 'is_from_bot', 'message_snippet')

    # Fields to filter the list view by
    list_filter = ('is_from_bot', 'timestamp', 'user')

    # Fields to search across
    search_fields = ('user__email', 'message')

    # Fields that users cannot edit after creation
    readonly_fields = ('user', 'message', 'is_from_bot', 'timestamp')

    # A custom method to show only the first part of the message in the list display
    def message_snippet(self, obj):
        """Returns a truncated version of the message."""
        max_length = 100
        if len(obj.message) > max_length:
            return obj.message[:max_length] + '...'
        return obj.message

    # Set a custom header for the snippet column
    message_snippet.short_description = 'Message Snippet'
