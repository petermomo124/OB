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
def index(request):
    return render(request, 'index.html')

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


@csrf_protect
def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Validate required fields
        if not email or not password:
            messages.error(request, 'Both email and password are required.')
            return render(request, 'client_portal/login.html')

        # Validate email format
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Please enter a valid email address.')
            return render(request, 'client_portal/login.html')

        # Authenticate user
        user = authenticate(request, email=email, password=password)

        if user is not None:
            # Check if user is approved
            if not user.is_approved:
                messages.error(request, 'Your account has not been approved yet. Please contact administrator.')
                return render(request, 'client_portal/login.html')

            # Check if user is active
            if not user.is_active:
                messages.error(request, 'Your account is inactive. Please contact administrator.')
                return render(request, 'client_portal/login.html')

            # Login successful
            login(request, user)
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