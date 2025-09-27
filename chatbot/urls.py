from django.urls import path
from . import views

urlpatterns = [
    # Route for the main chatbot interface
    path('chat/', views.chatbot_view, name='chatbot_view'),

    # API endpoint for sending and processing messages
    path('api/', views.chatbot_api, name='chatbot_api'),
]