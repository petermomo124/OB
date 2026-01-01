from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView

# Service data
SERVICES = {
    'audit': {
        'name': 'Audit Services',
        'tagline': 'Comprehensive audit solutions for your business',
        'photos': [
            'images/services/audit1.jpg',
            'images/services/audit2.jpg',
            'images/services/audit3.jpg'
        ],
        'benefits': [
            {
                'title': 'Risk Assessment',
                'description': 'Identify and mitigate financial and operational risks.'
            },
            {
                'title': 'Compliance',
                'description': 'Ensure compliance with relevant laws and regulations.'
            },
            {
                'title': 'Process Improvement',
                'description': 'Enhance operational efficiency and effectiveness.'
            },
            {
                'title': 'Financial Accuracy',
                'description': 'Ensure the accuracy and reliability of financial statements.'
            },
            {
                'title': 'Fraud Detection',
                'description': 'Identify and prevent potential fraudulent activities.'
            },
            {
                'title': 'Strategic Insights',
                'description': 'Gain valuable insights for better decision-making.'
            }
        ],
        'how_we_help': [
            {
                'title': 'Initial Consultation',
                'description': 'We start by understanding your business and specific audit needs.'
            },
            {
                'title': 'Planning',
                'description': 'Develop a customized audit plan tailored to your organization.'
            },
            {
                'title': 'Fieldwork',
                'description': 'Our team conducts thorough testing and analysis of your financial data.'
            },
            {
                'title': 'Reporting',
                'description': 'Receive a detailed report with findings and recommendations.'
            },
            {
                'title': 'Follow-up',
                'description': 'We provide ongoing support and follow-up as needed.'
            }
        ],
        'team_members': [
            {
                'name': 'John Smith',
                'position': 'Audit Partner',
                'photo': 'images/team/john-smith.jpg',
                'bio': '20+ years of experience in audit and assurance.'
            },
            {
                'name': 'Sarah Johnson',
                'position': 'Senior Manager',
                'photo': 'images/team/sarah-johnson.jpg',
                'bio': 'Specializes in financial services audits.'
            },
            {
                'name': 'Michael Chen',
                'position': 'Manager',
                'photo': 'images/team/michael-chen.jpg',
                'bio': 'Expert in internal controls and compliance.'
            },
            {
                'name': 'Emily Davis',
                'position': 'Senior Associate',
                'photo': 'images/team/emily-davis.jpg',
                'bio': 'Focuses on technology and risk assessment.'
            }
        ]
    },
    # Add other services here following the same structure
}
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from .models import User  # Import your custom User model
from django.shortcuts import render
from .models import User, Office
def index(request):
    # Get executive team members (users with executive_team=True)
    executives = User.objects.filter(
        executive_team=True,
        is_active=True
    ).select_related('office')

    # Get all offices
    offices = Office.objects.all()

    context = {
        'executives': executives,
        'offices': offices,
    }

    return render(request, 'index.html', context)
def service_detail(request, service_slug):
    service = SERVICES.get(service_slug)
    if not service:
        # Handle 404 if service not found
        from django.http import Http404
        raise Http404("Service not found")

    # Add related services (all other services)
    related_services = [
        {'name': 'Tax Services', 'url': '/services/tax'},
        {'name': 'Consulting', 'url': '/services/consulting'},
        {'name': 'Advisory', 'url': '/services/advisory'},
        {'name': 'Technology Solutions', 'url': '/services/technology'},
        {'name': 'Managed Services', 'url': '/services/managed'}
    ]

    context = {
        'service_name': service['name'],
        'service_tagline': service['tagline'],
        'service_photos': service['photos'],
        'benefits': service['benefits'],
        'how_we_help': service['how_we_help'],
        'team_members': service['team_members'],
        'related_services': related_services
    }

    return render(request, f'services/{service_slug}.html', context)

# Industry Data
INDUSTRIES = {
    'financial-services': {
        'name': 'Financial Services',
        'tagline': 'Tailored solutions for banks, insurance companies, and financial institutions',
        'stats': [
            {'value': '15+', 'label': 'Years of Experience'},
            {'value': '200+', 'label': 'Financial Institutions Served'},
            {'value': '95%', 'label': 'Client Retention Rate'}
        ],
        'team_members': [
            {
                'name': 'John Doe',
                'position': 'Financial Services Lead',
                'photo': 'images/team/john-doe.jpg',
                'bio': '20+ years of experience in financial services'
            },
            {
                'name': 'Jane Smith',
                'position': 'Risk Management Expert',
                'photo': 'images/team/jane-smith.jpg',
                'bio': 'Specializes in regulatory compliance and risk assessment'
            }
        ],
        'case_studies': [
            {
                'title': 'Digital Banking Transformation',
                'description': 'Modernized digital infrastructure for a regional bank, increasing mobile banking adoption by 40%.',
                'results': ['40% increase in mobile banking', 'Improved customer satisfaction']
            },
            {
                'title': 'Regulatory Compliance Overhaul',
                'description': 'Implemented a comprehensive compliance framework for an investment firm.',
                'results': ['75% reduction in compliance issues', 'Streamlined reporting processes']
            }
        ]
    },
    # Other industries can be added here with the same structure
}

def industry_detail(request, industry_slug):
    industry = INDUSTRIES.get(industry_slug)
    if not industry:
        from django.http import Http404
        raise Http404("Industry not found")

    context = {
        'industry': industry,
        'industry_name': industry['name'],
        'industry_tagline': industry['tagline'],
        'stats': industry['stats'],
        'team_members': industry['team_members'],
        'case_studies': industry['case_studies']
    }

    return render(request, f'industries/{industry_slug}.html', context)


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import update_last_login  # For last_login
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

# Safely get the custom User model
User = get_user_model()


@csrf_protect
def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # 🔑 NEW: Retrieve the timezone sent from the client-side
        # Default to 'UTC' if the client fails to send it
        client_timezone = request.POST.get('client_timezone', 'UTC')

        # Validate required fields
        if not email or not password:
            messages.error(request, 'Both email and password are required.')
            return render(request, 'client_portal/login.html')

        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Please enter a valid email address.')
            return render(request, 'client_portal/login.html')

        # Authenticate user
        user = authenticate(request, email=email, password=password)

        if user is not None:
            # Check if user is approved (EXISTING CONDITION)
            if not user.is_approved:
                messages.error(request, 'Your account has not been approved yet. Please contact administrator.')
                return render(request, 'client_portal/login.html')

            # Check if user is active (EXISTING CONDITION)
            if not user.is_active:
                messages.error(request, 'Your account is inactive. Please contact administrator.')
                return render(request, 'client_portal/login.html')

            # Login successful
            login(request, user)

            # ====================================================================
            # 🔑 TIMEZONE AND LAST LOGIN UPDATES
            # ====================================================================

            # 1. Update the user's timezone if it's different from the current stored value
            if user.timezone != client_timezone:
                user.timezone = client_timezone
                # Save only the 'timezone' field for efficiency
                user.save(update_fields=['timezone'])

                # 2. Set the user's last login date correctly
            update_last_login(None, user)

            # ====================================================================

            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'client_portal/login.html')

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import User  # Make sure to import your custom User model
import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .models import User, Task

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
import json


# Assuming Task and User models are correctly imported
# from .models import Task, User

@login_required
def dashboard(request):
    current_user = request.user

    total_tasks = 0
    tasks_to_filter = None
    status_data = {}

    # Initialize other stats to None unless user is admin
    total_users = None
    total_clients = None
    total_staffs = None

    # Determine which tasks the user can see based on their role
    if current_user.role == 'admin':
        # Admin can see all tasks and all user statistics
        tasks_to_filter = Task.objects.all()
        total_users = User.objects.count()
        total_clients = User.objects.filter(role='client').count()
        total_staffs = User.objects.filter(role='staff').count()

    elif current_user.role == 'staff':
        # Staff can only see tasks they are assigned to
        tasks_to_filter = Task.objects.filter(
            Q(supervisee=current_user) | Q(supervisor=current_user)
        )
    # The 'else' case for 'client' is implicitly handled; tasks_to_filter remains None

    if tasks_to_filter is not None:
        # Calculate total tasks and status breakdown if the user has tasks to view
        total_tasks = tasks_to_filter.count()
        tasks_by_status = tasks_to_filter.values('status').annotate(total=Count('status'))
        status_data = {item['status']: item['total'] for item in tasks_by_status}

    status_data_json = json.dumps(status_data)

    context = {
        'user': current_user,
        'total_tasks': total_tasks,
        'total_users': total_users,
        'total_clients': total_clients,
        'total_staffs': total_staffs,
        'status_data_json': status_data_json,
    }
    return render(request, 'client_portal/dashboard.html', context)
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('client_portal')


from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from .models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


@csrf_protect
def signup_view(request):
    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        date_of_birth = request.POST.get('date_of_birth')
        nationality = request.POST.get('nationality')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Validate required fields
        if not all([first_name, last_name, email, phone_number, address,
                    date_of_birth, nationality, password, confirm_password]):
            messages.error(request, 'All fields are required.')
            return render(request, 'client_portal/signup.html', {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone_number': phone_number,
                'address': address,
                'date_of_birth': date_of_birth,
                'nationality': nationality,
            })

        # Validate password match
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'client_portal/signup.html', {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone_number': phone_number,
                'address': address,
                'date_of_birth': date_of_birth,
                'nationality': nationality,
            })

        # Validate password length (at least 8 characters)
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'client_portal/signup.html', {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone_number': phone_number,
                'address': address,
                'date_of_birth': date_of_birth,
                'nationality': nationality,
            })

        # Validate password contains alphanumeric characters and symbols
        # At least one letter, one number, and one special character
        has_letter = any(char.isalpha() for char in password)
        has_digit = any(char.isdigit() for char in password)
        has_special = any(not char.isalnum() for char in password)

        if not (has_letter and has_digit and has_special):
            messages.error(request, 'Password must contain letters, numbers, and special characters.')
            return render(request, 'client_portal/signup.html', {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone_number': phone_number,
                'address': address,
                'date_of_birth': date_of_birth,
                'nationality': nationality,
            })

        # Validate phone number format
        # Check if it starts with +
        if not phone_number.startswith('+'):
            messages.error(request, 'Phone number must start with a + sign.')
            return render(request, 'client_portal/signup.html', {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone_number': phone_number,
                'address': address,
                'date_of_birth': date_of_birth,
                'nationality': nationality,
            })

        # Check if phone number has at least 10 digits (including country code)
        # Remove + sign and any non-digit characters for counting
        digits_only = ''.join(filter(str.isdigit, phone_number))
        if len(digits_only) < 10:
            messages.error(request, 'Phone number must be at least 10 digits long (including country code).')
            return render(request, 'client_portal/signup.html', {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone_number': phone_number,
                'address': address,
                'date_of_birth': date_of_birth,
                'nationality': nationality,
            })

        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Please enter a valid email address.')
            return render(request, 'client_portal/signup.html', {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone_number': phone_number,
                'address': address,
                'date_of_birth': date_of_birth,
                'nationality': nationality,
            })

        # Check if phone number already exists
        if User.objects.filter(phone_number=phone_number).exists():
            messages.error(request, 'This phone number is already registered.')
            return render(request, 'client_portal/signup.html', {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone_number': phone_number,
                'address': address,
                'date_of_birth': date_of_birth,
                'nationality': nationality,
            })

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'This email is already registered.')
            return render(request, 'client_portal/signup.html', {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone_number': phone_number,
                'address': address,
                'date_of_birth': date_of_birth,
                'nationality': nationality,
            })

        try:
            # Create user with the specified defaults
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                address=address,
                date_of_birth=date_of_birth,
                nationality=nationality,
                role='client',
                is_active=True,
                is_approved=False,
                is_staff=False,
                is_superuser=False
            )

            messages.success(request, 'Registration successful! Your account is pending approval.')
            return redirect('user_login')

        except Exception as e:
            messages.error(request, f'An error occurred during registration: {str(e)}')
            return render(request, 'client_portal/signup.html', {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone_number': phone_number,
                'address': address,
                'date_of_birth': date_of_birth,
                'nationality': nationality,
            })

    return render(request, 'client_portal/signup.html')


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.db.models import Q
from .models import User


def is_admin(user):
    return user.is_authenticated and user.role == 'admin'


@login_required
@user_passes_test(is_admin)
def manage_users(request):
    users = User.objects.all().order_by('-date_joined')

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone_number__icontains=search_query) |
            Q(role__icontains=search_query)
        )

    context = {
        'users': users,
        'search_query': search_query,
    }
    return render(request, 'admin/manage_users.html', context)


@login_required
@user_passes_test(is_admin)
def user_detail(request, user_id):
    # Get the user to be viewed
    user_to_view = get_object_or_404(User, id=user_id)

    # Pass both the selected user and the logged-in user to the template
    context = {
        'user_to_view': user_to_view,
        'logged_in_user': request.user
    }
    return render(request, 'admin/user_detail.html', context)

