from django import template
from django.contrib.auth import get_user_model

register = template.Library()

@register.filter(name='display_name')
def display_name(user):
    """
    Returns the best available display name for a user in this order:
    1. Full name (first_name + last_name)
    2. First name
    3. Email (without the domain part if possible)
    4. Username
    5. 'User' as fallback
    """
    if not user or not hasattr(user, 'is_authenticated') or not user.is_authenticated:
        return 'Guest'
    
    # Try to get full name
    if hasattr(user, 'get_full_name') and user.get_full_name().strip():
        return user.get_full_name().strip()
    
    # Try first name
    if hasattr(user, 'first_name') and user.first_name:
        return user.first_name.strip()
    
    # Try email (without domain if possible)
    if hasattr(user, 'email') and user.email:
        return user.email.split('@')[0]
    
    # Try username
    if hasattr(user, 'get_username'):
        return user.get_username()
    elif hasattr(user, 'username'):
        return user.username
    
    return 'User'
