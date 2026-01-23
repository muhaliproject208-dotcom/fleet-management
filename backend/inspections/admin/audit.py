from django.contrib import admin
from ..models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin configuration for AuditLog model"""
    
    list_display = [
        'timestamp',
        'get_user_name',
        'action',
        'get_object_type',
        'object_id',
        'ip_address'
    ]
    
    list_filter = [
        'action',
        'content_type',
        'timestamp',
    ]
    
    search_fields = [
        'user__email',
        'user__first_name',
        'user__last_name',
        'description',
        'ip_address',
    ]
    
    readonly_fields = [
        'user',
        'action',
        'content_type',
        'object_id',
        'changes',
        'description',
        'ip_address',
        'user_agent',
        'timestamp',
    ]
    
    fieldsets = (
        ('Action Details', {
            'fields': ('user', 'action', 'content_type', 'object_id')
        }),
        ('Changes', {
            'fields': ('changes', 'description')
        }),
        ('Request Details', {
            'fields': ('ip_address', 'user_agent', 'timestamp')
        }),
    )
    
    ordering = ['-timestamp']
    
    def get_user_name(self, obj):
        """Display user name in list view"""
        return obj.user.get_full_name() if obj.user else 'System'
    get_user_name.short_description = 'User'
    get_user_name.admin_order_field = 'user__first_name'
    
    def get_object_type(self, obj):
        """Display object type in list view"""
        return obj.content_type.model.upper()
    get_object_type.short_description = 'Object Type'
    get_object_type.admin_order_field = 'content_type'
    
    def has_add_permission(self, request):
        """Disable add in admin (created programmatically only)"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable edit in admin (immutable)"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete audit logs"""
        return request.user.is_superuser
