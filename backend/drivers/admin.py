from django.contrib import admin
from .models import Driver


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    """Admin configuration for Driver model"""
    
    list_display = [
        'driver_id',
        'full_name',
        'license_number',
        'phone_number',
        'is_active',
        'created_at',
        'created_by'
    ]
    
    list_filter = [
        'is_active',
        'created_at',
    ]
    
    search_fields = [
        'driver_id',
        'full_name',
        'license_number',
        'phone_number',
        'email'
    ]
    
    readonly_fields = [
        'driver_id',
        'created_at',
        'updated_at',
        'created_by'
    ]
    
    fieldsets = (
        ('Driver Information', {
            'fields': ('driver_id', 'full_name', 'license_number')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'email')
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
    
    def save_model(self, request, obj, form, change):
        """Set created_by to current user if creating new driver"""
        if not change:  # Only set on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

