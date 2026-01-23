from django.contrib import admin
from ..models import SupervisorRemarks, EvaluationSummary


@admin.register(SupervisorRemarks)
class SupervisorRemarksAdmin(admin.ModelAdmin):
    """Admin configuration for SupervisorRemarks model"""
    
    list_display = [
        'get_inspection_id',
        'supervisor_name',
        'created_at'
    ]
    
    list_filter = [
        'created_at',
    ]
    
    search_fields = [
        'inspection__inspection_id',
        'inspection__driver__full_name',
        'supervisor_name',
        'remarks',
        'recommendation',
    ]
    
    readonly_fields = [
        'inspection',
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('Inspection', {
            'fields': ('inspection',)
        }),
        ('Supervisor Details', {
            'fields': ('supervisor_name',)
        }),
        ('Remarks', {
            'fields': ('remarks', 'recommendation')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['-created_at']
    
    def get_inspection_id(self, obj):
        """Display inspection ID in list view"""
        return obj.inspection.inspection_id if obj.inspection else 'N/A'
    get_inspection_id.short_description = 'Inspection'
    get_inspection_id.admin_order_field = 'inspection__inspection_id'
    
    def has_delete_permission(self, request, obj=None):
        """Disable delete permission in admin"""
        return False


@admin.register(EvaluationSummary)
class EvaluationSummaryAdmin(admin.ModelAdmin):
    """Admin configuration for EvaluationSummary model"""
    
    list_display = [
        'get_inspection_id',
        'get_average_score',
        'overall_performance',
        'created_at'
    ]
    
    list_filter = [
        'overall_performance',
        'created_at',
    ]
    
    search_fields = [
        'inspection__inspection_id',
        'inspection__driver__full_name',
        'comments',
    ]
    
    readonly_fields = [
        'inspection',
        'overall_performance',
        'get_average_score',
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('Inspection', {
            'fields': ('inspection',)
        }),
        ('Scores', {
            'fields': (
                'pre_trip_inspection_score',
                'driving_conduct_score',
                'incident_management_score',
                'post_trip_reporting_score',
                'compliance_documentation_score',
            )
        }),
        ('Overall Assessment', {
            'fields': ('get_average_score', 'overall_performance', 'comments')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['-created_at']
    
    def get_inspection_id(self, obj):
        """Display inspection ID in list view"""
        return obj.inspection.inspection_id if obj.inspection else 'N/A'
    get_inspection_id.short_description = 'Inspection'
    get_inspection_id.admin_order_field = 'inspection__inspection_id'
    
    def get_average_score(self, obj):
        """Display average score"""
        return f"{obj.calculate_average_score():.2f}"
    get_average_score.short_description = 'Average Score'
    
    def has_delete_permission(self, request, obj=None):
        """Disable delete permission in admin"""
        return False