# core/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .models import User, Office  # Make sure to import Office
import cloudinary.uploader

# core/views.py
import cloudinary
import cloudinary.uploader
from django.conf import settings  # Import settings

# Configure Cloudinary using your settings.py variables
cloudinary.config(
  cloud_name = settings.CLOUDINARY_CLOUD_NAME,
  api_key = settings.CLOUDINARY_API_KEY,
  api_secret = settings.CLOUDINARY_API_SECRET,
  secure = True  # Recommended for security
)
def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.hashers import make_password
from .models import User, Office  # Assuming your models are in this directory
import cloudinary.uploader

def is_admin(user):
    return user.is_authenticated and user.role == 'admin'


from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import User, Office
import cloudinary.uploader
import os


# Helper function to check if a user is an admin
def is_admin(user):
    return user.is_authenticated and user.role == 'admin'


@login_required
@user_passes_test(is_admin)
def update_user(request, user_id):
    # Retrieve the user to be updated
    user_to_update = get_object_or_404(User, id=user_id)
    offices = Office.objects.all()

    if request.method == 'POST':
        # --- Form Validation and Data Retrieval ---
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        date_of_birth_str = request.POST.get('date_of_birth')
        nationality = request.POST.get('nationality')
        role = request.POST.get('role')
        office_id = request.POST.get('office')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Basic Required Field Validation
        required_fields = {
            'first_name': first_name, 'last_name': last_name, 'email': email,
            'phone_number': phone_number, 'address': address, 'date_of_birth': date_of_birth_str,
            'nationality': nationality, 'role': role
        }

        for field, value in required_fields.items():
            if not value:
                messages.error(request, f'{field.replace("_", " ").title()} is required.')
                return redirect('update_user', user_id=user_to_update.id)

        if phone_number:
            phone_digits = phone_number.replace('+', '').strip()
            if not phone_number.startswith('+') or not phone_digits.isdigit() or len(phone_digits) < 9:
                messages.error(request,
                               'Phone number must start with "+", contain only digits after the plus sign, and be at least 9 digits long.')
                return redirect('update_user', user_id=user_to_update.id)

        # Email and Phone Number Uniqueness Validation
        if email != user_to_update.email and User.objects.filter(email=email).exists():
            messages.error(request, 'This email is already registered.')
            return redirect('update_user', user_id=user_to_update.id)
        if phone_number != user_to_update.phone_number and User.objects.filter(phone_number=phone_number).exists():
            messages.error(request, 'This phone number is already registered.')
            return redirect('update_user', user_id=user_to_update.id)

        # Password Validation
        if new_password:
            if len(new_password) < 9:
                messages.error(request, 'New password must be at least 9 characters long.')
                return redirect('update_user', user_id=user_to_update.id)
            if new_password != confirm_password:
                messages.error(request, 'New passwords do not match.')
                return redirect('update_user', user_id=user_to_update.id)
            # Update password
            user_to_update.password = make_password(new_password)

        # --- Update User Model Fields ---
        user_to_update.first_name = first_name
        user_to_update.last_name = last_name
        user_to_update.email = email
        user_to_update.phone_number = phone_number
        user_to_update.address = address
        user_to_update.nationality = nationality
        user_to_update.role = role

        # Handle date of birth
        if date_of_birth_str:
            user_to_update.date_of_birth = date_of_birth_str
        else:
            user_to_update.date_of_birth = None

        # Handle office assignment
        if office_id:
            try:
                office_obj = Office.objects.get(id=office_id)
                user_to_update.office = office_obj
            except Office.DoesNotExist:
                messages.error(request, 'Invalid office selected.')
                return redirect('update_user', user_id=user_to_update.id)

        # Other editable fields
        user_to_update.linkedin = request.POST.get('linkedin', user_to_update.linkedin)
        user_to_update.company_impact = request.POST.get('company_impact', user_to_update.company_impact)
        user_to_update.office_impact = request.POST.get('office_impact', user_to_update.office_impact)
        user_to_update.field_position = request.POST.get('field_position', user_to_update.field_position)
        user_to_update.executive_position_description = request.POST.get('executive_position_description',
                                                                         user_to_update.executive_position_description)

        # Boolean fields
        user_to_update.is_active = 'is_active' in request.POST
        user_to_update.is_approved = 'is_approved' in request.POST
        user_to_update.is_staff = 'is_staff' in request.POST
        user_to_update.audit = 'audit' in request.POST
        user_to_update.tax = 'tax' in request.POST
        user_to_update.consulting = 'consulting' in request.POST
        user_to_update.forensic_service = 'forensic_service' in request.POST
        user_to_update.managed_service = 'managed_service' in request.POST
        user_to_update.technology_solution = 'technology_solution' in request.POST
        user_to_update.advisory = 'advisory' in request.POST
        user_to_update.executive_team = 'executive_team' in request.POST

        # --- LOGIC TO SET is_superuser BASED ON ROLE ---
        if role == 'admin':
            user_to_update.is_superuser = True
            # When a user is an admin, they are also considered staff by Django
            user_to_update.is_staff = True
        else:
            user_to_update.is_superuser = False
            # To ensure consistency, if they are not an admin, check if they
            # should still be staff based on the form
            user_to_update.is_staff = 'is_staff' in request.POST

        # Handle profile image upload
        if 'profile_image' in request.FILES:
            image_file = request.FILES['profile_image']
            try:
                upload_result = cloudinary.uploader.upload(image_file)
                user_to_update.profile_image = upload_result['secure_url']
            except Exception as e:
                messages.error(request, f'Failed to upload image: {e}')
                return redirect('update_user', user_id=user_to_update.id)

        user_to_update.save()
        messages.success(request, f'User {user_to_update.email} updated successfully.')
        return redirect('dashboard')
    context = {
        'user_to_update': user_to_update,
        'offices': offices,
        'roles': User.ROLE_CHOICES,
    }
    return render(request, 'admin/update_user.html', context)
from django.contrib.auth import logout
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import User

@login_required
@user_passes_test(is_admin)
def delete_user(request, user_id):
    user_to_delete = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        # Check if the logged-in user is deleting their own account
        if request.user.id == user_to_delete.id:
            # Delete the user's account
            user_to_delete.delete()
            # Log out the user
            logout(request)
            messages.success(request, 'Your account has been successfully deleted.')
            # Redirect to the index page
            return redirect('index')
        else:
            # Logic for an admin deleting a different user's account
            email = user_to_delete.email
            user_to_delete.delete()
            messages.success(request, f'User {email} deleted successfully.')
            return redirect('manage_users')

    return render(request, 'admin/delete_user.html', {'user': user_to_delete})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.hashers import make_password
from .models import User, Office  # Assuming these are your models
import cloudinary.uploader


def is_admin(user):
    return user.is_authenticated and user.is_staff and user.is_superuser


@login_required
@user_passes_test(is_admin)
def add_user(request):
    offices = Office.objects.all()

    if request.method == 'POST':
        # --- Form Validation and Data Retrieval ---
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        date_of_birth_str = request.POST.get('date_of_birth')
        nationality = request.POST.get('nationality')
        role = request.POST.get('role')

        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Basic Required Field Validation
        required_fields = {
            'first_name': first_name, 'last_name': last_name, 'email': email,
            'phone_number': phone_number, 'address': address, 'date_of_birth': date_of_birth_str,
            'nationality': nationality, 'role': role, 'new_password': new_password,
            'confirm_password': confirm_password
        }

        for field, value in required_fields.items():
            if not value:
                messages.error(request, f'{field.replace("_", " ").title()} is required.')
                return redirect('add_user')

        if phone_number:
            phone_digits = phone_number.replace('+', '').strip()
            if not phone_number.startswith('+') or not phone_digits.isdigit() or len(phone_digits) < 9:
                messages.error(request,
                               'Phone number must start with "+", contain only digits after the plus sign, and be at least 9 digits long.')
                return redirect('add_user')

        # Email and Phone Number Uniqueness Validation
        if User.objects.filter(email=email).exists():
            messages.error(request, 'This email is already registered.')
            return redirect('add_user')
        if User.objects.filter(phone_number=phone_number).exists():
            messages.error(request, 'This phone number is already registered.')
            return redirect('add_user')

        # Password Validation
        if len(new_password) < 9:
            messages.error(request, 'Password must be at least 9 characters long.')
            return redirect('add_user')
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('add_user')

        # --- Create New User Model Instance ---
        try:
            # We will set is_superuser and is_staff based on the role below
            user = User.objects.create_user(
                email=email,
                password=new_password,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                address=address,
                nationality=nationality,
                date_of_birth=date_of_birth_str,
                role=role
            )
        except Exception as e:
            messages.error(request, f'Failed to create user: {e}')
            return redirect('add_user')

        # Handle boolean fields
        user.is_active = 'is_active' in request.POST
        user.is_approved = 'is_approved' in request.POST
        user.executive_team = 'executive_team' in request.POST
        user.audit = 'audit' in request.POST
        user.tax = 'tax' in request.POST
        user.consulting = 'consulting' in request.POST
        user.forensic_service = 'forensic_service' in request.POST
        user.managed_service = 'managed_service' in request.POST
        user.technology_solution = 'technology_solution' in request.POST
        user.advisory = 'advisory' in request.POST

        # Handle `is_staff` and `is_superuser` based on the selected role
        if role == 'admin':
            user.is_superuser = True
            user.is_staff = True
        else:
            user.is_superuser = False
            user.is_staff = 'is_staff' in request.POST

        # Handle optional fields
        user.linkedin = request.POST.get('linkedin', '')
        user.company_impact = request.POST.get('company_impact', '')
        user.office_impact = request.POST.get('office_impact', '')
        user.field_position = request.POST.get('field_position', '')
        user.executive_position_description = request.POST.get('executive_position_description', '')

        # Handle profile image upload
        if 'profile_image' in request.FILES:
            image_file = request.FILES['profile_image']
            try:
                upload_result = cloudinary.uploader.upload(image_file)
                user.profile_image = upload_result['secure_url']
            except Exception as e:
                messages.error(request, f'Failed to upload image: {e}')
                user.delete()  # Clean up the created user if image upload fails
                return redirect('add_user')

        # Handle office assignment
        office_id = request.POST.get('office')
        if office_id:
            try:
                office_obj = Office.objects.get(id=office_id)
                user.office = office_obj
            except Office.DoesNotExist:
                messages.error(request, 'Invalid office selected.')
                user.delete()
                return redirect('add_user')

        user.save()
        messages.success(request, f'User {user.email} created successfully.')
        return redirect('manage_users')

    context = {
        'offices': offices,
        'roles': User.ROLE_CHOICES,
    }
    return render(request, 'admin/add_user.html', context)

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import User  # Assuming your custom user model is named User


@login_required
def user_profile(request, user_id):
    # This ensures that only the currently logged-in user can view their profile
    # You could also just use request.user directly in the template
    if request.user.id != user_id:
        # Redirect or show an error if the user tries to access another user's profile
        # For simplicity, we'll just show their own profile
        user = request.user
    else:
        user = get_object_or_404(User, id=user_id)

    context = {
        'user_to_view': user
    }
    return render(request, 'user_profile.html', context)  # You'll need to create this template


# core/views.py

import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone  # <-- Make sure this is imported
from .models import User, PasswordResetOTP

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)

            # Generate a 4-digit OTP
            otp = str(random.randint(1000, 9999))

            # Update or create the OTP object, ensuring the timestamp is always current
            otp_obj, created = PasswordResetOTP.objects.update_or_create(
                user=user,
                defaults={'otp': otp, 'created_at': timezone.now()}
            )

            # --- Professional Email Message Styling ---
            subject = 'OB Global Password Reset'
            context = {
                'user_name': user.first_name,
                'otp': otp,
            }
            html_message = render_to_string('emails/password_reset.html', context)
            plain_message = strip_tags(html_message)
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [user.email]

            send_mail(
                subject,
                plain_message,
                from_email,
                recipient_list,
                html_message=html_message
            )

            messages.success(request, 'A password reset code has been sent to your email.')
            return redirect('verify_otp')

        except User.DoesNotExist:
            messages.error(request, 'No user found with that email address.')

    return render(request, 'authentication/forgot_password.html')


# core/views.py
from django.contrib.auth.hashers import make_password


# ... other imports from above
def verify_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        otp = request.POST.get('otp')

        try:
            user = User.objects.get(email=email)
            otp_obj = PasswordResetOTP.objects.get(user=user)

            if otp_obj.otp == otp:
                # OTP is correct, redirect to password reset page
                request.session['temp_user_id'] = user.id
                messages.success(request, 'OTP verified. You can now reset your password.')
                return redirect('reset_password')
            else:
                messages.error(request, 'Invalid OTP.')
        except (User.DoesNotExist, PasswordResetOTP.DoesNotExist):
            messages.error(request, 'Invalid email or OTP.')

    return render(request, 'authentication/verify_otp.html')

# core/views.py
# ... other imports from above

import re


