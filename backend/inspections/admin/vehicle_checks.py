from django.contrib import admin
from ..models import (
    VehicleExteriorCheck,
    EngineFluidCheck,
    InteriorCabinCheck,
    FunctionalCheck,
    SafetyEquipmentCheck,
)


class BaseVehicleCheckAdmin(admin.ModelAdmin):
    """Base admin configuration for vehicle check models"""
    
    list_display = [
        'get_inspection_id',
        'check_item',
        'status',
        'get_critical_status',
        'created_at'
    ]
    
    list_filter = [
        'status',
        'check_item',
        'created_at',
    ]
    
    search_fields = [
        'inspection__inspection_id',
        'inspection__driver__full_name',
        'check_item',
        'remarks',
    ]
    
    readonly_fields = [
        'inspection',
        'created_at',
        'updated_at',
        'get_critical_status'
    ]
    
    fieldsets = (
        ('Inspection', {
            'fields': ('inspection',)
        }),
        ('Check Details', {
            'fields': ('check_item', 'status', 'remarks')
        }),
        ('Status', {
            'fields': ('get_critical_status',)
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
    
    def get_critical_status(self, obj):
        """Display if this is a critical failure"""
        if obj.has_critical_failure():
            return "⚠️ CRITICAL FAILURE"
        return "Normal"
    get_critical_status.short_description = 'Critical Status'
    
    def has_delete_permission(self, request, obj=None):
        """Allow delete for vehicle checks"""
        return True


@admin.register(VehicleExteriorCheck)
class VehicleExteriorCheckAdmin(BaseVehicleCheckAdmin):
    """Admin configuration for VehicleExteriorCheck model"""
    pass


@admin.register(EngineFluidCheck)
class EngineFluidCheckAdmin(BaseVehicleCheckAdmin):
    """Admin configuration for EngineFluidCheck model"""
    pass


@admin.register(InteriorCabinCheck)
class InteriorCabinCheckAdmin(BaseVehicleCheckAdmin):
    """Admin configuration for InteriorCabinCheck model"""
    pass


@admin.register(FunctionalCheck)
class FunctionalCheckAdmin(BaseVehicleCheckAdmin):
    """Admin configuration for FunctionalCheck model"""
    pass


@admin.register(SafetyEquipmentCheck)
class SafetyEquipmentCheckAdmin(BaseVehicleCheckAdmin):
    """Admin configuration for SafetyEquipmentCheck model"""
    pass
