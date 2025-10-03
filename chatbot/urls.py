from django.urls import path
from . import views

urlpatterns = [
    # Route for the main chatbot interface
    path('chat/', views.chatbot_view, name='chatbot_view'),

    # API endpoint for sending and processing messages
    path('api/', views.chatbot_api, name='chatbot_api'),
    # 🔑 NEW: Route for the public, non-saving chatbot interface
    path('chat/public/', views.public_chatbot_view, name='public_chatbot_view'),

    # 🔑 NEW: API endpoint for public, non-saving messages
    path('api/public/', views.public_chatbot_api, name='public_chatbot_api'),
]