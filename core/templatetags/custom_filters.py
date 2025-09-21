from django import template

register = template.Library()

@register.filter
def filename_from_public_id(public_id):
    """
    Extracts the filename from a Cloudinary public_id.
    e.g., 'tasks/30001/example_file.pdf' -> 'example_file.pdf'
    """
    return public_id.split('/')[-1]