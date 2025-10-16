from django.urls import path
from . import views

urlpatterns = [
    # Client-facing views (CRUD)
    path('', views.rfp_list, name='rfp_list'),
    path('new/', views.rfp_create, name='rfp_create'),
    path('<int:pk>/', views.rfp_detail, name='rfp_detail'),
    path('<int:pk>/edit/', views.rfp_update, name='rfp_update'),

    # File handling views
    path('<int:rfp_pk>/add-file/', views.rfp_add_file, name='rfp_add_file'),
    path('<int:rfp_pk>/delete-file/<int:file_pk>/', views.rfp_delete_file, name='rfp_delete_file'),

    # Admin-only delete
    path('<int:pk>/delete/', views.rfp_delete, name='rfp_delete'),
path(
        '<int:rfp_pk>/download-file/<int:file_pk>/',
        views.rfp_download_file,
        name='rfp_download_file'
    ),

# Add this to your urls.py
path('rfp-guide/', views.rfp_guide, name='rfp_guide'),
    path('<int:rfp_pk>/edit-docx/<int:file_pk>/', views.rfp_edit_docx, name='rfp_edit_docx'),
    path('<int:rfp_pk>/download-for-edit/<int:file_pk>/', views.rfp_download_for_edit, name='rfp_download_for_edit'),
    path('<int:rfp_pk>/finish-edit/<int:file_pk>/', views.rfp_finish_edit, name='rfp_finish_edit'),
    path('<int:rfp_pk>/replace-file/<int:file_pk>/', views.rfp_replace_file, name='rfp_replace_file'),
    path('rfp/upload-image/', views.upload_image, name='upload_image'),


path('rfp/<int:rfp_pk>/file/<int:file_pk>/download-original-docx/', views.rfp_download_original_docx, name='rfp_download_original_docx'),
]
