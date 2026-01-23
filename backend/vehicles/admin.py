from django.contrib import admin
from .models import Vehicle


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    """Admin configuration for Vehicle model"""
    
    list_display = [
        'vehicle_id',
        'registration_number',
        'vehicle_type',
        'get_driver_name',
        'is_active',
        'created_at',
        'created_by'
    ]
    
    list_filter = [
        'is_active',
        'vehicle_type',
        'created_at',
    ]
    
    search_fields = [
        'vehicle_id',
        'registration_number',
        'vehicle_type',
        'driver__full_name'
    ]
    
    readonly_fields = [
        'vehicle_id',
        'created_at',
        'updated_at',
        'created_by'
    ]
    
    fieldsets = (
        ('Vehicle Information', {
            'fields': ('vehicle_id', 'registration_number', 'vehicle_type')
        }),
        ('Driver Assignment', {
            'fields': ('driver',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['-created_at']
    
    def get_driver_name(self, obj):
        """Display driver name in list view"""
        return obj.driver.full_name if obj.driver else 'Unassigned'
    get_driver_name.short_description = 'Driver'
    
    def save_model(self, request, obj, form, change):
        """Set created_by to current user if creating new vehicle"""
        if not change:  # Only set on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

