# In your manage.py file, near the top
import sys

# Add this line to remove the problematic path
try:
    sys.path.remove('<fstring>')
except ValueError:
    pass