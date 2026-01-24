"""
Full inspection serializer with all nested data for detailed view.
This provides a complete inspection report with all related data in a single response.
"""

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from ..models import PreTripInspection
from .base import (
    DriverBasicSerializer,
    VehicleDetailedSerializer,
    UserDetailedSerializer,
    MechanicBasicSerializer,
)
from .health_fitness import HealthFitnessCheckSerializer
from .documentation import DocumentationComplianceSerializer
from .vehicle_checks import (
    VehicleExteriorCheckSerializer,
    EngineFluidCheckSerializer,
    InteriorCabinCheckSerializer,
    FunctionalCheckSerializer,
    SafetyEquipmentCheckSerializer,
)
from .behavior import (
    TripBehaviorMonitoringSerializer,
    DrivingBehaviorCheckSerializer,
)
from .post_trip import (
    PostTripReportSerializer,
    RiskScoreSummarySerializer,
)
from .enforcement import (
    CorrectiveMeasureSerializer,
    EnforcementActionSerializer,
)
from .evaluation import (
    SupervisorRemarksSerializer,
    EvaluationSummarySerializer,
)
from .signoff import InspectionSignOffSerializer


class PreTripInspectionFullSerializer(serializers.ModelSerializer):
    """
    Complete inspection serializer with all nested related data.
    Use for detailed inspection views and PDF generation.
    """
    
    # Core relationships
    driver = DriverBasicSerializer(read_only=True)
    vehicle = VehicleDetailedSerializer(read_only=True)
    supervisor = UserDetailedSerializer(read_only=True)
    mechanic = MechanicBasicSerializer(read_only=True, allow_null=True)
    approved_by = UserDetailedSerializer(read_only=True, allow_null=True)
    
    # OneToOne relationships - allow_null for optional sections
    health_fitness = HealthFitnessCheckSerializer(read_only=True, allow_null=True)
    documentation = DocumentationComplianceSerializer(read_only=True, allow_null=True)
    post_trip = PostTripReportSerializer(read_only=True, allow_null=True)
    risk_score = RiskScoreSummarySerializer(read_only=True, allow_null=True)
    supervisor_remarks = SupervisorRemarksSerializer(read_only=True, allow_null=True)
    evaluation = EvaluationSummarySerializer(read_only=True, allow_null=True)
    
    # ForeignKey relationships (many)
    exterior_checks = VehicleExteriorCheckSerializer(
        many=True,
        read_only=True
    )
    engine_fluid_checks = EngineFluidCheckSerializer(
        many=True,
        read_only=True
    )
    interior_cabin_checks = InteriorCabinCheckSerializer(
        many=True,
        read_only=True
    )
    functional_checks = FunctionalCheckSerializer(
        many=True,
        read_only=True
    )
    safety_equipment_checks = SafetyEquipmentCheckSerializer(
        many=True,
        read_only=True
    )
    trip_behaviors = TripBehaviorMonitoringSerializer(
        many=True,
        read_only=True
    )
    driving_behaviors = DrivingBehaviorCheckSerializer(
        many=True,
        read_only=True
    )
    corrective_measures = CorrectiveMeasureSerializer(
        many=True,
        read_only=True
    )
    enforcement_actions = EnforcementActionSerializer(
        many=True,
        read_only=True
    )
    sign_offs = InspectionSignOffSerializer(
        many=True,
        read_only=True
    )
    
    # Computed fields
    completion_percentage = serializers.SerializerMethodField()
    total_violation_points = serializers.SerializerMethodField()
    has_critical_failures = serializers.SerializerMethodField()
    
    class Meta:
        model = PreTripInspection
        fields = [
            # Basic fields
            'id',
            'inspection_id',
            'status',
            'inspection_date',
            'route',
            'approved_driving_hours',
            'approved_rest_stops',
            
            # Core relationships
            'driver',
            'vehicle',
            'supervisor',
            'mechanic',
            'approved_by',
            
            # OneToOne relationships
            'health_fitness',
            'documentation',
            'post_trip',
            'risk_score',
            'supervisor_remarks',
            'evaluation',
            
            # ForeignKey relationships (many)
            'exterior_checks',
            'engine_fluid_checks',
            'interior_cabin_checks',
            'functional_checks',
            'safety_equipment_checks',
            'trip_behaviors',
            'driving_behaviors',
            'corrective_measures',
            'enforcement_actions',
            'sign_offs',
            
            # Workflow fields
            'rejection_reason',
            'approval_status_updated_at',
            
            # Computed fields
            'completion_percentage',
            'total_violation_points',
            'has_critical_failures',
            
            # Timestamps
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'inspection_id',
            'approved_by',
            'approval_status_updated_at',
            'created_at',
            'updated_at',
        ]
    
    def get_completion_percentage(self, obj):
        """Calculate what percentage of the inspection is complete"""
        total_sections = 12  # Total number of inspection sections
        completed = 0
        
        def has_related(name):
            try:
                return getattr(obj, name) is not None
            except ObjectDoesNotExist:
                return False
        
        # Check each section
        if has_related('health_fitness'):
            completed += 1
        if has_related('documentation'):
            completed += 1
        if obj.exterior_checks.exists():
            completed += 1
        if obj.engine_fluid_checks.exists():
            completed += 1
        if obj.interior_cabin_checks.exists():
            completed += 1
        if obj.functional_checks.exists():
            completed += 1
        if obj.safety_equipment_checks.exists():
            completed += 1
        if obj.trip_behaviors.exists():
            completed += 1
        if obj.driving_behaviors.exists():
            completed += 1
        if has_related('post_trip'):
            completed += 1
        if has_related('supervisor_remarks'):
            completed += 1
        if has_related('evaluation'):
            completed += 1
        
        return round((completed / total_sections) * 100, 2)
    
    def get_total_violation_points(self, obj):
        """Get total violation points from trip behaviors"""
        return sum(
            behavior.violation_points 
            for behavior in obj.trip_behaviors.all()
        )
    
    def get_has_critical_failures(self, obj):
        """Check if there are any critical failures in vehicle checks"""
        for check in obj.exterior_checks.all():
            if check.has_critical_failure():
                return True
        for check in obj.engine_fluid_checks.all():
            if check.has_critical_failure():
                return True
        for check in obj.interior_cabin_checks.all():
            if check.has_critical_failure():
                return True
        for check in obj.functional_checks.all():
            if check.has_critical_failure():
                return True
        for check in obj.safety_equipment_checks.all():
            if check.has_critical_failure():
                return True
        return False
