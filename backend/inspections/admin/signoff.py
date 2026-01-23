from django.contrib import admin
from ..models import InspectionSignOff


@admin.register(InspectionSignOff)
class InspectionSignOffAdmin(admin.ModelAdmin):
    """Admin configuration for InspectionSignOff model"""
    
    list_display = [
        'get_inspection_id',
        'role',
        'signer_name',
        'signed_at'
    ]
    
    list_filter = [
        'role',
        'signed_at',
    ]
    
    search_fields = [
        'inspection__inspection_id',
        'inspection__driver__full_name',
        'signer_name',
    ]
    
    readonly_fields = [
        'inspection',
        'role',
        'signer_name',
        'signed_at'
    ]
    
    fieldsets = (
        ('Inspection', {
            'fields': ('inspection',)
        }),
        ('Sign-Off Details', {
            'fields': ('role', 'signer_name', 'signed_at')
        }),
    )
    
    ordering = ['-signed_at']
    
    def get_inspection_id(self, obj):
        """Display inspection ID in list view"""
        return obj.inspection.inspection_id if obj.inspection else 'N/A'
    get_inspection_id.short_description = 'Inspection'
    get_inspection_id.admin_order_field = 'inspection__inspection_id'
    
    def has_add_permission(self, request):
        """Disable add in admin (create via API only)"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable edit in admin (immutable)"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Disable delete in admin (immutable)"""
        return False
