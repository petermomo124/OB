from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
# NEW IMPORT: For generating the list of valid timezones
from zoneinfo import available_timezones


# Function to dynamically generate the list of IANA timezones
def get_timezone_choices():
    """Generates a list of (timezone_name, timezone_name) tuples for choices."""
    return [(tz, tz) for tz in sorted(available_timezones())]





class Office(models.Model):
    office_location = models.CharField(max_length=255)
    office_purpose = models.TextField()
    office_Name = models.CharField(max_length=255, default='Unnamed Office')
    # 🆕 NEW COLUMN: Google Maps URL
    google_map_url = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.office_location

from cloudinary.models import CloudinaryField


# Add this after your existing models

class OfficeDetail(models.Model):
    """
    Additional information for offices including contact details, focus areas,
    community involvement, and principal information.
    """
    office = models.OneToOneField(
        Office,
        on_delete=models.CASCADE,
        related_name='details',
        help_text="The office this information belongs to"
    )

    # Phone numbers
    first_phone_number = models.CharField(max_length=20, blank=True, null=True)
    second_phone_number = models.CharField(max_length=20, blank=True, null=True)

    # Office focus and community involvement
    office_focus = models.TextField(blank=True, null=True, help_text="Main focus areas of the office")
    community_involvement = models.TextField(blank=True, null=True, help_text="Community involvement and initiatives")

    # Principal information
    principal_full_name = models.CharField(max_length=255, blank=True, null=True)
    principal_business_email = models.EmailField(blank=True, null=True)
    principal_business_phone = models.CharField(max_length=20, blank=True, null=True)

    # Principal photo - stored on Cloudinary
    principal_photo = CloudinaryField(
        'principal_photo',
        folder='office_principals/',
        blank=True,
        null=True,
        help_text="Photo of the principal in charge"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Details for {self.office.office_Name}"

    def get_principal_photo_url(self):
        """Return the Cloudinary URL for the principal's photo"""
        if self.principal_photo:
            return self.principal_photo.url
        return None

    class Meta:
        verbose_name = "Office Detail"
        verbose_name_plural = "Office Details"
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        
        # Set is_staff=True if role is 'staff' or 'admin'
        role = extra_fields.get('role', 'client')
        if role in ['staff', 'admin']:
            extra_fields.setdefault('is_staff', True)
            
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_approved', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('client', 'Client'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='client')
    nationality = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)

    # Add the date_joined field here
    date_joined = models.DateTimeField(default=timezone.now)

    # Service booleans
    audit = models.BooleanField(default=False)
    tax = models.BooleanField(default=False)
    consulting = models.BooleanField(default=False)
    forensic_service = models.BooleanField(default=False)
    managed_service = models.BooleanField(default=False)
    technology_solution = models.BooleanField(default=False)
    advisory = models.BooleanField(default=False)

    # Executive team fields
    executive_team = models.BooleanField(default=False)
    executive_position_description = models.TextField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    timezone = models.CharField(
        max_length=50,
        choices=get_timezone_choices,  # Use the function for choices
        default='UTC',  # Default to UTC
        help_text="The IANA timezone for this user (e.g., 'America/New_York')."
    )
    # Company and office impact
    company_impact = models.CharField(max_length=255, blank=True, null=True)
    office = models.ForeignKey(Office, on_delete=models.SET_NULL, blank=True, null=True)
    office_impact = models.CharField(max_length=255, blank=True, null=True)
    field_position = models.CharField(max_length=255, blank=True, null=True)

    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def get_full_name(self):
        """Return the full name of the user"""
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        """Return the short name for the user (first name)"""
        return self.first_name


    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

# core/models.py

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from .models import User  # Import your User model if it's in the same file

class PasswordResetOTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        """Checks if the OTP is still valid (e.g., within 10 minutes of creation)."""
        ten_minutes_ago = timezone.now() - timezone.timedelta(minutes=10)
        return self.created_at >= ten_minutes_ago


# core/models.py
# ... (Your existing imports and models: Office, CustomUserManager, User, PasswordResetOTP) ...
from django.db import models
from django.utils import timezone
from .models import User  # Ensure this import is correct based on your file structure


class TaskStatus(models.TextChoices):
    PENDING = 'Pending', 'Pending'
    IN_PROGRESS = 'In Progress', 'In Progress'
    COMPLETED = 'Completed', 'Completed'
    CANCELED = 'Canceled', 'Canceled'


