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


from django import forms
from .models import Office, OfficeDetail
from cloudinary.forms import CloudinaryFileField

from django import forms
from django.core.exceptions import ValidationError
from .models import OfficeDetail
from cloudinary.forms import CloudinaryFileField


class OfficeDetailForm(forms.ModelForm):
    # Custom field for Cloudinary upload with specific options
    principal_photo = CloudinaryFileField(
        required=True,  # Changed to required
        options={
            'folder': 'office_principals/',
            'resource_type': 'image',
            'transformation': [
                {'width': 400, 'height': 400, 'crop': 'fill'},
                {'quality': 'auto'}
            ]
        }
    )

    class Meta:
        model = OfficeDetail
        fields = [
            'first_phone_number',
            'second_phone_number',
            'office_focus',
            'community_involvement',
            'principal_full_name',
            'principal_business_email',
            'principal_business_phone',
            'principal_photo'
        ]
        widgets = {
            'first_phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1 (555) 123-4567',
                'required': 'required'
            }),
            'second_phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1 (555) 987-6543',
                'required': 'required'
            }),
            'office_focus': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the main focus areas of this office...',
                'required': 'required'
            }),
            'community_involvement': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe community involvement and initiatives...',
                'required': 'required'
            }),
            'principal_full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full name of principal in charge',
                'required': 'required'
            }),
            'principal_business_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'business.email@company.com',
                'required': 'required'
            }),
            'principal_business_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1 (555) 555-5555',
                'required': 'required'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields required
        for field_name, field in self.fields.items():
            if field_name != 'principal_photo':  # principal_photo already set to required=True
                field.required = True
                if hasattr(field.widget, 'attrs'):
                    field.widget.attrs['required'] = 'required'

    def clean(self):
        cleaned_data = super().clean()

        # Get all phone numbers from the form
        first_phone = cleaned_data.get('first_phone_number')
        second_phone = cleaned_data.get('second_phone_number')
        principal_phone = cleaned_data.get('principal_business_phone')

        # Normalize phone numbers (remove spaces, dashes, parentheses for comparison)
        def normalize_phone(phone):
            if not phone:
                return None
            # Remove common separators and spaces
            import re
            return re.sub(r'[\s\+\-\(\)]', '', phone)

        normalized_first = normalize_phone(first_phone)
        normalized_second = normalize_phone(second_phone)
        normalized_principal = normalize_phone(principal_phone)

        # Create a list of normalized phone numbers for comparison
        phone_numbers = []
        if normalized_first:
            phone_numbers.append(('first_phone_number', normalized_first, first_phone))
        if normalized_second:
            phone_numbers.append(('second_phone_number', normalized_second, second_phone))
        if normalized_principal:
            phone_numbers.append(('principal_business_phone', normalized_principal, principal_phone))

        # Check for duplicates
        seen = {}
        duplicates = []

        for field_name, normalized, original in phone_numbers:
            if normalized in seen:
                duplicates.append((field_name, original, seen[normalized]))
            else:
                seen[normalized] = field_name

        # If duplicates found, raise validation error
        if duplicates:
            error_messages = []
            for dup_field, dup_value, existing_field in duplicates:
                error_messages.append(
                    f"'{dup_value}' in '{self.fields[dup_field].label}' "
                    f"is the same as '{existing_field}' field"
                )

            # Add errors to all duplicate fields
            for dup_field, _, _ in duplicates:
                self.add_error(dup_field, ValidationError(
                    "This phone number must be different from other phone numbers in the form.",
                    code='duplicate_phone'
                ))

            # Also add a non-field error
            raise ValidationError(
                "All phone numbers must be unique. Please use different phone numbers for each field."
            )

        # Additional validation: Check that first and second phone numbers are different
        if normalized_first and normalized_second and normalized_first == normalized_second:
            self.add_error('first_phone_number', ValidationError(
                "First phone number cannot be the same as second phone number.",
                code='duplicate_office_phones'
            ))
            self.add_error('second_phone_number', ValidationError(
                "Second phone number cannot be the same as first phone number.",
                code='duplicate_office_phones'
            ))

        # Check that principal phone is different from office phones
        if normalized_principal:
            if normalized_first and normalized_principal == normalized_first:
                self.add_error('principal_business_phone', ValidationError(
                    "Principal phone number cannot be the same as first office phone number.",
                    code='duplicate_principal_office'
                ))
            if normalized_second and normalized_principal == normalized_second:
                self.add_error('principal_business_phone', ValidationError(
                    "Principal phone number cannot be the same as second office phone number.",
                    code='duplicate_principal_office'
                ))

        return cleaned_data

    def clean_first_phone_number(self):
        first_phone = self.cleaned_data.get('first_phone_number')
        if first_phone:
            # Basic phone number validation
            import re
            # Remove all non-digit characters except leading +
            digits_only = re.sub(r'[^\d\+]', '', first_phone)
            if len(digits_only.replace('+', '')) < 10:
                raise ValidationError(
                    "Phone number must contain at least 10 digits.",
                    code='invalid_phone'
                )
        return first_phone

    def clean_second_phone_number(self):
        second_phone = self.cleaned_data.get('second_phone_number')
        if second_phone:
            # Basic phone number validation
            import re
            digits_only = re.sub(r'[^\d\+]', '', second_phone)
            if len(digits_only.replace('+', '')) < 10:
                raise ValidationError(
                    "Phone number must contain at least 10 digits.",
                    code='invalid_phone'
                )
        return second_phone

    def clean_principal_business_phone(self):
        principal_phone = self.cleaned_data.get('principal_business_phone')
        if principal_phone:
            # Basic phone number validation
            import re
            digits_only = re.sub(r'[^\d\+]', '', principal_phone)
            if len(digits_only.replace('+', '')) < 10:
                raise ValidationError(
                    "Phone number must contain at least 10 digits.",
                    code='invalid_phone'
                )
        return principal_phone

    def clean_principal_full_name(self):
        full_name = self.cleaned_data.get('principal_full_name')
        if full_name:
            # Check if it contains at least first and last name
            name_parts = full_name.strip().split()
            if len(name_parts) < 2:
                raise ValidationError(
                    "Please enter both first and last name of the principal.",
                    code='incomplete_name'
                )
        return full_name


