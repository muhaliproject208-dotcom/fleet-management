from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, SupabaseAuthSession, UserRole


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model"""
    
    list_display = [
        'email', 'first_name', 'last_name', 'role',
        'is_active', 'email_verified', 'date_joined'
    ]
    list_filter = ['role', 'is_active', 'email_verified', 'is_staff', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name', 'supabase_uid']
    ordering = ['-date_joined']
    
    fieldsets = (
        ('Authentication', {
            'fields': ('email', 'password', 'supabase_uid')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'phone_number')
        }),
        ('Permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'email_verified')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role'),
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login', 'supabase_uid']


@admin.register(SupabaseAuthSession)
class SupabaseAuthSessionAdmin(admin.ModelAdmin):
    """Admin interface for Supabase Auth Session model"""
    
    list_display = ['user', 'token_type', 'expires_at', 'created_at', 'is_expired']
    list_filter = ['token_type', 'created_at', 'expires_at']
    search_fields = ['user__email', 'access_token']
    ordering = ['-created_at']
    readonly_fields = ['user', 'access_token', 'refresh_token', 'token_type', 'expires_at', 'created_at']
    
    def has_add_permission(self, request):
        """Disable manual creation of sessions"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Make sessions read-only"""
        return False
