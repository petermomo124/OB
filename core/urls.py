from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [

 # Task Management URLs
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:task_id>/', views.task_detail, name='task_detail'),
    path('tasks/<int:task_id>/update/', views.task_update, name='task_update'),
    path('tasks/<int:task_id>/delete/', views.task_delete, name='task_delete'),
    path('tasks/<int:task_id>/add-file/', views.task_add_file, name='task_add_file'),
    path('tasks/<int:task_id>/delete-file/<int:file_id>/', views.task_delete_file, name='task_delete_file'),
    path('tasks/<int:task_id>/delete-file/<int:file_id>/', views.task_delete_file, name='task_delete_file'),
    path('tasks/<int:task_id>/download-file/<int:file_id>/', views.task_download_file, name='task_download_file'),
    path('tasks/<int:task_id>/feedback/', views.task_feedback, name='task_feedback'),
    path('tasks/<int:task_id>/clear-feedback/', views.task_clear_feedback, name='task_clear_feedback'),

    path('client-portal/password-reset/', views.forgot_password, name='forgot_password'),
    path('client-portal/verify-otp/', views.verify_otp, name='verify_otp'),
    path('client-portal/reset-password/', views.reset_password, name='reset_password'),

    path('user-profile/<int:user_id>/', views.user_profile, name='user_profile'),

# User Management - Changed from 'admin/' to 'manage/'
    path('manage/users/', views.manage_users, name='manage_users'),
    path('manage/user/<int:user_id>/', views.user_detail, name='user_detail'),
    path('manage/user/<int:user_id>/update/', views.update_user, name='update_user'),
    path('manage/user/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('manage/user/add/', views.add_user, name='add_user'),

    path('client-portal/signup/', views.signup_view, name='signup'),

    # Authentication URLs - ADD THESE 3 LINES
    path('client-portal/login/', views.user_login, name='user_login'),
    path('client-portal/dashboard/', views.dashboard, name='dashboard'),
    path('client-portal/logout/', views.user_logout, name='user_logout'),
    # Home
    path('', views.index, name='index'),
    
    # Services
    path('services/', TemplateView.as_view(template_name='services/index.html'), name='services'),
    path('services/audit/', views.service_detail, {'service_slug': 'audit'}, name='audit_service'),
    path('services/tax/', TemplateView.as_view(template_name='services/tax.html'), name='tax_service'),
    path('services/consulting/', TemplateView.as_view(template_name='services/consulting.html'), name='consulting_service'),
    path('services/advisory/', TemplateView.as_view(template_name='services/advisory.html'), name='advisory_service'),
    path('services/technology/', TemplateView.as_view(template_name='services/technology.html'), name='technology_service'),
    path('services/managed/', TemplateView.as_view(template_name='services/managed.html'), name='managed_service'),
    
    # Industries
    path('industries/', TemplateView.as_view(template_name='industries/index.html'), name='industries'),
    path('industries/<slug:industry_slug>/', views.industry_detail, name='industry_detail'),
    
    # About
    path('about/', TemplateView.as_view(template_name='about/index.html'), name='about'),
    
    # Careers
    path('careers/', TemplateView.as_view(template_name='careers/index.html'), name='careers'),
    
    # Insights
    path('insights/', TemplateView.as_view(template_name='insights/index.html'), name='insights'),
    
    # Regional Presence
    path('about/global-presence/', TemplateView.as_view(template_name='regional/index.html'), name='global_presence'),
    
    # Contact
    path('contact/', views.contact_us, name='contact'),
    path('privacy-policy/', views.privacy_policy, name='privacy'),

    # Client Portal
    path('client-portal/', views.user_login, name='client_portal'),
    # Subscription
    path('subscribe/', views.subscribe_redirect, name='subscribe'), # Replaces the old static view

    path('profile/', views.view_my_profile, name='view_my_profile'),
    path('profile/edit/', views.edit_my_profile, name='edit_my_profile'),


# 🏢 NEW OFFICE MANAGEMENT URLS
    path('manage/offices/', views.manage_offices, name='manage_offices'),
    path('manage/offices/add/', views.add_office, name='add_office'),
    path('manage/offices/<int:office_id>/view/', views.view_office, name='view_office'),
    path('manage/offices/<int:office_id>/edit/', views.edit_office, name='edit_office'),
    path('manage/offices/<int:office_id>/delete/', views.delete_office, name='delete_office'),

# core/urls.py - Add these URL patterns

# Advisory URLs
path('advisory/', views.advisory_main, name='advisory_main'),

# Forensic Services
path('advisory/forensic-accounting/', views.forensic_accounting, name='forensic_accounting'),
path('advisory/forensic-audit-investigation/', views.forensic_audit_investigation, name='forensic_audit_investigation'),

# Financial Accounting Outsourcing
path('advisory/forensic-accounting/cfo-service/', views.cfo_service, name='cfo_service'),
path('advisory/forensic-accounting/bookkeeping-service/', views.bookkeeping_service, name='bookkeeping_service'),
path('advisory/forensic-accounting/tax-planning-advisory/', views.tax_planning_advisory, name='tax_planning_advisory'),
path('advisory/forensic-accounting/internal-control-sox-compliance/', views.internal_control_sox_compliance, name='internal_control_sox_compliance'),

# Forensic Audit Investigation
path('advisory/forensic-audit-investigation/payroll-processing-management/', views.payroll_processing_management, name='payroll_processing_management'),
path('advisory/forensic-audit-investigation/account-management-bookkeeping/', views.account_management_bookkeeping, name='account_management_bookkeeping'),

# Advisory Services
path('advisory/tax-planning-advisory/', views.tax_planning_advisory_main, name='tax_planning_advisory_main'),
path('advisory/financial-accounting-advisory/', views.financial_accounting_advisory, name='financial_accounting_advisory'),
path('advisory/internal-control-sox-compliance/', views.internal_control_sox_compliance_main, name='internal_control_sox_compliance_main'),

# API Endpoint for Staff Modal
path('api/staff/<int:staff_id>/', views.get_staff_details, name='get_staff_details'),



# Technology Solutions URLs
path('technology/', views.technology_main, name='technology_main'),

# Implementation Services
path('technology/it-project-management-service/', views.it_project_management_service, name='it_project_management_service'),
path('technology/hardware-implementation-management/', views.hardware_implementation_management, name='hardware_implementation_management'),
path('technology/software-implementation-management/', views.software_implementation_management, name='software_implementation_management'),
path('technology/software-deployment-management/', views.software_deployment_management, name='software_deployment_management'),
path('technology/hardware-deployment-maintenance/', views.hardware_deployment_maintenance, name='hardware_deployment_maintenance'),
path('technology/it-project-management/', views.it_project_management, name='it_project_management'),

# Security & Consulting
path('technology/cybersecurity-assessment-management/', views.cybersecurity_assessment_management, name='cybersecurity_assessment_management'),
path('technology/technology-consulting/', views.technology_consulting, name='technology_consulting'),
path('technology/it-consulting/', views.it_consulting, name='it_consulting'),
path('technology/managed-it-service/', views.managed_it_service, name='managed_it_service'),
path('technology/it-security/', views.it_security, name='it_security'),

# Asset & Support
path('technology/cybersecurity/', views.cybersecurity_main, name='cybersecurity_main'),
path('technology/service-desk-help-desk/', views.service_desk_help_desk, name='service_desk_help_desk'),
path('technology/equipment-supply-setup/', views.equipment_supply_setup, name='equipment_supply_setup'),
path('technology/inventory-count-assets-management/', views.inventory_count_assets_management, name='inventory_count_assets_management'),
path('technology/asset-registry/', views.asset_registry, name='asset_registry'),
path('technology/barcoding/', views.barcoding, name='barcoding'),

    path('business-process-improvement/', views.business_process_improvement, name='business_process_improvement'),
]
