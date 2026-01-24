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
        'average_risk_score_display',
        'risk_level_display',
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
        'created_by',
        'average_risk_score_display',
        'risk_level_display'
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
        ('Performance Metrics', {
            'fields': ('average_risk_score_display', 'risk_level_display'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['-created_at']
    
    def average_risk_score_display(self, obj):
        """Display average risk score"""
        score = obj.get_average_risk_score()
        return f"{score:.2f}" if score is not None else "No trips yet"
    average_risk_score_display.short_description = 'Avg Risk Score'
    
    def risk_level_display(self, obj):
        """Display risk level with color coding"""
        from django.utils.html import format_html
        risk_level = obj.get_risk_level()
        
        colors = {
            'Low': '#4CAF50',
            'Medium': '#FF9800',
            'High': '#f44336',
            'N/A': '#999'
        }
        
        color = colors.get(risk_level, '#999')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            risk_level
        )
    risk_level_display.short_description = 'Risk Level'
    
    def save_model(self, request, obj, form, change):
        """Set created_by to current user if creating new driver"""
        if not change:  # Only set on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

