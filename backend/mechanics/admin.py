from django.contrib import admin
from .models import Mechanic


@admin.register(Mechanic)
class MechanicAdmin(admin.ModelAdmin):
    """Admin configuration for Mechanic model"""
    
    list_display = [
        'mechanic_id',
        'full_name',
        'specialization',
        'phone_number',
        'is_active',
        'created_at',
        'created_by'
    ]
    
    list_filter = [
        'is_active',
        'specialization',
        'created_at',
    ]
    
    search_fields = [
        'mechanic_id',
        'full_name',
        'specialization',
        'phone_number'
    ]
    
    readonly_fields = [
        'mechanic_id',
        'created_at',
        'updated_at',
        'created_by'
    ]
    
    fieldsets = (
        ('Mechanic Information', {
            'fields': ('mechanic_id', 'full_name', 'specialization')
        }),
        ('Contact Information', {
            'fields': ('phone_number',)
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
        """Set created_by to current user if creating new mechanic"""
        if not change:  # Only set on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