def reset_password(request):
    if 'temp_user_id' not in request.session:
        messages.error(request, 'Please go through the password reset process again.')
        return redirect('forgot_password')

    user_id = request.session['temp_user_id']
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # 1. Check if passwords match
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'authentication/reset_password.html')

        # 2. Check for minimum length
        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'authentication/reset_password.html')

        # 3. Check if password is alphanumeric
        # The isalnum() method checks if a string contains only letters and numbers and is not empty.
        if not new_password.isalnum():
            messages.error(request, 'Password must contain only letters and numbers (no special characters or spaces).')
            return render(request, 'authentication/reset_password.html')

        # 4. Check if password contains both letters and numbers
        # Use regex to ensure the password has at least one letter and one number.
        if not (re.search(r'[a-zA-Z]', new_password) and re.search(r'\d', new_password)):
            messages.error(request, 'Password must be alphanumeric and contain both letters and numbers.')
            return render(request, 'authentication/reset_password.html')

        # If all checks pass, update the password
        user.set_password(new_password)
        user.save()

        # Clear the temporary user ID from the session and delete the OTP
        del request.session['temp_user_id']
        PasswordResetOTP.objects.filter(user=user).delete()

        messages.success(request, 'Your password has been reset successfully.')
        return redirect('user_login')

    return render(request, 'authentication/reset_password.html')


# core/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import User, Task, TaskFile, TaskStatus
from django.db.models import Q


