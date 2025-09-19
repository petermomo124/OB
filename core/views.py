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

@login_required
def dashboard(request):
    # Retrieve the currently logged-in user
    current_user = request.user

    # Initialize variables for the counts
    total_users = None
    total_clients = None
    total_staffs = None

    # Check if the user is an admin before performing calculations
    if current_user.role == 'admin':
        # Perform the calculations
        total_users = User.objects.count()
        total_clients = User.objects.filter(role='client').count()
        total_staffs = User.objects.filter(is_staff=True).count()
        # You can adjust the filter for staffs based on your model field (e.g., role='staff')

    context = {
        'user': current_user,
        'total_users': total_users,
        'total_clients': total_clients,
        'total_staffs': total_staffs,
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

@login_required
@user_passes_test(is_admin)
def update_user(request, user_id):
    # Retrieve the user to be updated
    user_to_update = get_object_or_404(User, id=user_id)
    offices = Office.objects.all()

    if request.method == 'POST':
        # --- Form Validation and Data Retrieval ---
        # NOTE: All the validation logic below is correct, but could be cleaner
        # and more robust using a Django ModelForm. For now, we'll assume
        # you want to stick with this manual method.
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        date_of_birth_str = request.POST.get('date_of_birth')
        nationality = request.POST.get('nationality')
        role = request.POST.get('role')
        office_id = request.POST.get('office')

        # New password fields
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
                messages.error(request, 'Phone number must start with "+", contain only digits after the plus sign, and be at least 9 digits long.')
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
        user_to_update.executive_position_description = request.POST.get('executive_position_description', user_to_update.executive_position_description)

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
        return redirect('manage_users')

    context = {
        'user_to_update': user_to_update,
        'offices': offices,
        'roles': User.ROLE_CHOICES,
    }
    return render(request, 'admin/update_user.html', context)
@login_required
@user_passes_test(is_admin)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        email = user.email
        user.delete()
        messages.success(request, f'User {email} deleted successfully.')
        return redirect('manage_users')

    return render(request, 'admin/delete_user.html', {'user': user})


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

        # Handle optional fields
        user.linkedin = request.POST.get('linkedin', '')
        user.company_impact = request.POST.get('company_impact', '')
        user.office_impact = request.POST.get('office_impact', '')
        user.field_position = request.POST.get('field_position', '')
        user.executive_position_description = request.POST.get('executive_position_description', '')

        # Handle boolean fields
        user.is_active = 'is_active' in request.POST
        user.is_approved = 'is_approved' in request.POST
        user.is_staff = 'is_staff' in request.POST
        user.executive_team = 'executive_team' in request.POST
        user.audit = 'audit' in request.POST
        user.tax = 'tax' in request.POST
        user.consulting = 'consulting' in request.POST
        user.forensic_service = 'forensic_service' in request.POST
        user.managed_service = 'managed_service' in request.POST
        user.technology_solution = 'technology_solution' in request.POST
        user.advisory = 'advisory' in request.POST

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

