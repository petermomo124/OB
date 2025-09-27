import re
from django import template

# Register the template library
register = template.Library()


@register.filter
def cut_audio_tag(value):
    """
    Removes the [AUDIO_URL:...] tag from a string.

    This is necessary for the chatbot template to display only the text part
    of a message when the audio player is also being rendered.

    Example:
    Input: "Here is your response. [AUDIO_URL:/media/audio/123.mp3]"
    Output: "Here is your response."
    """
    # Regular expression to find and remove the full [AUDIO_URL:...] tag
    # r'\[AUDIO_URL:.*?\]' matches the literal brackets and everything between them non-greedily.
    cleaned_value = re.sub(r'\[AUDIO_URL:.*?\]', '', value).strip()
    return cleaned_value
