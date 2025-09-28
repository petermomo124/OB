import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.db.models import Q

from .models import Subscriber, Newsletter
from .forms import SubscriberForm, OTPForm, NewsletterForm
from django.core.mail import send_mail

# Helper function to check if a user is an admin
def is_admin(user):
    return user.is_authenticated and user.is_staff


# --- Subscription Views ---
import random
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

from .models import Subscriber
from .forms import SubscriberForm

import random
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.db.models import Q

from .models import Subscriber, Newsletter
from .forms import SubscriberForm, OTPForm, NewsletterForm

# Set up logger
logger = logging.getLogger(__name__)


# Helper function to check if a user is an admin
def is_admin(user):
    return user.is_authenticated and user.is_staff


def newsletter_subscribe(request):
    """
    Renders the subscription form and handles form submission.
    Creates a new subscriber or updates an existing, unverified one.
    """
    if request.method == 'POST':
        form = SubscriberForm(request.POST)

        if not form.is_valid():
            messages.error(request, "Please correct the errors below.")
            return render(request, 'newsletter/subscribe.html', {'form': form})

        email = form.cleaned_data['email']
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        preferences = form.cleaned_data['preferences']

        try:
            # Attempt to find an existing subscriber
            subscriber = Subscriber.objects.get(email=email)

            # Scenario 1: Subscriber exists and is already verified
            if subscriber.is_verified:
                messages.warning(request, "This email is already subscribed and verified.")
                return redirect('newsletter:subscribe')

            # Scenario 2: Subscriber exists but is unverified - UPDATE EXISTING
            subscriber.first_name = first_name
            subscriber.last_name = last_name

            # Update preferences
            subscriber.audit = 'audit' in preferences
            subscriber.tax = 'tax' in preferences
            subscriber.consulting = 'consulting' in preferences
            subscriber.forensic_service = 'forensic_service' in preferences
            subscriber.managed_service = 'managed_service' in preferences
            subscriber.technology_solution = 'technology_solution' in preferences
            subscriber.advisory = 'advisory' in preferences

            # Generate and save the new OTP
            new_otp = str(random.randint(1000, 9999))
            subscriber.otp = new_otp
            subscriber.save()

            messages.info(request, "New verification code sent to your email. Please check and verify.")

        except Subscriber.DoesNotExist:
            # Scenario 3: New subscriber - create a new instance
            subscriber = Subscriber()
            subscriber.first_name = first_name
            subscriber.last_name = last_name
            subscriber.email = email

            # Set preferences
            subscriber.audit = 'audit' in preferences
            subscriber.tax = 'tax' in preferences
            subscriber.consulting = 'consulting' in preferences
            subscriber.forensic_service = 'forensic_service' in preferences
            subscriber.managed_service = 'managed_service' in preferences
            subscriber.technology_solution = 'technology_solution' in preferences
            subscriber.advisory = 'advisory' in preferences

            # Generate and save the new OTP
            new_otp = str(random.randint(1000, 9999))
            subscriber.otp = new_otp
            subscriber.save()

            messages.success(request,
                             "Subscription request received. Please check your email for the verification code.")

        # Send the OTP email (common for both scenarios)
        try:
            context = {
                'user_name': subscriber.first_name,
                'otp': new_otp,
                'is_otp': True,
            }
            html_content = render_to_string('newsletter/otp_email.html', context)
            email_message = EmailMessage(
                subject='Verify Your Subscription to OB Global Newsletter',
                body=html_content,
                from_email=settings.EMAIL_HOST_USER,
                to=[email],
            )
            email_message.content_subtype = 'html'
            email_message.send()
            logger.info(f"OTP email sent successfully to {email}")

        except Exception as e:
            logger.error(f"Failed to send OTP email to {email}: {str(e)}")
            messages.info(request,
                          "Subscription received! If you don't receive the verification email, please contact support.")

        request.session['temp_subscriber_id'] = subscriber.id
        return redirect('newsletter:verify_otp')

    else:
        form = SubscriberForm()

    return render(request, 'newsletter/subscribe.html', {'form': form})


