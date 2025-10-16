from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


# Assuming send_rfp_submission_email exists here for context

def send_rfp_update_notification(referral, user_who_made_change):
    """
    Sends a notification email when an RFP is updated.

    If client made the change -> notify Admin.
    If Admin made the change -> notify Client.
    """

    # Determine roles and recipients
    is_client_update = (hasattr(user_who_made_change, 'role') and user_who_made_change.role == 'client')

    if is_client_update:
        # Client updated the RFP, notify the primary Admin email
        recipient_email = settings.ADMIN_EMAIL_FOR_NOTIFICATIONS  # Ensure this setting is defined
        subject = f"ACTION REQUIRED: Client Updated RFP - {referral.proposal_title}"
        notification_type = "Client Update"
        # Instructions for Admin
        instructions = "A client has made changes to the RFP below. Please review the details in the portal."
    else:
        # Admin updated the RFP, notify the Client
        recipient_email = referral.client.email
        subject = f"UPDATE: Your RFP Status Has Been Changed - {referral.proposal_title}"
        notification_type = "Admin Update"
        # Instructions for Client
        instructions = f"An administrator has made an update to your RFP (Status: {referral.status}). Please log into your client portal for details."

    # Render the HTML content using the new template
    html_content = render_to_string('emails/rfp_update_notification.html', {
        'referral': referral,
        'notification_type': notification_type,
        'instructions': instructions,
        'recipient_is_admin': not is_client_update,  # True if sending to client, False if sending to admin
        'user_who_made_change': user_who_made_change.email
    })

    try:
        send_mail(
            subject=subject,
            message=subject,  # Fallback plain text version (required)
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            html_message=html_content,
            fail_silently=False,
        )
        print(f"Update notification sent successfully to {recipient_email}")
    except Exception as e:
        # In a real application, you would log this error
        print(f"Error sending update email to {recipient_email}: {e}")
