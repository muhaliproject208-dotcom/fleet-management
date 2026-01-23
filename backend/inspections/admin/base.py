from django.contrib import admin
from ..models import PreTripInspection, InspectionStatus


@admin.register(PreTripInspection)
class PreTripInspectionAdmin(admin.ModelAdmin):
    """Admin configuration for PreTripInspection model"""
    
    list_display = [
        'inspection_id',
        'inspection_date',
        'get_driver_name',
        'get_vehicle_registration',
        'status',
        'supervisor',
        'created_at'
    ]
    
    list_filter = [
        'status',
        'inspection_date',
        'created_at',
    ]
    
    search_fields = [
        'inspection_id',
        'driver__full_name',
        'vehicle__registration_number',
        'route',
        'supervisor__email'
    ]
    
    readonly_fields = [
        'inspection_id',
        'status',
        'approval_status_updated_at',
        'approved_by',
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('Inspection Information', {
            'fields': ('inspection_id', 'inspection_date', 'route', 'status')
        }),
        ('Personnel', {
            'fields': ('driver', 'vehicle', 'supervisor', 'mechanic')
        }),
        ('Trip Details', {
            'fields': ('approved_driving_hours', 'approved_rest_stops')
        }),
        ('Approval Status', {
            'fields': (
                'approved_by',
                'approval_status_updated_at',
                'rejection_reason'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['-inspection_date', '-created_at']
    date_hierarchy = 'inspection_date'
    
    def get_driver_name(self, obj):
        """Display driver name in list view"""
        return obj.driver.full_name if obj.driver else 'N/A'
    get_driver_name.short_description = 'Driver'
    get_driver_name.admin_order_field = 'driver__full_name'
    
    def get_vehicle_registration(self, obj):
        """Display vehicle registration in list view"""
        return obj.vehicle.registration_number if obj.vehicle else 'N/A'
    get_vehicle_registration.short_description = 'Vehicle'
    get_vehicle_registration.admin_order_field = 'vehicle__registration_number'
    
    def has_delete_permission(self, request, obj=None):
        """Disable delete permission in admin"""
        return False