def verify_otp(request):
    """
    Handles OTP verification for new subscribers.
    No time limit for OTP input - OTP remains valid until used.
    """
    subscriber_id = request.session.get('temp_subscriber_id')
    if not subscriber_id:
        messages.error(request, "Invalid session. Please try subscribing again.")
        return redirect('newsletter:subscribe')

    subscriber = get_object_or_404(Subscriber, id=subscriber_id)

    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            user_otp = form.cleaned_data['otp']

            # Check if OTP matches (no time limit)
            if user_otp == subscriber.otp:
                subscriber.is_verified = True
                subscriber.otp = None  # Clear OTP after successful verification
                subscriber.save()

                # Prepare and send the HTML confirmation email WITH ERROR HANDLING
                try:
                    context = {
                        'user_name': subscriber.first_name,
                        'is_otp': False,
                    }
                    html_content = render_to_string('newsletter/welcome_email.html', context)

                    email_message = EmailMessage(
                        subject='Welcome to the OB Global Newsletter!',
                        body=html_content,
                        from_email=settings.EMAIL_HOST_USER,
                        to=[subscriber.email],
                    )
                    email_message.content_subtype = 'html'

                    # Send email with fail_silently to prevent crashes
                    email_message.send(fail_silently=True)

                    messages.success(request,
                                     "You have been successfully subscribed! A confirmation email has been sent.")

                except Exception as e:
                    # Log the error but continue with successful subscription
                    logger.error(f"Welcome email failed for {subscriber.email}: {str(e)}")
                    messages.success(request, "You have been successfully subscribed! (Welcome email may be delayed)")

                # Clear session and redirect
                del request.session['temp_subscriber_id']
                return redirect('index')
            else:
                messages.error(request, "Invalid OTP. Please try again.")
    else:
        form = OTPForm()

    return render(request, 'newsletter/verify_otp.html', {'form': form, 'email': subscriber.email})

# --- Admin Dashboard Views ---
# (Rest of the views remain unchanged)
# newsletter/views.py

# ... (other imports and views)
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Subscriber, Newsletter
from django.db.models import Count
from django.db.models.functions import Coalesce


# A simple decorator to check for admin status
def is_admin(user):
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """
    Renders the admin dashboard with data for visualizations.
    """
    # Get total counts
    total_subscribers = Subscriber.objects.count()
    verified_subscribers = Subscriber.objects.filter(is_verified=True).count()
    unverified_subscribers = total_subscribers - verified_subscribers

    total_newsletters = Newsletter.objects.count()
    sent_newsletters = Newsletter.objects.filter(sent=True).count()
    unsent_newsletters = total_newsletters - sent_newsletters

    # Get subscriber preference counts
    preference_counts = {
        'audit': Subscriber.objects.filter(audit=True).count(),
        'tax': Subscriber.objects.filter(tax=True).count(),
        'consulting': Subscriber.objects.filter(consulting=True).count(),
        'forensic_service': Subscriber.objects.filter(forensic_service=True).count(),
        'managed_service': Subscriber.objects.filter(managed_service=True).count(),
        'technology_solution': Subscriber.objects.filter(technology_solution=True).count(),
        'advisory': Subscriber.objects.filter(advisory=True).count(),
    }

    context = {
        'total_subscribers': total_subscribers,
        'verified_subscribers': verified_subscribers,
        'unverified_subscribers': unverified_subscribers,
        'total_newsletters': total_newsletters,
        'sent_newsletters': sent_newsletters,
        'unsent_newsletters': unsent_newsletters,
        'preference_labels': list(preference_counts.keys()),
        'preference_data': list(preference_counts.values()),
    }
    return render(request, 'newsletter/admin_dashboard.html', context)

# ... (rest of your views remain unchanged)

