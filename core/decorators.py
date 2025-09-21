# core/decorators.py

from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def admin_required(view_func):
    """
    Decorator to ensure the user is logged in and has the 'admin' role.
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "You must be logged in to view this page.")
            return redirect('login')  # or wherever your login URL is named

        if request.user.role != 'admin':
            messages.error(request, "You do not have permission to access this page.")
            return redirect('dashboard')  # or another appropriate page

        return view_func(request, *args, **kwargs)

    return _wrapped_view