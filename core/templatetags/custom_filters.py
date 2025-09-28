from django import template

# 1. ONLY DEFINE THE REGISTER OBJECT ONCE
register = template.Library()

# 2. First Filter: filename_from_public_id (now using the logic you defined)
@register.filter
def filename_from_public_id(public_id):
    """
    Extracts the filename from a Cloudinary public_id.
    e.g., 'tasks/30001/example_file.pdf' -> 'example_file.pdf'
    """
    if not public_id:
        return ''
    return public_id.split('/')[-1]

# 3. Second Filter: replace
@register.filter
def replace(value, arg):
    """
    Replaces all occurrences of a substring with another string.
    Usage: {{ value|replace:"old,new" }}
    """
    try:
        if not value:
            return value
        # This handles the template syntax fix from before: |replace:'old,new'
        parts = arg.split(',')
        old = parts[0]
        new = parts[1] if len(parts) > 1 else ''
        return value.replace(old, new)
    except Exception:
        # Return original value on error
        return value