@login_required
@user_passes_test(is_admin)
def subscriber_detail(request, pk):
    subscriber = get_object_or_404(Subscriber, pk=pk)
    if request.method == 'POST':
        preferences = request.POST.getlist('preferences')
        form = SubscriberForm(request.POST, instance=subscriber)
        if form.is_valid():
            updated_subscriber = form.save(commit=False)

            updated_subscriber.audit = 'audit' in preferences
            updated_subscriber.tax = 'tax' in preferences
            updated_subscriber.consulting = 'consulting' in preferences
            updated_subscriber.forensic_service = 'forensic_service' in preferences
            updated_subscriber.managed_service = 'managed_service' in preferences
            updated_subscriber.technology_solution = 'technology_solution' in preferences
            updated_subscriber.advisory = 'advisory' in preferences

            updated_subscriber.save()
            messages.success(request, "Subscriber details updated successfully.")
            return redirect('newsletter:admin_dashboard')

    form = SubscriberForm(instance=subscriber)
    form.fields['preferences'].initial = [
        'audit' if subscriber.audit else None,
        'tax' if subscriber.tax else None,
        'consulting' if subscriber.consulting else None,
        'forensic_service' if subscriber.forensic_service else None,
        'managed_service' if subscriber.managed_service else None,
        'technology_solution' if subscriber.technology_solution else None,
        'advisory' if subscriber.advisory else None,
    ]
    return render(request, 'newsletter/subscriber_detail.html', {'form': form, 'subscriber': subscriber})

@login_required
@user_passes_test(is_admin)
def newsletter_list(request):
    """
    Displays a list of all newsletters created by admins.
    """
    newsletters = Newsletter.objects.all().order_by('-created_at')
    context = {
        'newsletters': newsletters,
    }
    return render(request, 'newsletter/newsletter_list.html', context)


@login_required
@user_passes_test(is_admin)
def delete_subscriber(request, pk):
    subscriber = get_object_or_404(Subscriber, pk=pk)
    subscriber.delete()
    messages.success(request, "Subscriber deleted successfully.")
    return redirect('newsletter:admin_dashboard')


# newsletter/views.py

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Newsletter
from .forms import NewsletterForm


