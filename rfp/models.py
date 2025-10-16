from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

# Get the custom User model defined in settings.AUTH_USER_MODEL
User = get_user_model()


class RFPReferral(models.Model):
    """Stores the main details of the Request for Proposal referral."""

    # RFP Information Fields
    proposal_title = models.CharField(max_length=255)
    organization = models.CharField(max_length=255)
    proposal_deadline = models.DateTimeField()

    # Location Fields
    city = models.CharField(max_length=100)
    state_province = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)

    # Client/User Association
    # Foreign Key to the User model
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='rfp_referrals',
        help_text="The client/user who submitted the proposal."
    )

    # Status and Timestamps
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('in_review', 'In Review'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='submitted'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"RFP: {self.proposal_title} by {self.client.email}"

    class Meta:
        ordering = ['-created_at']


class RFPFile(models.Model):
    """Stores file attachments associated with an RFP referral."""

    referral = models.ForeignKey(
        RFPReferral,
        on_delete=models.CASCADE,
        related_name='files'
    )

    # File details from Cloudinary upload
    cloudinary_url = models.URLField(
        max_length=500,
        help_text="Public URL of the file stored in Cloudinary."
    )
    public_id = models.CharField(
        max_length=255,
        help_text="The Cloudinary public ID for deletion and management."
    )

    # File type tracking
    file_type = models.CharField(
        max_length=10,
        choices=[('docx', 'DOCX'), ('html', 'HTML')],
        default='docx',
        help_text="File format type"
    )

    # Document editing tracking
    is_being_edited = models.BooleanField(default=False)
    last_edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='edited_rfp_files'
    )
    last_edited_at = models.DateTimeField(null=True, blank=True)

    # Tracking
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_rfp_files'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File for RFP {self.referral.id}: {self.public_id.split('/')[-1]}"

    def get_file_name(self):
        """Extract filename from public_id"""
        return self.public_id.split('/')[-1] if self.public_id else "Unknown"

class OriginalDocxFile(models.Model):
    rfp_file = models.OneToOneField(
        RFPFile,
        on_delete=models.CASCADE,
        related_name='original_docx',
        db_index=True
    )
    cloudinary_url = models.URLField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['rfp_file', 'created_at']),
        ]


