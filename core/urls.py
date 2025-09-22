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
    path('contact/', TemplateView.as_view(template_name='contact/index.html'), name='contact'),
    
    # Client Portal
    path('client-portal/', views.user_login, name='client_portal'),
    # Subscription
    path('subscribe/', views.subscribe_redirect, name='subscribe'), # Replaces the old static view
    
    # RFP
    path('rfp/', TemplateView.as_view(template_name='rfp/request.html'), name='request_proposal'),
]
