from django.contrib import admin
from ..models import CorrectiveMeasure, EnforcementAction


@admin.register(CorrectiveMeasure)
class CorrectiveMeasureAdmin(admin.ModelAdmin):
    """Admin configuration for CorrectiveMeasure model"""
    
    list_display = [
        'get_inspection_id',
        'measure_type',
        'required',
        'completed',
        'due_date',
        'created_at'
    ]
    
    list_filter = [
        'measure_type',
        'required',
        'completed',
        'created_at',
    ]
    
    search_fields = [
        'inspection__inspection_id',
        'inspection__driver__full_name',
        'notes',
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
        ('Measure Details', {
            'fields': ('measure_type', 'required', 'notes')
        }),
        ('Completion Status', {
            'fields': ('due_date', 'completed', 'completed_date')
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


@admin.register(EnforcementAction)
class EnforcementActionAdmin(admin.ModelAdmin):
    """Admin configuration for EnforcementAction model"""
    
    list_display = [
        'get_inspection_id',
        'action_type',
        'is_applied',
        'start_date',
        'end_date',
        'created_at'
    ]
    
    list_filter = [
        'action_type',
        'is_applied',
        'created_at',
    ]
    
    search_fields = [
        'inspection__inspection_id',
        'inspection__driver__full_name',
        'notes',
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
        ('Action Details', {
            'fields': ('action_type', 'is_applied', 'notes')
        }),
        ('Action Period', {
            'fields': ('start_date', 'end_date')
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
