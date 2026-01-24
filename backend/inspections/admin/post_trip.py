from django.contrib import admin
from ..models import PostTripReport, RiskScoreSummary


@admin.register(PostTripReport)
class PostTripReportAdmin(admin.ModelAdmin):
    """
    Admin configuration for PostTripReport model.
    
    Note: To edit all post-trip related data (behaviors, risk scores, evaluations, etc.),
    use the PreTripInspection admin which has all inlines since these models are linked
    to the inspection, not directly to the PostTripReport.
    """
    
    list_display = [
        'get_inspection_id',
        'vehicle_fault_submitted',
        'final_inspection_signed',
        'incidents_recorded',
        'created_at'
    ]
    
    list_filter = [
        'vehicle_fault_submitted',
        'final_inspection_signed',
        'compliance_with_policy',
        'attitude_cooperation',
        'incidents_recorded',
        'created_at',
    ]
    
    search_fields = [
        'inspection__inspection_id',
        'inspection__driver__full_name',
        'fault_notes',
        'incident_notes',
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('Inspection', {
            'fields': ('inspection',)
        }),
        ('Vehicle Status', {
            'fields': ('vehicle_fault_submitted', 'fault_notes', 'final_inspection_signed')
        }),
        ('Driver Assessment', {
            'fields': ('compliance_with_policy', 'attitude_cooperation')
        }),
        ('Incidents', {
            'fields': ('incidents_recorded', 'incident_notes')
        }),
        ('Trip Duration', {
            'fields': ('total_trip_duration',)
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
        """Allow delete permission in admin"""
        return True


@admin.register(RiskScoreSummary)
class RiskScoreSummaryAdmin(admin.ModelAdmin):
    """Admin configuration for RiskScoreSummary model"""
    
    list_display = [
        'get_inspection_id',
        'total_points_this_trip',
        'risk_level',
        'total_points_30_days',
        'risk_level_30_days',
        'created_at'
    ]
    
    list_filter = [
        'risk_level',
        'risk_level_30_days',
        'created_at',
    ]
    
    search_fields = [
        'inspection__inspection_id',
        'inspection__driver__full_name',
    ]
    
    readonly_fields = [
        'inspection',
        'total_points_this_trip',
        'risk_level',
        'total_points_30_days',
        'risk_level_30_days',
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('Inspection', {
            'fields': ('inspection',)
        }),
        ('This Trip', {
            'fields': ('total_points_this_trip', 'risk_level')
        }),
        ('30-Day Rolling', {
            'fields': ('total_points_30_days', 'risk_level_30_days')
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
