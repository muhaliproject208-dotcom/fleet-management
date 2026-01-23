from django.contrib import admin
from ..models import DocumentationCompliance


@admin.register(DocumentationCompliance)
class DocumentationComplianceAdmin(admin.ModelAdmin):
    """Admin configuration for DocumentationCompliance model"""
    
    list_display = [
        'get_inspection_id',
        'certificate_of_fitness',
        'road_tax_valid',
        'insurance_valid',
        'trip_authorization_signed',
        'get_compliance_status',
        'created_at'
    ]
    
    list_filter = [
        'certificate_of_fitness',
        'road_tax_valid',
        'insurance_valid',
        'trip_authorization_signed',
        'logbook_present',
        'gps_activated',
        'rtsa_clearance',
        'created_at',
    ]
    
    search_fields = [
        'inspection__inspection_id',
        'inspection__driver__full_name',
        'emergency_contact',
    ]
    
    readonly_fields = [
        'inspection',
        'created_at',
        'updated_at',
        'get_compliance_status',
        'get_missing_documents'
    ]
    
    fieldsets = (
        ('Inspection', {
            'fields': ('inspection',)
        }),
        ('Required Documents', {
            'fields': (
                'certificate_of_fitness',
                'road_tax_valid',
                'insurance_valid',
                'trip_authorization_signed',
                'logbook_present',
            )
        }),
        ('Additional Documents', {
            'fields': (
                'driver_handbook_present',
                'permits_valid',
                'ppe_available',
            )
        }),
        ('Driver Preparation', {
            'fields': (
                'route_familiarity',
                'emergency_procedures_known',
                'safety_briefing_provided',
            )
        }),
        ('Technology & Clearance', {
            'fields': (
                'gps_activated',
                'rtsa_clearance',
            )
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact',)
        }),
        ('Compliance Status', {
            'fields': ('get_compliance_status', 'get_missing_documents'),
            'classes': ('collapse',)
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
    
    def get_compliance_status(self, obj):
        """Display compliance status"""
        return "✓ Compliant" if obj.is_compliant() else "✗ Non-Compliant"
    get_compliance_status.short_description = 'Compliance'
    
    def get_missing_documents(self, obj):
        """Display missing documents"""
        missing = obj.get_missing_documents()
        return ", ".join(missing) if missing else "All documents present"
    get_missing_documents.short_description = 'Missing Documents'
    
    def has_delete_permission(self, request, obj=None):
        """Disable delete permission in admin"""
        return False