from django import forms
from .models import RegionalLeader, ManagingPartner
from cloudinary.forms import CloudinaryFileField
from django import forms
from .models import RegionalLeader, ManagingPartner
from cloudinary.forms import CloudinaryFileField
import json


class BaseLeaderForm(forms.ModelForm):
    """Base form with common fields for both leader types"""
    leader_type = forms.ChoiceField(
        choices=[
            ('regional_leader', 'Regional Leader'),
            ('managing_partner', 'Managing Partner')
        ],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_leader_type'
        }),
        required=True
    )

    profile_image = CloudinaryFileField(
        required=False,
        options={
            'folder': 'regional_leaders/',
            'resource_type': 'image',
            'transformation': [
                {'width': 400, 'height': 400, 'crop': 'fill'},
                {'quality': 'auto'}
            ]
        }
    )

    class Meta:
        abstract = True
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter first name',
                'required': True,
                'id': 'id_first_name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter last name',
                'required': True,
                'id': 'id_last_name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address',
                'required': True,
                'id': 'id_email'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number',
                'required': True,
                'id': 'id_phone'
            }),
            'linkedin': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://linkedin.com/in/username',
                'required': True,
                'id': 'id_linkedin'
            }),
            'region_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Regional Director for Africa or Managing Partner',
                'required': True,
                'id': 'id_region_title'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Enter professional biography',
                'required': True,
                'id': 'id_bio'
            }),
            'education': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter education background',
                'required': True,
                'id': 'id_education'
            }),
            'achievements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter notable achievements',
                'required': True,
                'id': 'id_achievements'
            }),
            'company_impact': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe impact on company',
                'required': True,
                'id': 'id_company_impact'
            }),
            'joining_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control date-picker',
                'required': True,
                'id': 'id_joining_date'
            }),
            'display_order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100,
                'required': True,
                'id': 'id_display_order'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'toggle-switch',
                'id': 'id_is_active'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial for leader_type based on instance
        if self.instance and hasattr(self.instance, 'pk') and self.instance.pk:
            if hasattr(self.instance, 'leader_type'):
                self.fields['leader_type'].initial = self.instance.leader_type
            elif isinstance(self.instance, ManagingPartner):
                self.fields['leader_type'].initial = 'managing_partner'
            else:
                self.fields['leader_type'].initial = 'regional_leader'

        # Set required attribute for all fields except profile_image and leader_type
        for field_name, field in self.fields.items():
            if field_name not in ['profile_image', 'leader_type']:
                field.widget.attrs['required'] = 'required'


