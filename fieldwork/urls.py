from django.urls import path
from . import views

app_name = 'fieldwork'

urlpatterns = [
    # Admin URLs
    path('', views.field_job_list, name='field_job_list'),
    path('create/', views.field_job_create, name='field_job_create'),
    path('edit/<int:pk>/', views.field_job_edit, name='field_job_edit'),
    path('delete/<int:pk>/', views.field_job_delete, name='field_job_delete'),
    path('search-staff/', views.search_staff, name='search_staff'),

    # Staff URLs
    path('staff-jobs/', views.staff_field_jobs, name='staff_field_jobs'),
    path('report/create/<int:assignment_id>/', views.field_report_create, name='field_report_create'),
    path('report/detail/<int:report_id>/', views.field_report_detail, name='field_report_detail'),

    # Check in/out endpoints
    path('check-in/<int:assignment_id>/', views.check_in, name='check_in'),
    path('check-out/<int:assignment_id>/', views.check_out, name='check_out'),

    path('api/job-details/<int:job_id>/', views.job_details_api, name='job_details_api'),

    path('evaluate/<int:pk>/', views.field_job_evaluation, name='field_job_evaluation'),

path('reverse-geocode/', views.reverse_geocode, name='reverse_geocode'),

    # Primary location endpoint
    path('api/location/ipapi/', views.get_ipapi_location, name='get_ipapi_location'),
path('report/export/docx/<int:report_id>/',
         views.field_report_export_docx,  # <-- New DOCX function
         name='field_report_export_pdf'), # <-- Keep the old name for template link consistency
    # Fallback geocoding endpoint
    path('api/location/geocode/', views.reverse_geocode, name='reverse_geocode'),
path('api/report/<int:report_id>/', views.get_report_data, name='get_report_data'),
path('api/report/<int:report_id>/update/', views.update_report, name='update_report'),
path('api/report/<int:report_id>/delete/', views.delete_report, name='delete_report'),

]