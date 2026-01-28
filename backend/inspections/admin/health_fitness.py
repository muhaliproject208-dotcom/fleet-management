from django.contrib import admin
from ..models import HealthFitnessCheck


@admin.register(HealthFitnessCheck)
class HealthFitnessCheckAdmin(admin.ModelAdmin):
    """Admin configuration for HealthFitnessCheck model"""
    
    list_display = [
        'get_inspection_id',
        'adequate_rest',
        'rest_clearance_status',
        'alcohol_test_status',
        'temperature_check_status',
        'fit_for_duty',
        'section_score',
        'get_passed_status',
        'created_at'
    ]
    
    list_filter = [
        'adequate_rest',
        'rest_clearance_status',
        'alcohol_test_status',
        'temperature_check_status',
        'fit_for_duty',
        'medication_status',
        'no_health_impairment',
        'fatigue_checklist_completed',
        'created_at',
    ]
    
    search_fields = [
        'inspection__inspection_id',
        'inspection__driver__full_name',
        'alcohol_test_remarks',
        'medication_remarks',
        'fatigue_remarks',
    ]
    
    readonly_fields = [
        'inspection',
        'rest_clearance_status',
        'section_score',
        'max_possible_score',
        'created_at',
        'updated_at',
        'get_passed_status',
        'get_score_info',
        'get_clearance_message'
    ]
    
    fieldsets = (
        ('Inspection', {
            'fields': ('inspection',)
        }),
        ('Fatigue / Rest Clearance', {
            'fields': ('adequate_rest', 'rest_clearance_status', 'get_clearance_message'),
            'description': 'CRITICAL: Driver must have rested 8+ hours for travel clearance.'
        }),
        ('Alcohol Test', {
            'fields': ('alcohol_test_status', 'alcohol_test_remarks')
        }),
        ('Temperature Check', {
            'fields': ('temperature_check_status', 'temperature_value')
        }),
        ('Fitness Assessment', {
            'fields': ('fit_for_duty', 'no_health_impairment')
        }),
        ('Medication', {
            'fields': ('medication_status', 'medication_remarks')
        }),
        ('Fatigue Check', {
            'fields': ('fatigue_checklist_completed', 'fatigue_remarks')
        }),
        ('Scoring', {
            'fields': ('section_score', 'max_possible_score', 'get_score_info'),
            'classes': ('collapse',)
        }),
        ('Overall Status', {
            'fields': ('get_passed_status',)
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
    
    def get_passed_status(self, obj):
        """Display whether health check passed"""
        return "Passed" if obj.is_passed() else "Failed"
    get_passed_status.short_description = 'Status'
    
    def get_score_info(self, obj):
        """Display score information"""
        earned, max_score, percentage = obj.calculate_score()
        return f"{earned}/{max_score} ({percentage}%)"
    get_score_info.short_description = 'Score'
    
    def get_clearance_message(self, obj):
        """Display clearance message"""
        return obj.get_clearance_message()
    get_clearance_message.short_description = 'Clearance Status'
    
    def has_delete_permission(self, request, obj=None):
        """Disable delete permission in admin"""
        return False