# Decorator for admin-only access
def admin_required(view_func):
    def wrapper_func(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'admin':
            return HttpResponseForbidden("You are not authorized to access this page.")
        return view_func(request, *args, **kwargs)

    return wrapper_func


# Decorator for admin or supervisor access
def admin_or_supervisor_required(view_func):
    def wrapper_func(request, *args, **kwargs):
        if not request.user.is_authenticated or (request.user.role != 'admin' and request.user.role != 'supervisor'):
            return HttpResponseForbidden("You are not authorized to access this page.")
        return view_func(request, *args, **kwargs)

    return wrapper_func


# your_app/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import models  # 👈 Add this line
from .models import Task, User


@login_required
def task_list(request):
    user = request.user

    if user.role == 'admin':
        # Admin can view all tasks
        tasks = Task.objects.all().order_by('-created_at')
    else:
        # Staff and other roles can only see tasks where they are either
        # the supervisee or the supervisor.
        tasks = Task.objects.filter(
            models.Q(supervisee=user) | models.Q(supervisor=user)
        ).order_by('-created_at')

    context = {
        'tasks': tasks,
        'is_admin': user.role == 'admin'
    }
    return render(request, 'tasks/task_list.html', context)
# your_app/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Task, User
from .decorators import admin_required

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Task, User
from .decorators import admin_required
from datetime import datetime

@admin_required
def task_create(request):
    if request.method == 'POST':
        task_title = request.POST.get('task_title')
        task_purpose = request.POST.get('task_purpose')
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        supervisor_id = request.POST.get('supervisor')
        supervisee_id = request.POST.get('supervisee')

        supervisor = get_object_or_404(User, id=supervisor_id)
        supervisee = get_object_or_404(User, id=supervisee_id)

        if supervisor == supervisee:
            messages.error(request, 'Supervisor and Supervisee cannot be the same person.')
            return redirect('task_create')

        # Convert date strings to datetime objects for comparison
        # Use try-except to handle potential errors if date strings are invalid
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M') if end_date_str else None
        except (ValueError, TypeError):
            messages.error(request, 'Invalid date format. Please use a valid date and time.')
            return redirect('task_create')

        # ⚠️ New validation check
        if end_date and start_date > end_date:
            messages.error(request, 'The start date cannot be after the end date.')
            return redirect('task_create')

        # Create the task using the converted datetime objects
        task = Task.objects.create(
            task_title=task_title,
            task_purpose=task_purpose,
            start_date=start_date,
            end_date=end_date,
            supervisor=supervisor,
            supervisee=supervisee,
            created_by=request.user,
        )

        messages.success(request, 'Task created successfully. You can now add files to it.')
        return redirect('task_list')

    available_users = User.objects.filter(role='staff')
    context = {
        'available_users': available_users,
    }
    return render(request, 'tasks/task_create.html', context)
@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    user = request.user

    # Permission check: user must be admin, supervisor, or supervisee of the task
    if not (user.role == 'admin' or task.supervisor == user or task.supervisee == user):
        return HttpResponseForbidden("You do not have permission to view this task.")

    context = {
        'task': task,
        'is_admin': user.role == 'admin',
        'is_supervisor': task.supervisor == user,
        'is_supervisee': task.supervisee == user,
        'task_files': task.task_files.filter(file_type='task_document'),
        'submission_files': task.task_files.filter(file_type='submission_file')
    }
    return render(request, 'tasks/task_detail.html', context)


# your_app/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Q
from .models import User, Task, TaskStatus

# your_app/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Q
from .models import Task, User, TaskStatus # Import TaskStatus
# views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .models import Task, User, TaskStatus  # Assuming User and TaskStatus are correctly imported


@login_required
def task_update(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    user = request.user

    if not (user.role == 'admin' or task.supervisor == user):
        return HttpResponseForbidden("You do not have permission to update this task.")

    if request.method == 'POST':
        task.task_title = request.POST.get('task_title')
        task.task_purpose = request.POST.get('task_purpose')

        # --- FIX FOR VALIDATION ERROR ---
        # 1. Get the raw POST values for date fields
        start_date_raw = request.POST.get('start_date')
        end_date_raw = request.POST.get('end_date')

        # 2. Assign the value, setting it to None if the string is empty
        # This prevents the ValidationError when a required date field is left blank.
        task.start_date = start_date_raw if start_date_raw else None
        task.end_date = end_date_raw if end_date_raw else None
        # --- END FIX ---

        if user.role == 'admin' or task.supervisor == user:
            task.status = request.POST.get('status')

            # Key Note Field: Ensure this is also handled if it can be optional
            key_note_raw = request.POST.get('key_note')
            task.key_note = key_note_raw if key_note_raw else None

        if task.supervisee == user:
            supervisee_feedback_raw = request.POST.get('supervisee_feedback')
            task.supervisee_feedback = supervisee_feedback_raw if supervisee_feedback_raw else ""  # Assuming feedback is a CharField/TextField

        if user.role == 'admin':
            supervisor_id = request.POST.get('supervisor')
            supervisee_id = request.POST.get('supervisee')

            # Ensure IDs are present before fetching (optional but safe)
            if supervisor_id and supervisee_id:
                supervisor = get_object_or_404(User, id=supervisor_id)
                supervisee = get_object_or_404(User, id=supervisee_id)

                if supervisor == supervisee:
                    messages.error(request, 'Supervisor and Supervisee cannot be the same person.')
                    return redirect('task_update', task_id=task.id)

                task.supervisor = supervisor
                task.supervisee = supervisee

        task.save()
        messages.success(request, 'Task updated successfully.')
        return redirect('task_detail', task_id=task.id)

    # For GET request, provide filtered user lists for the template.
    available_users = User.objects.exclude(role='admin')

    context = {
        'task': task,
        'available_users': available_users,
        'is_admin': user.role == 'admin',
        'is_supervisor': task.supervisor == user,
        'is_supervisee': task.supervisee == user,
        'task_status_choices': TaskStatus.choices,
    }
    return render(request, 'tasks/task_update.html', context)
# your_app/views.py
import cloudinary.utils
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib import messages
import os

from .models import TaskFile, Task

import cloudinary
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from urllib.parse import urlparse
import os

from .models import TaskFile, Task

# your_app/views.py
import requests
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, HttpResponseForbidden
import os

from .models import TaskFile, Task

import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import Task, TaskFile

# This view handles the file upload directly from the browser to Django,
# and then from Django to Cloudinary's API.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .models import Task, TaskFile
import cloudinary.uploader  # <--- NEW: Import the Cloudinary uploader SDK

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
import cloudinary.uploader
import os  # <-- 1. IMPORT OS FOR FILEPATH OPERATIONS


# NOTE: Ensure Task and TaskFile are imported from your models file
# from .models import Task, TaskFile

@login_required
def task_add_file(request, task_id):
    """
    Handles file upload, validates the file extension, and ensures public access
    on Cloudinary.
    """
    task = get_object_or_404(Task, id=task_id)
    user = request.user

    # 2. DEFINE ALLOWED EXTENSIONS
    ALLOWED_EXTENSIONS = ['.txt', '.docx', '.png', '.jpg']

    if request.method == 'POST':
        # 1. Retrieve the uploaded file and file_type
        uploaded_file = request.FILES.get('file_to_upload')
        file_type = request.POST.get('file_type')

        # --- File Presence Check ---
        if not uploaded_file:
            messages.error(request, 'Please select a file to upload before submitting.')
            # Use 'task_detail' redirect here, as the view will be accessed via GET redirect from there.
            return redirect('task_detail', task_id=task.id)

        # --- NEW: File Extension Validation ---
        file_name = uploaded_file.name
        # os.path.splitext returns a tuple (root, ext), e.g., ('report', '.pdf')
        _, file_extension = os.path.splitext(file_name)

        # Convert to lowercase to ensure case-insensitive validation
        if file_extension.lower() not in ALLOWED_EXTENSIONS:
            messages.error(
                request,
                f"File type '{file_extension}' is not allowed. Only {', '.join(ALLOWED_EXTENSIONS)} are permitted."
            )
            return redirect('task_detail', task_id=task.id)

        # 2. Permission and File Count Check (Existing Logic)
        is_submission = (file_type == 'submission_file')

        if is_submission:
            if task.supervisee != user:
                return HttpResponseForbidden("You do not have permission to add a submission file.")
            # Use your actual model name for TaskFile
            if TaskFile.objects.filter(task=task, uploaded_by=user, file_type='submission_file').exists():
                messages.error(request, 'You can only submit one file for this task.')
                return redirect('task_detail', task_id=task.id)
        elif not (user.role == 'admin' or task.supervisor == user):
            return HttpResponseForbidden("You do not have permission to add this type of file.")

        # 3. Server-Side Cloudinary Upload
        try:
            folder_path = f"tasks/{task_id}/{file_type}"

            # Upload the file using the Cloudinary SDK
            upload_result = cloudinary.uploader.upload(
                uploaded_file,
                folder=folder_path,
                resource_type='auto',
                access_mode='public',  # <--- Ensures public access (Fixes 401 error)
                timeout=600
            )

            # Extract necessary data from the result
            cloudinary_url = upload_result.get('secure_url')
            public_id = upload_result.get('public_id')

            # 4. Save to Database (Use your actual model name for TaskFile)
            TaskFile.objects.create(
                task=task,
                cloudinary_url=cloudinary_url,
                public_id=public_id,
                file_type=file_type,
                uploaded_by=user,
            )
            messages.success(request, f"File '{file_name}' added successfully.")
            return redirect('task_detail', task_id=task.id)

        except Exception as e:
            messages.error(request,
                           f"Upload failed: A server error occurred during file processing. ({type(e).__name__}: {str(e)})")
            return redirect('task_detail', task_id=task.id)

    # --- GET Request (Display Form) ---
    file_type = request.GET.get('file_type', 'document')

    context = {
        'task': task,
        'file_type': file_type,
        'allowed_extensions_list': ALLOWED_EXTENSIONS  # Pass to template for display
    }
    return render(request, 'tasks/task_add_file.html', context)
# your_app/views.py
import requests
import os
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, HttpResponseForbidden

from .models import Task, TaskFile


@login_required
def task_download_file(request, task_id, file_id):
    try:
        task = get_object_or_404(Task, id=task_id)
        task_file = get_object_or_404(TaskFile, id=file_id)
        user = request.user

        # Ensure the file belongs to the task and the user has permission
        if task_file.task != task:
            messages.error(request, "File does not belong to this task.")
            return redirect('task_detail', task_id=task.id)

        can_download = (user.role == 'admin' or task.supervisor == user or task.supervisee == user)
        if not can_download:
            return HttpResponseForbidden("You do not have permission to download this file.")

        # Check if the public_id exists
        if not task_file.public_id:
            messages.error(request, "File is missing its public ID. It might have been uploaded incorrectly.")
            return redirect('task_detail', task_id=task.id)

        # Get the file extension from the public_id
        file_extension = os.path.splitext(task_file.public_id)[-1].lstrip('.')

        # Determine the Cloudinary resource type. This is important for downloads.
        resource_type = 'raw' if file_extension in ['pdf', 'doc', 'docx', 'zip', 'txt'] else 'image'

        # Construct the direct Cloudinary URL with the 'fl_attachment' transformation to force download.
        download_url = (
            f"https://res.cloudinary.com/dpupwwixw/{resource_type}/upload/fl_attachment/"
            f"{task_file.public_id}"
        )

        # Stream the file from Cloudinary and serve it with Django's HttpResponse
        response_from_cloudinary = requests.get(download_url, stream=True)
        response_from_cloudinary.raise_for_status()  # Raise an exception for bad status codes

        # Prepare Django's HttpResponse to send the file to the user
        filename = f"{task_file.public_id.split('/')[-1]}"  # Use the last part of public_id as filename
        django_response = HttpResponse(
            response_from_cloudinary.iter_content(chunk_size=8192),
            content_type=response_from_cloudinary.headers.get('Content-Type', 'application/octet-stream')
        )
        django_response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return django_response

    except Exception as e:
        messages.error(request, f"An error occurred while downloading the file: {e}")
        return redirect('task_detail', task_id=task.id)

@admin_required
def task_delete(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted successfully.')
        return redirect('task_list')
    return render(request, 'tasks/task_delete.html', {'task': task})


import cloudinary.uploader
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden

from .models import Task, TaskFile

# your_app/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden

from .models import Task, TaskFile
# your_app/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import Task, TaskFile
import os

@login_required
def task_delete_file(request, task_id, file_id):
    task = get_object_or_404(Task, id=task_id)
    task_file = get_object_or_404(TaskFile, id=file_id, task=task)
    user = request.user

    # Permissions
    can_delete = False
    # Admin can delete any file
    if user.role == 'admin':
        can_delete = True
    # Supervisor can delete any file on their task
    elif task.supervisor == user:
        can_delete = True
    # Supervisee can only delete their own submission file
    elif task.supervisee == user and task_file.file_type == 'submission_file' and task_file.uploaded_by == user:
        can_delete = True

    if not can_delete:
        return HttpResponseForbidden("You do not have permission to delete this file.")

    # ⚠️ This is the fix: Extract the filename to pass to the template
    filename = os.path.basename(task_file.public_id) if task_file.public_id else "File"

    if request.method == 'POST':
        task_file.delete()
        messages.success(request, f'File "{filename}" deleted successfully.')
        return redirect('task_detail', task_id=task.id)

    context = {
        'task_file': task_file,
        'filename': filename  # ⚠️ Pass the extracted filename to the template
    }
    return render(request, 'tasks/task_delete_file.html', context)
from django import template

register = template.Library()

@register.filter
def filename_from_public_id(public_id):
    """
    Extracts the filename from a Cloudinary public_id.
    e.g., 'tasks/30001/example_file.pdf' -> 'example_file.pdf'
    """
    return public_id.split('/')[-1]


# core/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from .models import Task # Make sure Task is imported

@login_required
def task_feedback(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    user = request.user

    # Permission check: Only the assigned supervisee can submit/edit feedback.
    if user != task.supervisee:
        return HttpResponseForbidden("You do not have permission to provide feedback for this task.")

    if request.method == 'POST':
        feedback_text = request.POST.get('feedback_text')

        # Update the supervisee_feedback field on the Task model
        task.supervisee_feedback = feedback_text
        task.save()
        messages.success(request, 'Feedback saved successfully.')
        return redirect('task_detail', task_id=task.id)

    # For a GET request, we just return a success message or JSON data
    return JsonResponse({'status': 'ok'})


# core/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Task

@login_required
def task_clear_feedback(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    user = request.user

    # Permission check: only the assigned supervisee can clear their feedback.
    if user != task.supervisee:
        return HttpResponseForbidden("You do not have permission to clear feedback for this task.")

    if request.method == 'POST':
        # Clear the feedback by setting the field to an empty string.
        task.supervisee_feedback = ""
        task.save()
        messages.success(request, 'Feedback cleared successfully.')
        return redirect('task_detail', task_id=task.id)

    return HttpResponseForbidden("Invalid request method.")



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django.db.models import Q
from django.utils import timezone
import random
from cloudinary.uploader import destroy as cloudinary_destroy
import cloudinary


def subscribe_redirect(request):
    """
    Redirects the user to the newsletter app's subscription page.
    """
    return redirect('newsletter:subscribe')

from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib import messages

# ... (rest of your existing views)

def contact_us(request):
    """
    Handles the contact form submission and sends an email.
    """
    if request.method == 'POST':
        # Get data from the form
        category = request.POST.get('question_category')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        job_title = request.POST.get('job_title')
        company = request.POST.get('company')
        location = request.POST.get('location')
        postal_code = request.POST.get('postal_code')
        message = request.POST.get('message')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        hear_about = request.POST.get('hear_about_us')

        # Check for required fields
        if not all([category, first_name, last_name, email, message]):
            messages.error(request, "Please fill in all required fields.")
            return render(request, 'contact/index.html')

        # Render email content from a template
        subject = f'New Contact Form Submission: {category}'
        html_message = render_to_string('contact/email_template.html', {
            'category': category,  # Pass the category variable to the template
            'first_name': first_name,
            'last_name': last_name,
            'job_title': job_title,
            'company': company,
            'location': location,
            'postal_code': postal_code,
            'message': message,
            'phone_number': phone_number,
            'email': email,
            'hear_about': hear_about,
        })
        plain_message = f"""
        New Contact Form Submission

        Category: {category}
        Name: {first_name} {last_name}
        Job Title: {job_title}
        Company: {company}
        Location: {location}
        Postal Code: {postal_code}
        Phone: {phone_number}
        Email: {email}
        Heard About Us: {hear_about}
        Message: {message}
        """

        try:
            # Send the email using settings from your settings.py
            send_mail(
                subject,
                plain_message,
                'petermomo124@gmail.com',  # From email, defined in settings
                ['Obconsultfirm@gmail.com'],  # To email
                html_message=html_message,
                fail_silently=False,
            )
            messages.success(request, "Thank you! Your message has been sent successfully.")
            return redirect('contact')
        except Exception as e:
            messages.error(request, f"There was an error sending your message. Please try again. Error: {e}")
            return render(request, 'contact/index.html')

    # For a GET request, just render the form
    return render(request, 'contact/index.html')



from django.shortcuts import render

def privacy_policy(request):
    return render(request, 'privacy.html')



# core/views.py (Add this function)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def view_my_profile(request):
    """
    Displays the profile of the currently logged-in user.
    """
    context = {
        'user_to_view': request.user,
    }
    # We will use a new template: 'user/view_my_profile.html'
    return render(request, 'user/view_my_profile.html', context)


# core/views.py (Add this function, adjust imports as needed)
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import cloudinary.uploader


# Assuming these are imported at the top of your file:
# from django.contrib.auth.hashers import make_password
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, redirect
# from django.contrib import messages
# from .models import User  # or wherever your User model is defined
# import cloudinary.uploader # if using Cloudinary

@login_required
def edit_my_profile(request):
    """
    Allows the logged-in user to edit their own profile information.
    """
    user_to_update = request.user

    if request.method == 'POST':
        # --- Data Retrieval for User-Editable Fields ---
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        linkedin = request.POST.get('linkedin')
        date_of_birth_str = request.POST.get('date_of_birth')
        nationality = request.POST.get('nationality')

        # Password Fields
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # -----------------------------------------------------------------
        # --- Validation: Required Fields & Format Checks (UNCHANGED) ---
        # -----------------------------------------------------------------

        # Basic Required Field Validation
        required_fields = {
            'first_name': first_name, 'last_name': last_name, 'email': email,
            'phone_number': phone_number, 'address': address, 'nationality': nationality
        }

        for field, value in required_fields.items():
            if not value:
                messages.error(request, f'{field.replace("_", " ").title()} is required.')
                return redirect('edit_my_profile')

        # Phone Number Format Validation
        if phone_number:
            phone_digits = phone_number.replace('+', '').strip()
            if not phone_number.startswith('+') or not phone_digits.isdigit() or len(phone_digits) < 9:
                messages.error(request,
                               'Phone number must start with "+", contain only digits after the plus sign, and be at least 9 digits long.')
                return redirect('edit_my_profile')

        # Email and Phone Number Uniqueness Validation (Requires User import)
        if email != user_to_update.email and User.objects.filter(email=email).exists():
            messages.error(request, 'This email is already registered.')
            return redirect('edit_my_profile')
        if phone_number != user_to_update.phone_number and User.objects.filter(phone_number=phone_number).exists():
            messages.error(request, 'This phone number is already registered.')
            return redirect('edit_my_profile')

        # -----------------------------------------------------------------
        # --- Password Field Consistency Check (The requested feature) ---
        # -----------------------------------------------------------------

        # Check if ANY password field was filled by the user.
        password_fields_entered = bool(current_password or new_password or confirm_password)

        if password_fields_entered:
            # If the user started filling password fields, ALL three must be provided.
            if not current_password or not new_password or not confirm_password:
                messages.error(request,
                               'To change your password, all three fields must be completed: Current Password, New Password, and Confirm New Password.')
                return redirect('edit_my_profile')

            # Since all three are present, proceed to the full password update validation
            # which is now moved into this block for clarity.

            # Current password verification
            if not user_to_update.check_password(current_password):
                messages.error(request, 'Incorrect current password.')
                return redirect('edit_my_profile')

            # New password length check
            if len(new_password) < 9:
                messages.error(request, 'New password must be at least 9 characters long.')
                return redirect('edit_my_profile')

            # New password match check
            if new_password != confirm_password:
                messages.error(request, 'New passwords do not match.')
                return redirect('edit_my_profile')

            # Update password hash (only done if all checks pass)
            user_to_update.password = make_password(new_password)

        # -----------------------------------------------------------------
        # --- END Password Logic ---
        # -----------------------------------------------------------------

        # --- Update User Model Fields (Only the allowed fields) ---
        user_to_update.first_name = first_name
        user_to_update.last_name = last_name
        user_to_update.email = email
        user_to_update.phone_number = phone_number
        user_to_update.address = address
        user_to_update.nationality = nationality
        user_to_update.linkedin = linkedin

        # Handle date of birth
        user_to_update.date_of_birth = date_of_birth_str if date_of_birth_str else None

        # Handle profile image upload/clear
        if 'profile_image' in request.FILES:
            image_file = request.FILES['profile_image']
            try:
                # Requires 'cloudinary.uploader' to be imported/accessible
                upload_result = cloudinary.uploader.upload(image_file)
                user_to_update.profile_image = upload_result['secure_url']
            except Exception as e:
                messages.error(request, f'Failed to upload image: {e}')
                return redirect('edit_my_profile')

        # Optional: Check for a checkbox/hidden field to explicitly delete the image
        # if 'clear_profile_image' in request.POST:
        #     user_to_update.profile_image = None

        user_to_update.save()
        messages.success(request, 'Your profile has been updated successfully. 🥳')
        return redirect('view_my_profile')

    context = {
        'user_to_update': user_to_update,
    }
    return render(request, 'user/edit_my_profile.html', context)



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Office  # Ensure this import is correct
from .forms import OfficeForm  # Ensure this import is correct
from django.contrib import messages


# ... other necessary imports (like User, make_password, etc.)

# ... (Your existing views) ...

# 🏢 OFFICE MANAGEMENT VIEWS

@login_required
def manage_offices(request):
    # Security check: Only Admins/Staff should manage offices
    if request.user.role not in ['admin', 'staff']:
        messages.error(request, "You do not have permission to view this page.")
        return redirect('dashboard')  # Redirect to a safe page

    query = request.GET.get('q')

    if query:
        # Search by office name, location, or purpose
        offices = Office.objects.filter(
            Q(office_Name__icontains=query) |
            Q(office_location__icontains=query) |
            Q(office_purpose__icontains=query)
        ).order_by('office_Name')
    else:
        offices = Office.objects.all().order_by('office_Name')

    context = {
        'offices': offices,
        'query': query,
    }
    return render(request, 'manage/manage_offices.html', context)


@login_required
def add_office(request):
    if request.user.role != 'admin':
        messages.error(request, "Only Admins can add new offices.")
        return redirect('manage_offices')

    if request.method == 'POST':
        form = OfficeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Office '{form.cleaned_data['office_Name']}' added successfully.")
            return redirect('manage_offices')
    else:
        form = OfficeForm()

    return render(request, 'manage/office_form.html', {'form': form, 'page_title': 'Add New Office'})


@login_required
def edit_office(request, office_id):
    if request.user.role != 'admin':
        messages.error(request, "Only Admins can edit offices.")
        return redirect('manage_offices')

    office = get_object_or_404(Office, id=office_id)

    if request.method == 'POST':
        form = OfficeForm(request.POST, instance=office)
        if form.is_valid():
            form.save()
            messages.success(request, f"Office '{office.office_Name}' updated successfully.")
            return redirect('manage_offices')
    else:
        form = OfficeForm(instance=office)

    return render(request, 'manage/office_form.html',
                  {'form': form, 'office': office, 'page_title': f'Edit {office.office_Name}'})


# core/views.py

@login_required
def view_office(request, office_id):
    office = get_object_or_404(Office, id=office_id)

    # ----------------------------------------------------
    # 🔑 FIX: Create a separate link URL in the view
    # ----------------------------------------------------
    large_map_url = None
    if office.google_map_url and 'maps/embed' in office.google_map_url.lower():
        # Replace the '/embed' part with '/place' to create a standard, clickable link
        large_map_url = office.google_map_url.replace('/embed', '/place')

    context = {
        'office': office,
        # Pass the newly created link URL to the template
        'large_map_url': large_map_url,
    }

    return render(request, 'manage/view_office.html', context)

@login_required
def delete_office(request, office_id):
    if request.user.role != 'admin':
        messages.error(request, "Only Admins can delete offices.")
        return redirect('manage_offices')

    office = get_object_or_404(Office, id=office_id)

    if request.method == 'POST':
        office_name = office.office_Name
        office.delete()
        messages.success(request, f"Office '{office_name}' deleted successfully.")
        return redirect('manage_offices')

    # Optional: Render a confirmation page if not a POST request
    return render(request, 'manage/office_confirm_delete.html', {'office': office})


# core/views.py - Add these views to your existing views

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import User


# Advisory Main Views
def advisory_main(request):
    """Main advisory page"""
    advisory_staff = User.objects.filter(
        advisory=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    # ✅ Get regional leaders from database - only active ones
    regional_leaders = RegionalLeader.objects.filter(
        is_active=True
    ).order_by('display_order', 'region')[:8]  # Limit to 8 for the component

    # ✅ Get managing partners from database - only active ones
    managing_partners = ManagingPartner.objects.filter(
        is_active=True
    ).order_by('display_order')[:3]  # Limit to 3

    context = {
        'advisory_staff': advisory_staff,
        'regional_leaders': regional_leaders,
        'managing_partners': managing_partners,
    }
    return render(request, 'advisory/index.html', context)
# Forensic Services Views
def forensic_accounting(request):
    """Forensic Accounting page"""
    advisory_staff = User.objects.filter(
        advisory=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'advisory_staff': advisory_staff,
        'service_name': 'Forensic Accounting',
        'service_description': 'Expert investigative accounting services to detect, prevent, and resolve financial irregularities, fraud, and compliance issues.',
    }
    return render(request, 'advisory/forensic_services/forensic_accounting.html', context)


def forensic_audit_investigation(request):
    """Forensic Audit and Investigation Analysis page"""
    advisory_staff = User.objects.filter(
        advisory=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'advisory_staff': advisory_staff,  # ✅ Correct variable name
        'service_name': 'Forensic Audit and Investigation Analysis',
        'service_description': 'Comprehensive audit and investigation services to uncover financial discrepancies and ensure regulatory compliance.',
    }
    return render(request, 'advisory/forensic_services/forensic_audit_investigation.html', context)
# Financial Accounting Outsourcing Views
def cfo_service(request):
    """CFO Service page"""
    advisory_staff = User.objects.filter(
        advisory=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'advisory_staff': advisory_staff,
        'service_name': 'CFO Service',
        'service_description': 'Strategic financial leadership and executive guidance to drive business growth and financial excellence.',
    }
    return render(request, 'advisory/forensic_services/financial_accounting_outsourcing/cfo_service.html', context)


def bookkeeping_service(request):
    """Book-keeping Service page"""
    advisory_staff = User.objects.filter(
        advisory=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'advisory_staff': advisory_staff,
        'service_name': 'Book-keeping Service',
        'service_description': 'Comprehensive bookkeeping solutions to maintain accurate financial records and support business decision-making.',
    }
    return render(request, 'advisory/forensic_services/financial_accounting_outsourcing/bookkeeping_service.html',
                  context)


def tax_planning_advisory(request):
    """Tax Planning and Advisory page"""
    advisory_staff = User.objects.filter(
        advisory=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'advisory_staff': advisory_staff,
        'service_name': 'Tax Planning and Advisory',
        'service_description': 'Strategic tax planning and advisory services to optimize tax efficiency and ensure compliance.',
    }
    return render(request, 'advisory/forensic_services/financial_accounting_outsourcing/tax_planning_advisory.html',
                  context)


def internal_control_sox_compliance(request):
    """Internal Control (SOX) Compliance page"""
    advisory_staff = User.objects.filter(
        advisory=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'advisory_staff': advisory_staff,
        'service_name': 'Internal Control (SOX) Compliance',
        'service_description': 'Comprehensive SOX compliance services to strengthen internal controls and meet regulatory requirements.',
    }
    return render(request,
                  'advisory/forensic_services/financial_accounting_outsourcing/internal_control_sox_compliance.html',
                  context)


# Forensic Audit Investigation Sub-services
def payroll_processing_management(request):
    """Payroll Processing and Management page"""
    advisory_staff = User.objects.filter(
        advisory=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'advisory_staff': advisory_staff,
        'service_name': 'Payroll Processing and Management',
        'service_description': 'End-to-end payroll solutions to ensure accurate, compliant, and efficient payroll processing.',
    }
    return render(request, 'advisory/forensic_services/forensic_audit_investigation/payroll_processing_management.html',
                  context)


def account_management_bookkeeping(request):
    """Account Management and Bookkeeping page"""
    advisory_staff = User.objects.filter(
        advisory=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'advisory_staff': advisory_staff,
        'service_name': 'Account Management and Bookkeeping',
        'service_description': 'Professional account management and bookkeeping services to maintain financial integrity and support growth.',
    }
    return render(request,
                  'advisory/forensic_services/forensic_audit_investigation/account_management_bookkeeping.html',
                  context)


# Advisory Services Views
def tax_planning_advisory_main(request):
    """Tax Planning and Advisory main page"""
    advisory_staff = User.objects.filter(
        advisory=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'advisory_staff': advisory_staff,
        'service_name': 'Tax Planning and Advisory',
        'service_description': 'Strategic tax planning and advisory services to optimize your tax position and ensure compliance across all jurisdictions.',
    }
    return render(request, 'advisory/advisory_services/tax_planning_advisory.html', context)


def financial_accounting_advisory(request):
    """Financial Accounting Advisory page"""
    advisory_staff = User.objects.filter(
        advisory=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'advisory_staff': advisory_staff,
        'service_name': 'Financial Accounting Advisory',
        'service_description': 'Expert financial accounting guidance to enhance reporting accuracy, compliance, and strategic decision-making.',
    }
    return render(request, 'advisory/advisory_services/financial_accounting_advisory.html', context)


def internal_control_sox_compliance_main(request):
    """Internal Control Compliance (SOX) main page"""
    advisory_staff = User.objects.filter(
        advisory=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'advisory_staff': advisory_staff,
        'service_name': 'Internal Control Compliance (SOX)',
        'service_description': 'Comprehensive SOX compliance services to establish, monitor, and optimize internal control environments.',
    }
    return render(request, 'advisory/advisory_services/internal_control_sox_compliance.html', context)


# API View for Staff Modal
def get_staff_details(request, staff_id):
    """API endpoint to get staff details for modal"""
    staff = get_object_or_404(User, id=staff_id, is_active=True, is_approved=True)

    data = {
        'id': staff.id,
        'first_name': staff.first_name,
        'last_name': staff.last_name,
        'email': staff.email,
        'phone_number': staff.phone_number or '',
        'address': staff.address or '',
        'nationality': staff.nationality or '',
        'linkedin': staff.linkedin or '',
        'profile_image': staff.profile_image.url if staff.profile_image else '',
        'field_position': staff.field_position or '',
        'company_impact': staff.company_impact or '',
        'office_impact': staff.office_impact or '',
        'office_location': staff.office.office_location if staff.office else '',
        'executive_position_description': staff.executive_position_description or '',
    }

    return JsonResponse(data)


# Technology Solutions Views
def technology_main(request):
    """Main technology solutions page"""
    technology_staff = User.objects.filter(
        technology_solution=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    # ✅ Get regional leaders from database - only active ones
    regional_leaders = RegionalLeader.objects.filter(
        is_active=True
    ).order_by('display_order', 'region')[:8]  # Limit to 8 for the component

    # ✅ Get managing partners from database - only active ones
    managing_partners = ManagingPartner.objects.filter(
        is_active=True
    ).order_by('display_order')[:3]  # Limit to 3

    # ✅ Get technology staff who are also marked as leaders/executives
    technology_leaders = User.objects.filter(
        technology_solution=True,
        executive_team=True,  # Or any field that indicates leadership
        is_active=True,
        is_approved=True
    ).select_related('office')[:5]  # Limit to 5

    context = {
        'technology_staff': technology_staff,
        'regional_leaders': regional_leaders,
        'managing_partners': managing_partners,
        'technology_leaders': technology_leaders,
    }
    return render(request, 'technology/index.html', context)
# Implementation Services Views
def it_project_management_service(request):
    """IT Project Management Service page"""
    technology_staff = User.objects.filter(
        technology_solution=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    # Regional leaders data - following the same structure as advisory_main
    regional_leaders = [
        {
            'id': 1,
            'first_name': 'Sarah',
            'last_name': 'Johnson',
            'profile_image': 'https://i.pinimg.com/1200x/77/31/a1/7731a10b118bb5b0a0c77bc6f8544bfa.jpg',
            'email': 'sarah.johnson@obglobal.com',
            'linkedin': 'https://linkedin.com/in/sarahjohnson'
        },
        {
            'id': 2,
            'first_name': 'David',
            'last_name': 'Chen',
            'profile_image': 'https://i.pinimg.com/736x/ae/e6/d4/aee6d45245609592339c8508ae27182d.jpg',
            'email': 'david.chen@obglobal.com',
            'linkedin': 'https://linkedin.com/in/davidchen'
        },
        {
            'id': 3,
            'first_name': 'Amina',
            'last_name': 'Diallo',
            'profile_image': 'https://i.pinimg.com/736x/ae/e6/d4/aee6d45245609592339c8508ae27182d.jpg',
            'email': 'amina.diallo@obglobal.com',
            'linkedin': 'https://linkedin.com/in/aminadiallo'
        },
        {
            'id': 4,
            'first_name': 'Kwame',
            'last_name': 'Osei',
            'profile_image': 'https://i.pinimg.com/736x/ae/e6/d4/aee6d45245609592339c8508ae27182d.jpg',
            'email': 'kwame.osei@obglobal.com',
            'linkedin': 'https://linkedin.com/in/kwameosei'
        },
        {
            'id': 5,
            'first_name': 'Fatima',
            'last_name': 'Bello',
            'profile_image': 'https://i.pinimg.com/736x/ae/e6/d4/aee6d45245609592339c8508ae27182d.jpg',
            'email': 'fatima.bello@obglobal.com',
            'linkedin': 'https://linkedin.com/in/fatimabello'
        }
    ]

    context = {
        'technology_staff': technology_staff,
        'regional_leaders': regional_leaders,
        'service_name': 'IT Project Management Service',
        'service_description': 'Comprehensive IT project management services to ensure successful technology implementations and digital transformations.',
    }
    return render(request, 'technology/implementation_services/it_project_management.html', context)
def hardware_implementation_management(request):
    """Hardware Implementation Management page"""
    technology_staff = User.objects.filter(
        technology_solution=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'technology_staff': technology_staff,
        'service_name': 'Hardware Implementation Management',
        'service_description': 'End-to-end hardware implementation and management services for optimal infrastructure performance.',
    }
    return render(request, 'technology/implementation_services/hardware_implementation_management.html', context)

def software_implementation_management(request):
    """Software Implementation Management page"""
    technology_staff = User.objects.filter(
        technology_solution=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'technology_staff': technology_staff,
        'service_name': 'Software Implementation Management',
        'service_description': 'Professional software implementation services to ensure seamless deployment and integration.',
    }
    return render(request, 'technology/implementation_services/software_implementation_management.html', context)

def software_deployment_management(request):
    """Software Deployment and Management page"""
    technology_staff = User.objects.filter(
        technology_solution=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'technology_staff': technology_staff,
        'service_name': 'Software Deployment and Management',
        'service_description': 'Comprehensive software deployment and ongoing management services for optimal system performance.',
    }
    return render(request, 'technology/implementation_services/software_deployment_management.html', context)

def hardware_deployment_maintenance(request):
    """Hardware Deployment and Maintenance page"""
    technology_staff = User.objects.filter(
        technology_solution=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'technology_staff': technology_staff,
        'service_name': 'Hardware Deployment and Maintenance',
        'service_description': 'Complete hardware deployment and maintenance services to ensure reliable infrastructure operations.',
    }
    return render(request, 'technology/implementation_services/hardware_deployment_maintenance.html', context)

def it_project_management(request):
    """IT Project Management page"""
    technology_staff = User.objects.filter(
        technology_solution=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'technology_staff': technology_staff,
        'service_name': 'IT Project Management',
        'service_description': 'Strategic IT project management to deliver technology initiatives on time and within budget.',
    }
    return render(request, 'technology/implementation_services/it_project_management_main.html', context)

# Security & Consulting Views
def cybersecurity_assessment_management(request):
    """Cybersecurity Assessment and Management page"""
    technology_staff = User.objects.filter(
        technology_solution=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'technology_staff': technology_staff,
        'service_name': 'Cybersecurity Assessment and Management',
        'service_description': 'Comprehensive cybersecurity services to protect your digital assets and ensure regulatory compliance.',
    }
    return render(request, 'technology/security_consulting/cybersecurity_assessment_management.html', context)

def technology_consulting(request):
    """Technology Consulting page"""
    technology_staff = User.objects.filter(
        technology_solution=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'technology_staff': technology_staff,
        'service_name': 'Technology Consulting',
        'service_description': 'Strategic technology consulting to align IT solutions with business objectives and drive digital transformation.',
    }
    return render(request, 'technology/security_consulting/technology_consulting.html', context)

def it_consulting(request):
    """IT Consulting page"""
    technology_staff = User.objects.filter(
        technology_solution=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'technology_staff': technology_staff,
        'service_name': 'IT Consulting',
        'service_description': 'Expert IT consulting services to optimize technology infrastructure and support business growth.',
    }
    return render(request, 'technology/security_consulting/it_consulting.html', context)

def managed_it_service(request):
    """Managed IT Service page"""
    technology_staff = User.objects.filter(
        technology_solution=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'technology_staff': technology_staff,
        'service_name': 'Managed IT Service',
        'service_description': 'Comprehensive managed IT services to ensure reliable, secure, and efficient technology operations.',
    }
    return render(request, 'technology/security_consulting/managed_it_service.html', context)

def it_security(request):
    """IT Security page"""
    technology_staff = User.objects.filter(
        technology_solution=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'technology_staff': technology_staff,
        'service_name': 'IT Security',
        'service_description': 'Robust IT security solutions to protect against cyber threats and ensure data integrity.',
    }
    return render(request, 'technology/security_consulting/it_security.html', context)

# Asset & Support Views
def cybersecurity_main(request):
    """Cybersecurity page"""
    technology_staff = User.objects.filter(
        technology_solution=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'technology_staff': technology_staff,
        'service_name': 'Cybersecurity',
        'service_description': 'Advanced cybersecurity solutions to safeguard your digital infrastructure and sensitive data.',
    }
    return render(request, 'technology/asset_support/cybersecurity.html', context)

def service_desk_help_desk(request):
    """Service Desk/Help Desk page"""
    technology_staff = User.objects.filter(
        technology_solution=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'technology_staff': technology_staff,
        'service_name': 'Service Desk/Help Desk',
        'service_description': 'Professional service desk and help desk support to ensure uninterrupted technology operations.',
    }
    return render(request, 'technology/asset_support/service_desk_help_desk.html', context)

def equipment_supply_setup(request):
    """Equipment Supply and Setup page"""
    technology_staff = User.objects.filter(
        technology_solution=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'technology_staff': technology_staff,
        'service_name': 'Equipment Supply and Setup',
        'service_description': 'Complete equipment supply and setup services for optimal technology infrastructure deployment.',
    }
    return render(request, 'technology/asset_support/equipment_supply_setup.html', context)

def inventory_count_assets_management(request):
    """Inventory Count and Assets Management page"""
    technology_staff = User.objects.filter(
        technology_solution=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'technology_staff': technology_staff,
        'service_name': 'Inventory Count and Assets Management',
        'service_description': 'Comprehensive inventory and asset management solutions to optimize technology resource utilization.',
    }
    return render(request, 'technology/asset_support/inventory_count_assets_management.html', context)

def asset_registry(request):
    """Asset Registry page"""
    technology_staff = User.objects.filter(
        technology_solution=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'technology_staff': technology_staff,
        'service_name': 'Asset Registry',
        'service_description': 'Centralized asset registry services to maintain accurate technology asset records and lifecycle management.',
    }
    return render(request, 'technology/asset_support/asset_registry.html', context)

def barcoding(request):
    """Barcoding page"""
    technology_staff = User.objects.filter(
        technology_solution=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'technology_staff': technology_staff,
        'service_name': 'Barcoding',
        'service_description': 'Efficient barcoding solutions for streamlined asset tracking and inventory management.',
    }
    return render(request, 'technology/asset_support/barcoding.html', context)

def business_process_improvement(request):
    """Business Process Improvement page"""
    technology_staff = User.objects.filter(
        technology_solution=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'technology_staff': technology_staff,
        'service_name': 'Business Process Improvement',
        'service_description': 'Strategic business process optimization to enhance operational efficiency and drive growth.',
    }
    return render(request, 'technology/business_process_improvement.html', context)


# Managed Services Main Views
def managed_service_main(request):
    """Main managed service page"""
    managed_service_staff = User.objects.filter(
        managed_service=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    # ✅ Get regional leaders from database - only active ones
    regional_leaders = RegionalLeader.objects.filter(
        is_active=True
    ).order_by('display_order', 'region')[:8]  # Limit to 8 for the component

    # ✅ Get managing partners from database - only active ones
    managing_partners = ManagingPartner.objects.filter(
        is_active=True
    ).order_by('display_order')[:3]  # Limit to 3

    context = {
        'managed_service_staff': managed_service_staff,
        'regional_leaders': regional_leaders,
        'managing_partners': managing_partners,
    }
    return render(request, 'managed_service/index.html', context)
def managed_service_accounting(request):
    """Accounting Services main page"""
    managed_service_staff = User.objects.filter(
        managed_service=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'managed_service_staff': managed_service_staff,
        'service_name': 'Accounting Services',
        'service_description': 'Comprehensive accounting solutions for your business.',
    }
    return render(request, 'managed_service/accounting_services/index.html', context)

def managed_service_tax(request):
    """Tax Services main page"""
    managed_service_staff = User.objects.filter(
        managed_service=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'managed_service_staff': managed_service_staff,
        'service_name': 'Tax Services',
        'service_description': 'Complete tax planning and compliance services.',
    }
    return render(request, 'managed_service/tax_services/index.html', context)

def managed_service_technology(request):
    """Technology Services main page"""
    managed_service_staff = User.objects.filter(
        managed_service=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'managed_service_staff': managed_service_staff,
        'service_name': 'Technology Services',
        'service_description': 'Comprehensive IT infrastructure and support solutions.',
    }
    return render(request, 'managed_service/technology_services/index.html', context)

# Accounting Services Sub-views
def account_management_bookkeeping_ms(request):
    """Account Management & Bookkeeping page"""
    managed_service_staff = User.objects.filter(
        managed_service=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'managed_service_staff': managed_service_staff,
        'service_name': 'Account Management & Bookkeeping',
        'service_description': 'Professional account management and comprehensive bookkeeping solutions to maintain financial integrity and accuracy.',
    }
    return render(request, 'managed_service/accounting_services/account_management_bookkeeping.html', context)

def financial_statement_preparation(request):
    """Financial Statement Preparation page"""
    managed_service_staff = User.objects.filter(
        managed_service=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'managed_service_staff': managed_service_staff,
        'service_name': 'Financial Statement Preparation',
        'service_description': 'Professional preparation of comprehensive financial statements including balance sheets, income statements, and cash flow statements.',
    }
    return render(request, 'managed_service/accounting_services/financial_statement_preparation.html', context)

def bank_reconciliation(request):
    """Bank Reconciliation page"""
    managed_service_staff = User.objects.filter(
        managed_service=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'managed_service_staff': managed_service_staff,
        'service_name': 'Bank Reconciliation',
        'service_description': 'Accurate and timely bank reconciliation services to ensure financial records match bank statements.',
    }
    return render(request, 'managed_service/accounting_services/bank_reconciliation.html', context)

def account_payable_receivable(request):
    """Account Payable/Receivable page"""
    managed_service_staff = User.objects.filter(
        managed_service=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'managed_service_staff': managed_service_staff,
        'service_name': 'Accounts Payable & Receivable Management',
        'service_description': 'Comprehensive management of accounts payable and receivable to optimize cash flow and vendor relationships.',
    }
    return render(request, 'managed_service/accounting_services/account_payable_receivable.html', context)

def budget_and_forecasting(request):
    """Budget and Forecasting page"""
    managed_service_staff = User.objects.filter(
        managed_service=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'managed_service_staff': managed_service_staff,
        'service_name': 'Budget and Forecasting',
        'service_description': 'Strategic budgeting and financial forecasting services to guide business planning and decision-making.',
    }
    return render(request, 'managed_service/accounting_services/budget_and_forecasting.html', context)

def forensic_accounting_ms(request):
    """Forensic Accounting page"""
    managed_service_staff = User.objects.filter(
        managed_service=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'managed_service_staff': managed_service_staff,
        'service_name': 'Forensic Accounting',
        'service_description': 'Expert forensic accounting services to investigate financial discrepancies, fraud, and ensure financial integrity.',
    }
    return render(request, 'managed_service/accounting_services/forensic_accounting.html', context)

def business_consulting_ms(request):
    """Business Consulting page"""
    managed_service_staff = User.objects.filter(
        managed_service=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'managed_service_staff': managed_service_staff,
        'service_name': 'Business Consulting',
        'service_description': 'Strategic business consulting services to optimize operations, improve efficiency, and drive growth.',
    }
    return render(request, 'managed_service/accounting_services/business_consulting.html', context)

def public_accounting(request):
    """Public Accounting page"""
    managed_service_staff = User.objects.filter(
        managed_service=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'managed_service_staff': managed_service_staff,
        'service_name': 'Public Accounting',
        'service_description': 'Comprehensive public accounting services including audit, tax, and consulting for businesses and individuals.',
    }
    return render(request, 'managed_service/accounting_services/public_accounting.html', context)

# Tax Services Sub-views
def tax_planning_ms(request):
    """Tax Planning page"""
    managed_service_staff = User.objects.filter(
        managed_service=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'managed_service_staff': managed_service_staff,
        'service_name': 'Tax Planning',
        'service_description': 'Strategic tax planning services to minimize tax liability and optimize your financial position.',
    }
    return render(request, 'managed_service/tax_services/tax_planning.html', context)

def payroll_tax(request):
    """Payroll Tax page"""
    managed_service_staff = User.objects.filter(
        managed_service=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'managed_service_staff': managed_service_staff,
        'service_name': 'Payroll Tax Management',
        'service_description': 'Comprehensive payroll tax services including calculation, filing, and compliance management.',
    }
    return render(request, 'managed_service/tax_services/payroll_tax.html', context)

def individual_tax_1040(request):
    """Individual Tax - 1040 page"""
    managed_service_staff = User.objects.filter(
        managed_service=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'managed_service_staff': managed_service_staff,
        'service_name': 'Individual Tax - Form 1040',
        'service_description': 'Complete individual tax preparation and filing services for Form 1040 and related schedules.',
    }
    return render(request, 'managed_service/tax_services/individual_tax_1040.html', context)

def business_tax_1120s_1120(request):
    """Business Tax – 1120s and 1120 page"""
    managed_service_staff = User.objects.filter(
        managed_service=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'managed_service_staff': managed_service_staff,
        'service_name': 'Business Tax – Forms 1120 & 1120S',
        'service_description': 'Comprehensive business tax services for corporations (Form 1120) and S-corporations (Form 1120S).',
    }
    return render(request, 'managed_service/tax_services/business_tax_1120s_1120.html', context)

def nonprofit_tax_990(request):
    """Non-profit Tax – 990 page"""
    managed_service_staff = User.objects.filter(
        managed_service=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'managed_service_staff': managed_service_staff,
        'service_name': 'Non-profit Tax – Form 990',
        'service_description': 'Specialized tax services for non-profit organizations including Form 990 preparation and compliance.',
    }
    return render(request, 'managed_service/tax_services/nonprofit_tax_990.html', context)

def tax_accounting(request):
    """Tax Accounting page"""
    managed_service_staff = User.objects.filter(
        managed_service=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'managed_service_staff': managed_service_staff,
        'service_name': 'Tax Accounting',
        'service_description': 'Professional tax accounting services including provision calculations, deferred taxes, and tax basis accounting.',
    }
    return render(request, 'managed_service/tax_services/tax_accounting.html', context)

def international_tax(request):
    """International Tax page"""
    managed_service_staff = User.objects.filter(
        managed_service=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'managed_service_staff': managed_service_staff,
        'service_name': 'International Tax',
        'service_description': 'Expert international tax services including cross-border transactions, transfer pricing, and treaty analysis.',
    }
    return render(request, 'managed_service/tax_services/international_tax.html', context)

# Technology Services Sub-views
def asset_tracking_management(request):
    """Asset Tracking and Management page"""
    managed_service_staff = User.objects.filter(
        managed_service=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'managed_service_staff': managed_service_staff,
        'service_name': 'Asset Tracking and Management',
        'service_description': 'Comprehensive IT asset tracking and management solutions to optimize technology investments and lifecycle management.',
    }
    return render(request, 'managed_service/technology_services/asset_tracking_management.html', context)

def it_support_management(request):
    """IT Support Management page"""
    managed_service_staff = User.objects.filter(
        managed_service=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'managed_service_staff': managed_service_staff,
        'service_name': 'IT Support Management',
        'service_description': 'Professional IT support management services including help desk, technical support, and system maintenance.',
    }
    return render(request, 'managed_service/technology_services/it_support_management.html', context)

def cybersecurity_ms(request):
    """Cybersecurity page"""
    managed_service_staff = User.objects.filter(
        managed_service=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'managed_service_staff': managed_service_staff,
        'service_name': 'Cybersecurity Services',
        'service_description': 'Comprehensive cybersecurity solutions including threat protection, vulnerability assessment, and security monitoring.',
    }
    return render(request, 'managed_service/technology_services/cybersecurity.html', context)

def network_support_health_check(request):
    """Network Support/Health Check page"""
    managed_service_staff = User.objects.filter(
        managed_service=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'managed_service_staff': managed_service_staff,
        'service_name': 'Network Support & Health Check',
        'service_description': 'Professional network support services including health checks, optimization, and performance monitoring.',
    }
    return render(request, 'managed_service/technology_services/network_support_health_check.html', context)

def inventory(request):
    """Inventory page"""
    managed_service_staff = User.objects.filter(
        managed_service=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    context = {
        'managed_service_staff': managed_service_staff,
        'service_name': 'Inventory Management',
        'service_description': 'Comprehensive inventory management solutions including tracking, optimization, and reporting.',
    }
    return render(request, 'managed_service/technology_services/inventory.html', context)



# Insights Views
def insights_main(request):
    return render(request, 'insights/index.html')

def ai_revolution_business_operations(request):
    return render(request, 'insights/ai_revolution_business_operations.html')

def digital_transformation_strategies(request):
    return render(request, 'insights/digital_transformation_strategies.html')

def esg_compliance_frameworks(request):
    return render(request, 'insights/esg_compliance_frameworks.html')

def remote_workforce_management(request):
    return render(request, 'insights/remote_workforce_management.html')

def tax_law_changes_2024(request):
    return render(request, 'insights/tax_law_changes_2024.html')

def cybersecurity_threat_landscape(request):
    return render(request, 'insights/cybersecurity_threat_landscape.html')

def cloud_migration_best_practices(request):
    return render(request, 'insights/cloud_migration_best_practices.html')

# Industries Views
def industries_main(request):
    return render(request, 'industries/index.html')

def financial_services(request):
    return render(request, 'industries/financial_services.html')

def government_public_sector(request):
    return render(request, 'industries/government_public_sector.html')

def consumer_business(request):
    return render(request, 'industries/consumer_business.html')

def healthcare_industry(request):
    return render(request, 'industries/healthcare.html')

def real_estate_construction(request):
    return render(request, 'industries/real_estate_construction.html')

def non_profit_organizations(request):
    return render(request, 'industries/non_profit_organizations.html')

def manufacturing_industry(request):
    return render(request, 'industries/manufacturing.html')

def professional_service_firms(request):
    return render(request, 'industries/professional_service_firms.html')

def technology_media_telecom(request):
    return render(request, 'industries/technology_media_telecom.html')


# Innovation Views
def innovation_main(request):
    """Main innovation page"""
    # If you have an 'innovation' field in your User model, use it:
    # innovation_staff = User.objects.filter(
    #     innovation=True,
    #     is_active=True,
    #     is_approved=True
    # ).select_related('office')

    # Using advisory field as a proxy for innovation staff
    innovation_staff = User.objects.filter(
        advisory=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    # ✅ Get regional leaders from database - only active ones
    regional_leaders = RegionalLeader.objects.filter(
        is_active=True
    ).order_by('display_order', 'region')[:8]  # Limit to 8 for the component

    # ✅ Get managing partners from database - only active ones
    managing_partners = ManagingPartner.objects.filter(
        is_active=True
    ).order_by('display_order')[:3]  # Limit to 3

    context = {
        'innovation_staff': innovation_staff,
        'regional_leaders': regional_leaders,
        'managing_partners': managing_partners,
    }
    return render(request, 'innovation/index.html', context)
def ai_driven_business_intelligence(request):
    return render(request, 'innovation/ai_driven_business_intelligence.html')

def predictive_analytics_solutions(request):
    return render(request, 'innovation/predictive_analytics_solutions.html')

def natural_language_processing(request):
    return render(request, 'innovation/natural_language_processing.html')

def advanced_threat_protection(request):
    return render(request, 'innovation/advanced_threat_protection.html')

def zero_trust_architecture(request):
    return render(request, 'innovation/zero_trust_architecture.html')

def custom_software_development(request):
    return render(request, 'innovation/custom_software_development.html')

def enterprise_application_integration(request):
    return render(request, 'innovation/enterprise_application_integration.html')

def digital_forensic_tools(request):
    return render(request, 'innovation/digital_forensic_tools.html')

# In your views.py file
def compliance_main(request):
    """Main compliance solutions page"""
    context = {
        'title': 'Compliance Solutions | OB Global',
        'description': 'Comprehensive compliance solutions for regulatory requirements, ESG frameworks, and industry standards.',
    }
    return render(request, 'compliance/compliance_main.html', context)


from django.shortcuts import render, get_object_or_404
from .models import RegionalLeader


def regional_leader_profile(request, leader_id):
    """Individual regional leader profile page using database"""
    leader = get_object_or_404(RegionalLeader, id=leader_id, is_active=True)

    context = {
        'leader': leader,
    }
    return render(request, 'regional_leader_profile.html', context)

def oil_and_gas_industry(request):
    """Oil and Gas Industry page"""
    # Get staff members who work in oil & gas or advisory services
    # You may want to create a specific field for industries later
    industry_staff = User.objects.filter(
        advisory=True,  # Using advisory as a proxy filter for now
        is_active=True,
        is_approved=True
    ).select_related('office')

    # Industry-specific data
    industry_data = {
        'name': 'Oil and Gas',
        'tagline': 'Expert solutions for the energy sector',
        'description': 'Comprehensive services for exploration, production, refining, and distribution.',
        'stats': [
            {'value': '20+', 'label': 'Years in Energy Sector'},
            {'value': '150+', 'label': 'Energy Projects'},
            {'value': '98%', 'label': 'Client Satisfaction'},
        ],
        # Add any other data your template needs
    }

    context = {
        'industry_staff': industry_staff,
        'industry': industry_data,
        'industry_name': industry_data['name'],
        'industry_tagline': industry_data['tagline'],
    }

    return render(request, 'industries/oil_and_gas.html', context)


# Add this to your views.py after other views

def executive_leadership(request):
    """Executive Leadership page focusing on company-wide capabilities"""
    # Get executive team members (users with executive_team=True)
    executives = User.objects.filter(
        executive_team=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    # Regional leaders data
    regional_leaders = [
        {
            'id': 1,
            'first_name': 'Sarah',
            'last_name': 'Johnson',
            'profile_image': 'https://i.pinimg.com/1200x/77/31/a1/7731a10b118bb5b0a0c77bc6f8544bfa.jpg',
            'email': 'sarah.johnson@obglobal.com',
            'linkedin': 'https://linkedin.com/in/sarahjohnson'
        },
        {
            'id': 2,
            'first_name': 'David',
            'last_name': 'Chen',
            'profile_image': 'https://i.pinimg.com/736x/ae/e6/d4/aee6d45245609592339c8508ae27182d.jpg',
            'email': 'david.chen@obglobal.com',
            'linkedin': 'https://linkedin.com/in/davidchen'
        },
        {
            'id': 3,
            'first_name': 'Amina',
            'last_name': 'Diallo',
            'profile_image': 'https://i.pinimg.com/736x/ae/e6/d4/aee6d45245609592339c8508ae27182d.jpg',
            'email': 'amina.diallo@obglobal.com',
            'linkedin': 'https://linkedin.com/in/aminadiallo'
        },
        {
            'id': 4,
            'first_name': 'Kwame',
            'last_name': 'Osei',
            'profile_image': 'https://i.pinimg.com/736x/ae/e6/d4/aee6d45245609592339c8508ae27182d.jpg',
            'email': 'kwame.osei@obglobal.com',
            'linkedin': 'https://linkedin.com/in/kwameosei'
        },
        {
            'id': 5,
            'first_name': 'Fatima',
            'last_name': 'Bello',
            'profile_image': 'https://i.pinimg.com/736x/ae/e6/d4/aee6d45245609592339c8508ae27182d.jpg',
            'email': 'fatima.bello@obglobal.com',
            'linkedin': 'https://linkedin.com/in/fatimabello'
        }
    ]

    context = {
        'executives': executives,
        'regional_leaders': regional_leaders,
    }

    return render(request, 'about/leadership.html', context)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Office, OfficeDetail
from .forms import OfficeDetailForm


def is_admin_or_staff(user):
    """Check if user is admin or staff"""
    return user.is_authenticated and user.role in ['admin', 'staff']


@login_required
@user_passes_test(is_admin_or_staff)
def manage_office_details(request, office_id):
    """
    Main view to manage office details - shows existing details or form to create new ones
    """
    office = get_object_or_404(Office, id=office_id)

    # Try to get existing details, or None if they don't exist
    try:
        office_details = OfficeDetail.objects.get(office=office)
        form = None  # We'll show details instead of form
    except OfficeDetail.DoesNotExist:
        office_details = None
        form = OfficeDetailForm()

    if request.method == 'POST':
        if office_details:
            # Update existing details
            form = OfficeDetailForm(request.POST, request.FILES, instance=office_details)
        else:
            # Create new details
            form = OfficeDetailForm(request.POST, request.FILES)

        if form.is_valid():
            office_detail = form.save(commit=False)
            office_detail.office = office
            office_detail.save()

            action = "updated" if office_details else "added"
            messages.success(request, f"Office details {action} successfully!")
            return redirect('manage_office_details', office_id=office.id)

    context = {
        'office': office,
        'office_details': office_details,
        'form': form,
    }
    return render(request, 'manage/office_details.html', context)


from django.shortcuts import render, get_object_or_404
from .models import Office, OfficeDetail


def office_detailed_view(request, office_id):
    """
    Detailed view for a single office showing all associated information
    """
    office = get_object_or_404(Office, id=office_id)

    # Try to get office details if they exist
    try:
        office_details = OfficeDetail.objects.get(office=office)
    except OfficeDetail.DoesNotExist:
        office_details = None

    # Get all staff members assigned to this office
    office_staff = User.objects.filter(
        office=office,
        is_active=True,
        is_approved=True
    ).select_related('office')

    # Get executives in this office
    executives_in_office = User.objects.filter(
        office=office,
        executive_team=True,
        is_active=True,
        is_approved=True
    ).select_related('office')

    # Create Google Maps link for full view (if embed URL exists)
    large_map_url = None
    if office.google_map_url and 'maps/embed' in office.google_map_url.lower():
        large_map_url = office.google_map_url.replace('/embed', '/place')

    context = {
        'office': office,
        'office_details': office_details,
        'office_staff': office_staff,
        'executives_in_office': executives_in_office,
        'large_map_url': large_map_url,
    }

    return render(request, 'office_detail_page.html', context)

@login_required
@user_passes_test(is_admin_or_staff)
def edit_office_details(request, office_id):
    """
    Edit existing office details
    """
    office = get_object_or_404(Office, id=office_id)
    office_details = get_object_or_404(OfficeDetail, office=office)

    if request.method == 'POST':
        form = OfficeDetailForm(request.POST, request.FILES, instance=office_details)
        if form.is_valid():
            form.save()
            messages.success(request, "Office details updated successfully!")
            return redirect('manage_office_details', office_id=office.id)
    else:
        form = OfficeDetailForm(instance=office_details)

    context = {
        'office': office,
        'office_details': office_details,
        'form': form,
        'edit_mode': True,
    }
    return render(request, 'manage/edit_office_details.html', context)


@login_required
@user_passes_test(is_admin_or_staff)
def delete_office_details(request, office_id):
    """
    Delete office details
    """
    office = get_object_or_404(Office, id=office_id)
    office_details = get_object_or_404(OfficeDetail, office=office)

    if request.method == 'POST':
        office_name = office.office_Name
        office_details.delete()
        messages.success(request, f"Office details for {office_name} deleted successfully!")
        return redirect('manage_offices')

    context = {
        'office': office,
        'office_details': office_details,
    }
    return render(request, 'manage/delete_office_details.html', context)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from .models import RegionalLeader, ManagingPartner
from .forms import RegionalLeaderForm, ManagingPartnerForm


def is_admin(user):
    return user.is_authenticated and user.role == 'admin'


# Combined Leader Management Views
@login_required
@user_passes_test(is_admin)
def manage_regional_leaders(request):
    """View all regional leaders and managing partners"""
    regional_leaders = RegionalLeader.objects.filter(is_active=True).order_by('display_order', 'region')
    inactive_regional_leaders = RegionalLeader.objects.filter(is_active=False).order_by('display_order', 'region')

    managing_partners = ManagingPartner.objects.filter(is_active=True).order_by('display_order')
    inactive_managing_partners = ManagingPartner.objects.filter(is_active=False).order_by('display_order')

    search_query = request.GET.get('search', '')
    if search_query:
        regional_leaders = regional_leaders.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(region__icontains=search_query) |
            Q(email__icontains=search_query)
        )
        managing_partners = managing_partners.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    context = {
        'regional_leaders': regional_leaders,
        'inactive_regional_leaders': inactive_regional_leaders,
        'managing_partners': managing_partners,
        'inactive_managing_partners': inactive_managing_partners,
        'search_query': search_query,
    }
    return render(request, 'manage/manage_regional_leaders.html', context)


@login_required
@user_passes_test(is_admin)
def add_regional_leader(request):
    """Add a new regional leader or managing partner"""
    leader_type = request.GET.get('type', 'regional_leader')

    # Determine if it's a managing partner
    is_managing_partner = leader_type == 'managing_partner'

    if request.method == 'POST':
        if is_managing_partner:
            form = ManagingPartnerForm(request.POST, request.FILES)
            success_message = 'Managing Partner'
            success_redirect = 'manage_regional_leaders'
        else:
            form = RegionalLeaderForm(request.POST, request.FILES)
            success_message = 'Regional Leader'
            success_redirect = 'manage_regional_leaders'

        if form.is_valid():
            leader = form.save()
            messages.success(request, f'{success_message} {leader.get_full_name()} added successfully!')
            return redirect(success_redirect)
        else:
            # Store form errors in JSON format for JavaScript handling
            form_errors = {}
            for field, errors in form.errors.items():
                if errors:
                    form_errors[field] = errors[0]

            # If form is invalid, we need to set page_title based on leader_type
            if is_managing_partner:
                page_title = 'Add Managing Partner'
            else:
                page_title = 'Add Regional Leader'

    else:
        # Initial form load
        if is_managing_partner:
            form = ManagingPartnerForm(
                initial={
                    'display_order': 0,
                    'is_active': True,
                    'leader_type': 'managing_partner'
                }
            )
            page_title = 'Add Managing Partner'
        else:
            form = RegionalLeaderForm(
                initial={
                    'display_order': 0,
                    'is_active': True,
                    'leader_type': 'regional_leader'
                }
            )
            page_title = 'Add Regional Leader'

        # No form errors on initial load
        form_errors = {}

    # Convert form errors to JSON for JavaScript
    form_errors_json = json.dumps(form_errors)

    context = {
        'form': form,
        'page_title': page_title,
        'is_managing_partner': is_managing_partner,
        'leader_type': leader_type,
        'form_errors_json': form_errors_json,
    }

    return render(request, 'manage/regional_leader_form.html', context)


@login_required
@user_passes_test(is_admin)
def edit_regional_leader(request, leader_id):
    """Edit an existing regional leader or managing partner"""

    # Initialize variables
    leader = None
    is_managing_partner = False
    form_class = None
    form_errors = {}

    # Try to get as RegionalLeader first
    try:
        leader = RegionalLeader.objects.get(id=leader_id)
        is_managing_partner = False
        form_class = RegionalLeaderForm
        page_title = f'Edit Regional Leader - {leader.get_full_name()}'
        success_message = 'Regional Leader'
    except RegionalLeader.DoesNotExist:
        # Try to get as ManagingPartner
        try:
            leader = ManagingPartner.objects.get(id=leader_id)
            is_managing_partner = True
            form_class = ManagingPartnerForm
            page_title = f'Edit Managing Partner - {leader.get_full_name()}'
            success_message = 'Managing Partner'
        except ManagingPartner.DoesNotExist:
            raise Http404("Leader not found")

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=leader)
        if form.is_valid():
            updated_leader = form.save()
            messages.success(request, f'{success_message} {updated_leader.get_full_name()} updated successfully!')
            return redirect('manage_regional_leaders')
        else:
            # Store form errors in JSON format for JavaScript handling
            for field, errors in form.errors.items():
                if errors:
                    form_errors[field] = errors[0]
            # Keep the same page_title since form is invalid
    else:
        form = form_class(instance=leader)

    # Convert form errors to JSON for JavaScript
    form_errors_json = json.dumps(form_errors)

    context = {
        'form': form,
        'leader': leader,
        'page_title': page_title,
        'is_managing_partner': is_managing_partner,
        'form_errors_json': form_errors_json,
        'existing_profile_image': leader.get_profile_image_url() if leader.profile_image else '',
    }

    return render(request, 'manage/regional_leader_form.html', context)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, Http404
from .models import RegionalLeader, ManagingPartner
import cloudinary.uploader  # For deleting Cloudinary images


@login_required
@user_passes_test(is_admin)
def view_regional_leader(request, leader_id):
    """View detailed information about a regional leader or managing partner"""
    leader = None
    leader_type = 'regional_leader'

    # Try to get as regional leader first
    try:
        leader = RegionalLeader.objects.get(id=leader_id)
        leader_type = 'regional_leader'
    except RegionalLeader.DoesNotExist:
        # If not found as regional leader, try as managing partner
        try:
            leader = ManagingPartner.objects.get(id=leader_id)
            leader_type = 'managing_partner'
        except ManagingPartner.DoesNotExist:
            raise Http404("Leader not found")

    context = {
        'leader': leader,
        'leader_type': leader_type,
    }
    return render(request, 'manage/view_regional_leader.html', context)


@login_required
@user_passes_test(is_admin)
def delete_regional_leader(request, leader_id):
    """Handle both deactivation and permanent deletion of leaders"""
    leader = None
    is_managing_partner = False
    leader_type = 'Regional Leader'

    # Try to get as regional leader first
    try:
        leader = RegionalLeader.objects.get(id=leader_id)
        is_managing_partner = False
        leader_type = 'Regional Leader'
    except RegionalLeader.DoesNotExist:
        # If not found as regional leader, try as managing partner
        try:
            leader = ManagingPartner.objects.get(id=leader_id)
            is_managing_partner = True
            leader_type = 'Managing Partner'
        except ManagingPartner.DoesNotExist:
            raise Http404("Leader not found")

    if request.method == 'POST':
        # Check if this is a permanent delete
        if request.POST.get('permanent') == 'true':
            # Permanent delete - remove from database
            leader_name = leader.get_full_name()

            # Delete profile image from Cloudinary if exists
            if hasattr(leader, 'profile_image') and leader.profile_image:
                try:
                    cloudinary.uploader.destroy(leader.profile_image.public_id)
                except:
                    pass  # Silently fail if image deletion fails

            leader.delete()
            messages.success(request, f'{leader_type} {leader_name} permanently deleted from the system!')
        else:
            # Soft delete (deactivation) - just mark as inactive
            leader.is_active = False
            leader.save()
            messages.success(request, f'{leader_type} {leader.get_full_name()} deactivated successfully!')

        return redirect('manage_regional_leaders')

    context = {
        'leader': leader,
        'leader_type': leader_type,
        'is_managing_partner': is_managing_partner,
    }

    # If permanent delete is requested, show a different template
    if request.GET.get('permanent') == 'true':
        return render(request, 'manage/delete_regional_leader.html', context)

    return render(request, 'manage/deactivate_regional_leader.html', context)


@login_required
@user_passes_test(is_admin)
def activate_regional_leader(request, leader_id):
    """Reactivate a regional leader or managing partner"""
    leader = None
    is_managing_partner = False
    leader_type = 'Regional Leader'

    # Try to get as regional leader first
    try:
        leader = RegionalLeader.objects.get(id=leader_id)
        is_managing_partner = False
        leader_type = 'Regional Leader'
    except RegionalLeader.DoesNotExist:
        # If not found as regional leader, try as managing partner
        try:
            leader = ManagingPartner.objects.get(id=leader_id)
            is_managing_partner = True
            leader_type = 'Managing Partner'
        except ManagingPartner.DoesNotExist:
            raise Http404("Leader not found")

    leader.is_active = True
    leader.save()
    messages.success(request, f'{leader_type} {leader.get_full_name()} activated successfully!')
    return redirect('manage_regional_leaders')


# Public profile view for both leader types
def regional_leader_profile(request, leader_id):
    """Public profile view for regional leaders and managing partners"""
    leader = None
    leader_type = 'regional_leader'

    # Try to get as regional leader first
    try:
        leader = RegionalLeader.objects.get(id=leader_id, is_active=True)
        leader_type = 'regional_leader'
    except RegionalLeader.DoesNotExist:
        # If not found as regional leader, try as managing partner
        try:
            leader = ManagingPartner.objects.get(id=leader_id, is_active=True)
            leader_type = 'managing_partner'
        except ManagingPartner.DoesNotExist:
            raise Http404("Leader not found")

    context = {
        'leader': leader,
        'leader_type': leader_type,
        # Add these additional context variables if your template needs them
        'page_title': f"{leader.first_name} {leader.last_name} | OB Global",
        'meta_description': f"Professional profile of {leader.first_name} {leader.last_name}, {'Regional Leader' if leader_type == 'regional_leader' else 'Managing Partner'} at OB Global",
    }

    # Use the correct template path based on your file location
    # Your file is at: core/templates/regional_leader_profile.html
    return render(request, 'regional_leader_profile.html', context)
@login_required
@user_passes_test(is_admin)
def permanent_delete_regional_leader(request, leader_id):
    leader = get_object_or_404(RegionalLeader, id=leader_id)
    if request.method == 'DELETE':
        leader.delete()
        return JsonResponse({'success': True, 'message': 'Regional leader permanently deleted'})
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

@login_required
@user_passes_test(is_admin)
def permanent_delete_managing_partner(request, leader_id):
    partner = get_object_or_404(ManagingPartner, id=leader_id)
    if request.method == 'DELETE':
        partner.delete()
        return JsonResponse({'success': True, 'message': 'Managing partner permanently deleted'})
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

# Combined permanent delete view for both leader types
@login_required
@user_passes_test(is_admin)
def permanent_delete_leader(request, leader_id):
    """Permanently delete a leader (regional leader or managing partner) via AJAX"""
    leader = None
    leader_type = ''

    # Try to get as regional leader first
    try:
        leader = RegionalLeader.objects.get(id=leader_id)
        leader_type = 'Regional Leader'
    except RegionalLeader.DoesNotExist:
        # If not found as regional leader, try as managing partner
        try:
            leader = ManagingPartner.objects.get(id=leader_id)
            leader_type = 'Managing Partner'
        except ManagingPartner.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Leader not found'}, status=404)

    if request.method == 'DELETE':
        leader_name = leader.get_full_name()

        # Delete profile image from Cloudinary if exists
        if hasattr(leader, 'profile_image') and leader.profile_image:
            try:
                cloudinary.uploader.destroy(leader.profile_image.public_id)
            except:
                pass  # Silently fail if image deletion fails

        leader.delete()
        return JsonResponse({
            'success': True,
            'message': f'{leader_type} {leader_name} permanently deleted'
        })

    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)


# Remove or comment out these separate views (they're now combined into permanent_delete_leader):
# @login_required
# @user_passes_test(is_admin)
# def permanent_delete_regional_leader(request, leader_id):
#     leader = get_object_or_404(RegionalLeader, id=leader_id)
#     if request.method == 'DELETE':
#         leader.delete()
#         return JsonResponse({'success': True, 'message': 'Regional leader permanently deleted'})
#     return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

# @login_required
# @user_passes_test(is_admin)
# def permanent_delete_managing_partner(request, leader_id):
#     partner = get_object_or_404(ManagingPartner, id=leader_id)
#     if request.method == 'DELETE':
#         partner.delete()
#         return JsonResponse({'success': True, 'message': 'Managing partner permanently deleted'})
#     return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)



def sport_entertainment_industry(request):
    context = {
        'title': 'Sport & Entertainment Industry',
        'description': 'Specialized services for sports teams, entertainment companies, venues, and media rights.',
        'services': [
            'Sport and Entertainment Audit',
            'Media Rights Valuation',
            'Sponsorship Revenue Analysis',
            'Venue Management Consulting',
            'Player Contract Analysis',
            'Event Financial Management'
        ]
    }
    return render(request, 'industries/sport_entertainment.html', context)

def marine_industry(request):
    context = {
        'title': 'Marine & Maritime Industry',
        'description': 'Expert services for shipping, ports, offshore operations, and maritime logistics.',
        'services': [
            'Maritime Compliance Audit',
            'Port Operations Analysis',
            'Shipping Financial Management',
            'Offshore Asset Valuation',
            'Marine Insurance Consulting',
            'Supply Chain Optimization'
        ]
    }
    return render(request, 'industries/marine.html', context)

def aerospace_industry(request):
    context = {
        'title': 'Aerospace & Aviation Industry',
        'description': 'Specialized solutions for aircraft manufacturing, airline operations, and aerospace defense.',
        'services': [
            'Aerospace Manufacturing Audit',
            'Airline Operations Analysis',
            'Aircraft Lease Accounting',
            'Defense Contract Compliance',
            'Aviation Tax Advisory',
            'Maintenance Cost Optimization'
        ]
    }
    return render(request, 'industries/aerospace.html', context)