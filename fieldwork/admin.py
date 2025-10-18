from django.contrib import admin
from .models import FieldJob, FieldJobAssignment, FieldReport

@admin.register(FieldJob)
class FieldJobAdmin(admin.ModelAdmin):
    list_display = ['client_name', 'category', 'date_of_job', 'poc_name', 'created_by', 'created_at']
    list_filter = ['category', 'date_of_job', 'created_at']
    search_fields = ['client_name', 'poc_name', 'site_address']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(FieldJobAssignment)
class FieldJobAssignmentAdmin(admin.ModelAdmin):
    list_display = ['field_job', 'staff', 'poc_approval_code', 'is_code_used', 'created_at']
    list_filter = ['is_code_used', 'created_at']
    search_fields = ['field_job__client_name', 'staff__first_name', 'staff__last_name']
    readonly_fields = ['poc_approval_code', 'created_at']

@admin.register(FieldReport)
class FieldReportAdmin(admin.ModelAdmin):
    list_display = ['assignment', 'check_in_time', 'check_out_time', 'site_visit_complete', 'submitted_at']
    list_filter = ['site_visit_complete', 'revisit_required', 'submitted_at']
    search_fields = ['assignment__field_job__client_name', 'assignment__staff__first_name']
    readonly_fields = ['submitted_at']