class RegionalLeaderForm(BaseLeaderForm):
    """Form for Regional Leader model"""

    region = forms.ChoiceField(
        choices=[],  # Empty choices, will be populated in __init__
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_region',
            'required': True
        }),
        required=True
    )

    regional_expertise = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Enter regional expertise',
            'required': True,
            'id': 'id_regional_expertise'
        })
    )

    leadership_style = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Describe leadership style',
            'required': True,
            'id': 'id_leadership_style'
        })
    )

    market_insights = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Share market insights',
            'required': True,
            'id': 'id_market_insights'
        })
    )

    class Meta(BaseLeaderForm.Meta):
        model = RegionalLeader
        fields = [
            'leader_type',
            'first_name', 'last_name',
            'region', 'region_title',
            'email', 'phone', 'linkedin',
            'profile_image',
            'bio', 'education', 'regional_expertise', 'achievements',
            'company_impact', 'leadership_style', 'market_insights',
            'joining_date', 'display_order', 'is_active'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial leader_type for new instances
        if not self.instance or not self.instance.pk:
            self.fields['leader_type'].initial = 'regional_leader'

        # Get region choices from model - use REGIONS, not REGION_CHOICES
        region_choices = list(RegionalLeader.REGIONS)

        # Add empty option at the beginning
        region_choices = [('', 'Select a region')] + region_choices

        # Update region field choices
        self.fields['region'].choices = region_choices

        # Set initial region value if editing
        if self.instance and self.instance.pk:
            self.fields['region'].initial = self.instance.region


class ManagingPartnerForm(BaseLeaderForm):
    """Form for Managing Partner model"""

    region = forms.ChoiceField(
        choices=[],  # Empty choices, will be populated in __init__
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_region',
            'required': False
        }),
        required=False
    )

    expertise = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Enter professional expertise',
            'required': True,
            'id': 'id_expertise'
        })
    )

    leadership_philosophy = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Describe leadership philosophy',
            'required': True,
            'id': 'id_leadership_philosophy'
        })
    )

    strategic_vision = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Share strategic vision',
            'required': True,
            'id': 'id_strategic_vision'
        })
    )

    # Optional fields for managing partners
    previous_positions = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'List previous positions',
            'required': False,
            'id': 'id_previous_positions'
        }),
        required=False
    )

    board_memberships = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'List board memberships',
            'required': False,
            'id': 'id_board_memberships'
        }),
        required=False
    )

    awards = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'List awards and recognitions',
            'required': False,
            'id': 'id_awards'
        }),
        required=False
    )

    # Note: position_title field is used instead of region_title for managing partners
    position_title = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Managing Partner, CEO, etc.',
            'required': True,
            'id': 'id_position_title'
        })
    )

    # Note: years_in_role field is specific to managing partners
    years_in_role = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 0,
            'max': 50,
            'required': True,
            'id': 'id_years_in_role'
        }),
        initial=0
    )

    class Meta(BaseLeaderForm.Meta):
        model = ManagingPartner
        fields = [
            'leader_type',
            'first_name', 'last_name',
            'position_title',
            'email', 'phone', 'linkedin',
            'profile_image',
            'bio', 'education', 'expertise', 'achievements',
            'company_impact', 'leadership_philosophy', 'strategic_vision',
            'previous_positions', 'board_memberships', 'awards',
            'years_in_role',
            'joining_date', 'display_order', 'is_active'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial leader_type for new instances
        if not self.instance or not self.instance.pk:
            self.fields['leader_type'].initial = 'managing_partner'

        # Get region choices from RegionalLeader model - use REGIONS
        region_choices = list(RegionalLeader.REGIONS)

        # Add empty option at the beginning
        region_choices = [('', 'Select a region')] + region_choices

        # Update region field choices
        self.fields['region'].choices = region_choices

        # For managing partners, set region to 'all' by default
        if not self.instance or not self.instance.pk:
            self.fields['region'].initial = 'all'
        elif self.instance and self.instance.pk:
            self.fields['region'].initial = getattr(self.instance, 'region', 'all')

    def clean(self):
        cleaned_data = super().clean()

        # For managing partners, set region to 'all' if not specified
        region = cleaned_data.get('region')
        if not region:
            cleaned_data['region'] = 'all'

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Handle region field for managing partners
        region = self.cleaned_data.get('region', 'all')
        instance.region = region

        if commit:
            instance.save()
            self.save_m2m()

        return instance