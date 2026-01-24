from django.contrib import admin
from ..models import (
    PreTripInspection, InspectionStatus,
    HealthFitnessCheck, DocumentationCompliance,
    VehicleExteriorCheck, EngineFluidCheck, InteriorCabinCheck,
    FunctionalCheck, SafetyEquipmentCheck,
    TripBehaviorMonitoring, DrivingBehaviorCheck,
    PostTripReport, RiskScoreSummary,
    CorrectiveMeasure, EnforcementAction,
    SupervisorRemarks, EvaluationSummary,
    InspectionSignOff
)


# Inline admin classes for all related inspection sections

class HealthFitnessCheckInline(admin.StackedInline):
    model = HealthFitnessCheck
    extra = 0
    fields = (
        'alcohol_test_status', 'alcohol_test_remarks',
        'temperature_check_status', 'temperature_value',
        'fit_for_duty', 'medication_status', 'medication_remarks',
        'no_health_impairment', 'fatigue_checklist_completed', 'fatigue_remarks'
    )


class DocumentationComplianceInline(admin.StackedInline):
    model = DocumentationCompliance
    extra = 0
    fields = (
        'certificate_of_fitness', 'road_tax_valid', 'insurance_valid',
        'trip_authorization_signed', 'logbook_present', 'driver_handbook_present',
        'permits_valid', 'ppe_available', 'route_familiarity',
        'emergency_procedures_known', 'gps_activated', 'safety_briefing_provided',
        'rtsa_clearance', 'emergency_contact'
    )


class VehicleExteriorCheckInline(admin.TabularInline):
    model = VehicleExteriorCheck
    extra = 0
    fields = ('check_item', 'status', 'remarks')


class EngineFluidCheckInline(admin.TabularInline):
    model = EngineFluidCheck
    extra = 0
    fields = ('check_item', 'status', 'remarks')


class InteriorCabinCheckInline(admin.TabularInline):
    model = InteriorCabinCheck
    extra = 0
    fields = ('check_item', 'status', 'remarks')


class FunctionalCheckInline(admin.TabularInline):
    model = FunctionalCheck
    extra = 0
    fields = ('check_item', 'status', 'remarks')


class SafetyEquipmentCheckInline(admin.TabularInline):
    model = SafetyEquipmentCheck
    extra = 0
    fields = ('check_item', 'status', 'remarks')


class TripBehaviorMonitoringInline(admin.TabularInline):
    model = TripBehaviorMonitoring
    extra = 0
    fields = ('behavior_item', 'status', 'notes', 'violation_points')
    readonly_fields = ('violation_points',)


class DrivingBehaviorCheckInline(admin.TabularInline):
    model = DrivingBehaviorCheck
    extra = 0
    fields = ('behavior_item', 'status', 'remarks')


class PostTripReportInline(admin.StackedInline):
    model = PostTripReport
    extra = 0
    fields = (
        'vehicle_fault_submitted', 'fault_notes',
        'final_inspection_signed', 'compliance_with_policy',
        'attitude_cooperation', 'incidents_recorded', 'incident_notes',
        'total_trip_duration'
    )


class RiskScoreSummaryInline(admin.StackedInline):
    model = RiskScoreSummary
    extra = 0
    readonly_fields = (
        'total_points_this_trip', 'risk_level',
        'total_points_30_days', 'risk_level_30_days'
    )
    fields = readonly_fields


class CorrectiveMeasureInline(admin.TabularInline):
    model = CorrectiveMeasure
    extra = 0
    fields = ('measure_type', 'required', 'due_date', 'completed', 'completed_date', 'notes')


class EnforcementActionInline(admin.TabularInline):
    model = EnforcementAction
    extra = 0
    fields = ('action_type', 'is_applied', 'start_date', 'end_date', 'notes')


class SupervisorRemarksInline(admin.StackedInline):
    model = SupervisorRemarks
    extra = 0
    fields = ('supervisor_name', 'remarks', 'recommendation')


class EvaluationSummaryInline(admin.StackedInline):
    model = EvaluationSummary
    extra = 0
    readonly_fields = ('overall_performance',)
    fields = (
        'pre_trip_inspection_score', 'driving_conduct_score',
        'incident_management_score', 'post_trip_reporting_score',
        'compliance_documentation_score', 'overall_performance', 'comments'
    )


class InspectionSignOffInline(admin.TabularInline):
    model = InspectionSignOff
    extra = 0
    readonly_fields = ('signed_at',)
    fields = ('role', 'signer_name', 'signed_at')


@admin.register(PreTripInspection)
class PreTripInspectionAdmin(admin.ModelAdmin):
    """Admin configuration for PreTripInspection model with all related sections as inlines"""
    
    inlines = [
        HealthFitnessCheckInline,
        DocumentationComplianceInline,
        VehicleExteriorCheckInline,
        EngineFluidCheckInline,
        InteriorCabinCheckInline,
        FunctionalCheckInline,
        SafetyEquipmentCheckInline,
        TripBehaviorMonitoringInline,
        DrivingBehaviorCheckInline,
        PostTripReportInline,
        RiskScoreSummaryInline,
        CorrectiveMeasureInline,
        EnforcementActionInline,
        SupervisorRemarksInline,
        EvaluationSummaryInline,
        InspectionSignOffInline,
    ]
    
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
        """Only superusers can delete inspections"""
        return request.user.is_superuser
