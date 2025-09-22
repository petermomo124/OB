# newsletter/urls.py

from django.urls import path
from . import views

app_name = 'newsletter'

urlpatterns = [
    path('subscribers/<int:pk>/update/', views.update_subscriber, name='update_subscriber'),
    path('newsletters/<int:pk>/update/', views.update_newsletter, name='update_newsletter'),

    # Public-facing views
    path('subscribe/', views.newsletter_subscribe, name='subscribe'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),

    # Admin Dashboard main page
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Paths for managing subscribers
    path('admin/subscribers/', views.subscriber_list, name='subscriber_list'),
    path('subscribers/<int:pk>/', views.subscriber_detail, name='subscriber_detail'),
    path('subscribers/<int:pk>/delete/', views.delete_subscriber, name='delete_subscriber'),

    # Paths for managing newsletters
    path('admin/newsletters/', views.newsletter_list, name='newsletter_list'),
    path('newsletters/create/', views.create_newsletter, name='create_newsletter'),
    path('newsletters/<int:pk>/', views.newsletter_detail, name='newsletter_detail'),
    path('newsletters/<int:pk>/delete/', views.delete_newsletter, name='delete_newsletter'),
    path('newsletters/<int:pk>/send/', views.send_newsletter, name='send_newsletter'),
]