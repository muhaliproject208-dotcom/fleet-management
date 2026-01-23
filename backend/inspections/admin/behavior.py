from django.contrib import admin
from ..models import TripBehaviorMonitoring, DrivingBehaviorCheck


@admin.register(TripBehaviorMonitoring)
class TripBehaviorMonitoringAdmin(admin.ModelAdmin):
    """Admin configuration for TripBehaviorMonitoring model"""
    
    list_display = [
        'get_inspection_id',
        'behavior_item',
        'status',
        'violation_points',
        'created_at'
    ]
    
    list_filter = [
        'status',
        'behavior_item',
        'created_at',
    ]
    
    search_fields = [
        'inspection__inspection_id',
        'inspection__driver__full_name',
        'behavior_item',
        'notes',
    ]
    
    readonly_fields = [
        'inspection',
        'violation_points',
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('Inspection', {
            'fields': ('inspection',)
        }),
        ('Behavior Details', {
            'fields': ('behavior_item', 'status', 'notes', 'violation_points')
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


@admin.register(DrivingBehaviorCheck)
class DrivingBehaviorCheckAdmin(admin.ModelAdmin):
    """Admin configuration for DrivingBehaviorCheck model"""
    
    list_display = [
        'get_inspection_id',
        'behavior_item',
        'status',
        'created_at'
    ]
    
    list_filter = [
        'status',
        'behavior_item',
        'created_at',
    ]
    
    search_fields = [
        'inspection__inspection_id',
        'inspection__driver__full_name',
        'behavior_item',
        'remarks',
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
        ('Behavior Details', {
            'fields': ('behavior_item', 'status', 'remarks')
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
