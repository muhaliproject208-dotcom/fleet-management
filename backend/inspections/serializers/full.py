"""
Full inspection serializer with all nested data for detailed view.
This provides a complete inspection report with all related data in a single response.
"""

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
    mechanic = MechanicBasicSerializer(read_only=True)
    approved_by = UserDetailedSerializer(read_only=True)
    
    # OneToOne relationships
    health_fitness = HealthFitnessCheckSerializer(
        source='health_fitness_check',
        read_only=True
    )
    documentation = DocumentationComplianceSerializer(
        source='documentation_compliance',
        read_only=True
    )
    post_trip = PostTripReportSerializer(
        source='post_trip_report',
        read_only=True
    )
    risk_score = RiskScoreSummarySerializer(
        source='risk_score_summary',
        read_only=True
    )
    supervisor_remarks = SupervisorRemarksSerializer(read_only=True)
    evaluation = EvaluationSummarySerializer(read_only=True)
    
    # ForeignKey relationships (many)
    exterior_checks = VehicleExteriorCheckSerializer(
        source='vehicleexteriorcheck_set',
        many=True,
        read_only=True
    )
    engine_fluid_checks = EngineFluidCheckSerializer(
        source='enginefluidcheck_set',
        many=True,
        read_only=True
    )
    interior_cabin_checks = InteriorCabinCheckSerializer(
        source='interiorcabincheck_set',
        many=True,
        read_only=True
    )
    functional_checks = FunctionalCheckSerializer(
        source='functionalcheck_set',
        many=True,
        read_only=True
    )
    safety_equipment_checks = SafetyEquipmentCheckSerializer(
        source='safetyequipmentcheck_set',
        many=True,
        read_only=True
    )
    trip_behaviors = TripBehaviorMonitoringSerializer(
        source='tripbehaviormonitoring_set',
        many=True,
        read_only=True
    )
    driving_behaviors = DrivingBehaviorCheckSerializer(
        source='drivingbehaviorcheck_set',
        many=True,
        read_only=True
    )
    corrective_measures = CorrectiveMeasureSerializer(
        source='correctivemeasure_set',
        many=True,
        read_only=True
    )
    enforcement_actions = EnforcementActionSerializer(
        source='enforcementaction_set',
        many=True,
        read_only=True
    )
    sign_offs = InspectionSignOffSerializer(
        source='sign_offs',
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
            'trip_date',
            'route',
            'planned_departure_time',
            'actual_departure_time',
            
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
        
        # Check each section
        if hasattr(obj, 'health_fitness_check'):
            completed += 1
        if hasattr(obj, 'documentation_compliance'):
            completed += 1
        if obj.vehicleexteriorcheck_set.exists():
            completed += 1
        if obj.enginefluidcheck_set.exists():
            completed += 1
        if obj.interiorcabincheck_set.exists():
            completed += 1
        if obj.functionalcheck_set.exists():
            completed += 1
        if obj.safetyequipmentcheck_set.exists():
            completed += 1
        if obj.tripbehaviormonitoring_set.exists():
            completed += 1
        if obj.drivingbehaviorcheck_set.exists():
            completed += 1
        if hasattr(obj, 'post_trip_report'):
            completed += 1
        if hasattr(obj, 'supervisor_remarks'):
            completed += 1
        if hasattr(obj, 'evaluation'):
            completed += 1
        
        return round((completed / total_sections) * 100, 2)
    
    def get_total_violation_points(self, obj):
        """Get total violation points from trip behaviors"""
        return sum(
            behavior.violation_points 
            for behavior in obj.tripbehaviormonitoring_set.all()
        )
    
    def get_has_critical_failures(self, obj):
        """Check if there are any critical failures in vehicle checks"""
        # Check exterior checks
        if obj.vehicleexteriorcheck_set.filter(
            status='fail',
            is_critical_failure=True
        ).exists():
            return True
        
        # Check engine fluid checks
        if obj.enginefluidcheck_set.filter(
            status='fail',
            is_critical_failure=True
        ).exists():
            return True
        
        # Check interior cabin checks
        if obj.interiorcabincheck_set.filter(
            status='fail',
            is_critical_failure=True
        ).exists():
            return True
        
        # Check functional checks
        if obj.functionalcheck_set.filter(
            status='fail',
            is_critical_failure=True
        ).exists():
            return True
        
        # Check safety equipment checks
        if obj.safetyequipmentcheck_set.filter(
            status='fail',
            is_critical_failure=True
        ).exists():
            return True
        
        return False
