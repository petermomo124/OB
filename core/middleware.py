# ✅ core/middleware.py (The correct and safe way)
from django.utils import timezone
from zoneinfo import ZoneInfo
from django.contrib.auth import get_user_model  # <--- Use this standard import

# Get the custom User model defined in your project
User = get_user_model()  # This is the safe way to reference your model


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            tzname = getattr(request.user, 'timezone', None)

            if tzname and tzname != 'UTC':
                try:
                    timezone.activate(ZoneInfo(tzname))
                except Exception:
                    timezone.deactivate()
            else:
                timezone.deactivate()
        else:
            timezone.deactivate()

        response = self.get_response(request)
        return response