@login_required
@user_passes_test(is_admin)
def create_newsletter(request):
    """
    Handles the creation of a new newsletter, manually setting the boolean
    fields for audience preferences based on the form data.
    """
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            # Save the form data but don't commit to the database yet
            new_newsletter = form.save(commit=False)

            # Manually get the list of selected preferences from the form
            preferences = form.cleaned_data.get('preferences', [])

            # Set the corresponding boolean fields on the model
            new_newsletter.audit = 'audit' in preferences
            new_newsletter.tax = 'tax' in preferences
            new_newsletter.consulting = 'consulting' in preferences
            new_newsletter.forensic_service = 'forensic_service' in preferences
            new_newsletter.managed_service = 'managed_service' in preferences
            new_newsletter.technology_solution = 'technology_solution' in preferences
            new_newsletter.advisory = 'advisory' in preferences

            # Now save the newsletter object to the database
            new_newsletter.save()

            messages.success(request, "Newsletter created successfully.")
            return redirect('newsletter:newsletter_list')  # Redirect to the list view
    else:
        form = NewsletterForm()

    return render(request, 'newsletter/create_newsletter.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def newsletter_detail(request, pk):
    newsletter = get_object_or_404(Newsletter, pk=pk)
    if request.method == 'POST':
        form = NewsletterForm(request.POST, instance=newsletter)
        if form.is_valid():
            form.save()
            messages.success(request, "Newsletter updated successfully.")
            return redirect('newsletter:admin_dashboard')

    form = NewsletterForm(instance=newsletter)
    return render(request, 'newsletter/newsletter_detail.html', {'form': form, 'newsletter': newsletter})


@login_required
@user_passes_test(is_admin)
def delete_newsletter(request, pk):
    newsletter = get_object_or_404(Newsletter, pk=pk)
    newsletter.delete()
    messages.success(request, "Newsletter deleted successfully.")
    return redirect('newsletter:admin_dashboard')


# newsletter/views.py
# newsletter/views.py

from django.db import connection  # ⬅️ ADD THIS IMPORT AT THE TOP OF THE FILE


@login_required
@user_passes_test(is_admin)
def send_newsletter(request, pk):
    newsletter = get_object_or_404(Newsletter, pk=pk)

    q_objects = Q()
    if newsletter.audit:
        q_objects |= Q(audit=True)
    if newsletter.tax:
        q_objects |= Q(tax=True)
    if newsletter.consulting:
        q_objects |= Q(consulting=True)
    if newsletter.forensic_service:
        q_objects |= Q(forensic_service=True)
    if newsletter.managed_service:
        q_objects |= Q(managed_service=True)
    if newsletter.technology_solution:
        q_objects |= Q(technology_solution=True)
    if newsletter.advisory:
        q_objects |= Q(advisory=True)

    # 🚨 MODIFICATION 1: Use .values_list() for efficiency
    # This fetches only the 'email' column, reducing query load and memory,
    # and preventing timeouts during the initial database query.
    if not q_objects:
        email_list = list(Subscriber.objects.filter(is_verified=True).values_list('email', flat=True))
    else:
        email_list = list(Subscriber.objects.filter(q_objects, is_verified=True).values_list('email', flat=True))

    if email_list:
        # Prepare the HTML content for the email using a template
        html_content = render_to_string('newsletter/newsletter_email.html', {'newsletter': newsletter})

        # CRITICAL FIX: Close the database connection
        # before the long-running email process begins.
        # This ensures the connection isn't idle long enough to be timed out by the server.
        connection.close()

        # Create an EmailMessage instance
        email_message = EmailMessage(
            subject=newsletter.title,
            body=html_content,
            from_email=settings.EMAIL_HOST_USER,
            # Using a list comprehension to prepare the 'to' field for bulk sending
            to=email_list,
        )

        # Set the content subtype to 'html'
        email_message.content_subtype = 'html'

        # Send the email
        # NOTE: For bulk, use email_message.send(fail_silently=True) for better resilience
        email_message.send()

        # Django will automatically re-open a new connection for the save operation.
        newsletter.sent = True
        newsletter.sent_at = timezone.now()
        newsletter.save()
        messages.success(request, f"Newsletter '{newsletter.title}' sent to {len(email_list)} subscribers.")
    else:
        messages.warning(request, "No subscribers found for the selected preferences.")

    return redirect('newsletter:admin_dashboard')
@login_required
@user_passes_test(is_admin)
def subscriber_detail(request, pk):
    """
    Admin can view and update subscriber details, including preferences.
    """
    subscriber = get_object_or_404(Subscriber, pk=pk)
    if request.method == 'POST':
        preferences = request.POST.getlist('preferences')
        form = SubscriberForm(request.POST, instance=subscriber)
        if form.is_valid():
            updated_subscriber = form.save(commit=False)

            # Manually set preferences based on the form data
            updated_subscriber.audit = 'audit' in preferences
            updated_subscriber.tax = 'tax' in preferences
            updated_subscriber.consulting = 'consulting' in preferences
            updated_subscriber.forensic_service = 'forensic_service' in preferences
            updated_subscriber.managed_service = 'managed_service' in preferences
            updated_subscriber.technology_solution = 'technology_solution' in preferences
            updated_subscriber.advisory = 'advisory' in preferences

            updated_subscriber.save()
            messages.success(request, "Subscriber details updated successfully.")
            return redirect('newsletter:subscriber_list')
    else:
        # Pass the instance to the form to pre-populate fields
        form = SubscriberForm(instance=subscriber)
        # Set the initial values for the preferences field
        form.fields['preferences'].initial = [
            'audit' if subscriber.audit else None,
            'tax' if subscriber.tax else None,
            'consulting' if subscriber.consulting else None,
            'forensic_service' if subscriber.forensic_service else None,
            'managed_service' if subscriber.managed_service else None,
            'technology_solution' if subscriber.technology_solution else None,
            'advisory' if subscriber.advisory else None,
        ]

    return render(request, 'newsletter/subscriber_detail.html', {'form': form, 'subscriber': subscriber})

@login_required
@user_passes_test(is_admin)
def subscriber_list(request):
    """
    Displays a list of all newsletter subscribers in a table.
    """
    subscribers = Subscriber.objects.all().order_by('-created_at')
    context = {
        'subscribers': subscribers,
    }
    return render(request, 'newsletter/subscriber_list.html', context)


# newsletter/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .models import Subscriber
from .forms import SubscriberForm
from django.contrib import messages

# newsletter/views.py (CORRECTED update_subscriber view)

from django.shortcuts import render, redirect, get_object_or_404
from .models import Subscriber
from .forms import SubscriberForm
from django.contrib import messages


def update_subscriber(request, pk):
    subscriber = get_object_or_404(Subscriber, pk=pk)

    # NOTE: Since SubscriberForm is a forms.Form, the 'instance=subscriber'
    # must be handled by the form's __init__ (which you've done correctly).
    if request.method == 'POST':
        form = SubscriberForm(request.POST, instance=subscriber)

        if form.is_valid():
            cleaned_data = form.cleaned_data

            # 1. Update the simple fields manually
            subscriber.first_name = cleaned_data['first_name']
            subscriber.last_name = cleaned_data['last_name']
            subscriber.email = cleaned_data['email']

            # 2. Update the boolean preference fields manually
            preferences = cleaned_data.get('preferences', [])

            subscriber.audit = 'audit' in preferences
            subscriber.tax = 'tax' in preferences
            subscriber.consulting = 'consulting' in preferences
            subscriber.forensic_service = 'forensic_service' in preferences
            subscriber.managed_service = 'managed_service' in preferences
            subscriber.technology_solution = 'technology_solution' in preferences
            subscriber.advisory = 'advisory' in preferences

            # 3. Save the model instance to the database
            subscriber.save()  # ✅ Correct: save on the model instance

            messages.success(request, 'Subscriber updated successfully.')
            return redirect('newsletter:subscriber_detail', pk=subscriber.pk)
    else:
        # Initializing the form using 'instance' to pre-populate is fine
        # because the form's __init__ handles it.
        form = SubscriberForm(instance=subscriber)

    context = {
        'form': form,
        'subscriber': subscriber,
    }
    return render(request, 'newsletter/update_subscriber.html', context)

# newsletter/views.py
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Newsletter
from .forms import NewsletterForm

# newsletter/views.py

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Newsletter
from .forms import NewsletterForm
from django.utils import timezone


@login_required
@user_passes_test(is_admin)
def update_newsletter(request, pk):
    """
    View to update an existing newsletter.

    This function prevents updating a newsletter that has already been sent
    and resets the sent status if an update is made. It manually handles
    the boolean fields for targeting preferences from the form data.
    """
    newsletter = get_object_or_404(Newsletter, pk=pk)

    if request.method == 'POST':
        form = NewsletterForm(request.POST, instance=newsletter)
        if form.is_valid():
            updated_newsletter = form.save(commit=False)

            # Manually handle the boolean fields for targeting preferences
            preferences = form.cleaned_data.get('preferences', [])
            updated_newsletter.audit = 'audit' in preferences
            updated_newsletter.tax = 'tax' in preferences
            updated_newsletter.consulting = 'consulting' in preferences
            updated_newsletter.forensic_service = 'forensic_service' in preferences
            updated_newsletter.managed_service = 'managed_service' in preferences
            updated_newsletter.technology_solution = 'technology_solution' in preferences
            updated_newsletter.advisory = 'advisory' in preferences

            # Reset sent status and date if the newsletter was previously sent.
            # This allows it to be edited and resent.
            if newsletter.sent:
                updated_newsletter.sent = False
                updated_newsletter.sent_at = None
                messages.info(request,
                              "This newsletter was previously sent. Its status has been reset to 'Draft' for resending.")

            updated_newsletter.save()

            messages.success(request, "Newsletter updated successfully.")
            return redirect('newsletter:newsletter_detail', pk=updated_newsletter.pk)
    else:
        # Pre-populate the form with existing data
        form = NewsletterForm(instance=newsletter)

        # Set the initial values for the preferences field based on boolean fields
        selected_preferences = []
        if newsletter.audit: selected_preferences.append('audit')
        if newsletter.tax: selected_preferences.append('tax')
        if newsletter.consulting: selected_preferences.append('consulting')
        if newsletter.forensic_service: selected_preferences.append('forensic_service')
        if newsletter.managed_service: selected_preferences.append('managed_service')
        if newsletter.technology_solution: selected_preferences.append('technology_solution')
        if newsletter.advisory: selected_preferences.append('advisory')
        form.fields['preferences'].initial = selected_preferences

    return render(request, 'newsletter/update_newsletter.html', {'form': form, 'newsletter': newsletter})
