from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


class Office(models.Model):
    office_location = models.CharField(max_length=255)
    office_purpose = models.TextField()
    # Add the new column here
    office_Name = models.CharField(max_length=255, default='Unnamed Office')

    def __str__(self):
        return self.office_location


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
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

    # Company and office impact
    company_impact = models.CharField(max_length=255, blank=True, null=True)
    office = models.ForeignKey(Office, on_delete=models.SET_NULL, blank=True, null=True)
    office_impact = models.CharField(max_length=255, blank=True, null=True)
    field_position = models.CharField(max_length=255, blank=True, null=True)

    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

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