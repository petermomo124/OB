from django import forms
from .models import Office

class OfficeForm(forms.ModelForm):
    class Meta:
        model = Office
        fields = ['office_Name', 'office_location', 'office_purpose', 'google_map_url']
        widgets = {
            'office_purpose': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'office_Name': 'Office Name',
            'office_location': 'Location Address',
            'office_purpose': 'Purpose/Description',
            'google_map_url': 'Google Maps URL (Embed Link)',
        }