class Task(models.Model):
    task_title = models.CharField(max_length=255)
    task_purpose = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=TaskStatus.choices,
        default=TaskStatus.PENDING
    )
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(blank=True, null=True)
    completion_date = models.DateTimeField(blank=True, null=True)

    # Relationships
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='created_tasks',
        null=True
    )
    supervisor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='supervised_tasks',
        null=True
    )
    supervisee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='assigned_tasks',
        null=True
    )

    # Text fields
    comments = models.TextField(blank=True, null=True)
    key_note = models.TextField(blank=True, null=True)
    supervisee_feedback = models.TextField(blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.task_title


from django.db import models
from django.utils import timezone
from .models import User
from .models import Task

class TaskFile(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='task_files')
    # Use a CharField to store the full Cloudinary URL
    cloudinary_url = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # Store the Cloudinary-generated public ID to use for secure downloads
    public_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.file_type} for {self.task.task_title}"

    # You might need to add a method to get the file's name
    def get_file_name(self):
        # Extract the filename from the public_id
        return self.public_id.split('/')[-1] if self.public_id else "No Name"


from django.db import models
from cloudinary.models import CloudinaryField


class RegionalLeader(models.Model):
    """Model to store regional leadership information"""
    REGIONS = [
        ('all', 'All Regions'),  # <-- ADD THIS LINE
        ('north_america', 'North America'),
        ('south_america', 'South America'),
        ('europe', 'Europe'),
        ('asia', 'Asia'),
        ('africa', 'Africa'),
        ('middle_east', 'Middle East'),
        ('oceania', 'Oceania'),
    ]

    # Basic Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    region = models.CharField(max_length=50, choices=REGIONS, default='africa')
    region_title = models.CharField(max_length=200, default='Head of Africa Region')

    # Contact Information
    email = models.EmailField()
    linkedin = models.URLField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    # Profile Image (stored in Cloudinary)
    profile_image = CloudinaryField(
        'profile_image',
        folder='regional_leaders/',
        blank=True,
        null=True,
        help_text="Profile photo of the regional leader"
    )

    # Professional Information
    bio = models.TextField(blank=True, null=True, help_text="Professional biography")
    education = models.TextField(blank=True, null=True)
    joining_date = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., March 2018")
    regional_expertise = models.TextField(blank=True, null=True)
    achievements = models.TextField(blank=True, null=True)
    company_impact = models.TextField(blank=True, null=True)
    leadership_style = models.TextField(blank=True, null=True)
    market_insights = models.TextField(blank=True, null=True)

    # Display Order
    display_order = models.IntegerField(default=0,
                                        help_text="Order in which leaders are displayed (lower numbers first)")

    # Status
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'region', 'last_name']
        verbose_name = "Regional Leader"
        verbose_name_plural = "Regional Leaders"

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.get_region_display()}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_profile_image_url(self):
        """Return the Cloudinary URL for the profile image"""
        if self.profile_image:
            return self.profile_image.url
        return 'https://i.pinimg.com/1200x/77/31/a1/7731a10b118bb5b0a0c77bc6f8544bfa.jpg'


# Add this after your RegionalLeader model

class ManagingPartner(models.Model):
    """Model to store managing partners who oversee all regions"""

    # Basic Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    position_title = models.CharField(max_length=200, default='Managing Partner')

    # Contact Information
    email = models.EmailField()
    linkedin = models.URLField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    # Profile Image (stored in Cloudinary)
    profile_image = CloudinaryField(
        'profile_image',
        folder='managing_partners/',
        blank=True,
        null=True,
        help_text="Profile photo of the managing partner"
    )

    # Professional Information
    bio = models.TextField(help_text="Professional biography")
    education = models.TextField()
    joining_date = models.DateField(help_text="Date when they became Managing Partner")
    expertise = models.TextField(help_text="Areas of expertise and specializations")
    achievements = models.TextField(help_text="Notable achievements and accomplishments")
    company_impact = models.TextField(help_text="Impact on the company")
    leadership_philosophy = models.TextField(help_text="Leadership philosophy and style")
    strategic_vision = models.TextField(help_text="Strategic vision for the company")

    # Additional Information
    years_in_role = models.IntegerField(default=0, help_text="Years served as Managing Partner")
    previous_positions = models.TextField(blank=True, null=True, help_text="Previous positions held")
    board_memberships = models.TextField(blank=True, null=True, help_text="Current board memberships")
    awards = models.TextField(blank=True, null=True, help_text="Awards and recognitions")

    # Display Order
    display_order = models.IntegerField(
        default=0,
        help_text="Order in which partners are displayed (lower numbers first)"
    )

    # Status
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'last_name']
        verbose_name = "Managing Partner"
        verbose_name_plural = "Managing Partners"

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.position_title}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_profile_image_url(self):
        """Return the Cloudinary URL for the profile image"""
        if self.profile_image:
            return self.profile_image.url
        return 'https://i.pinimg.com/1200x/77/31/a1/7731a10b118bb5b0a0c77bc6f8544bfa.jpg'

    def get_formatted_joining_date(self):
        """Return formatted joining date"""
        return self.joining_date.strftime("%B %d, %Y")