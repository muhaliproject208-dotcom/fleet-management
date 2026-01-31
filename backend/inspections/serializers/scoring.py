from rest_framework import serializers
from ..models import PreTripScoreSummary


class PreTripScoreSummarySerializer(serializers.ModelSerializer):
    """Serializer for Pre-Trip Score Summary"""
    
    section_summary = serializers.SerializerMethodField()
    total_summary = serializers.SerializerMethodField()
    score_level_display = serializers.SerializerMethodField()
    risk_status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = PreTripScoreSummary
        fields = [
            'id',
            'inspection',
            # Section scores with questions count
            'health_fitness_score',
            'health_fitness_max',
            'health_fitness_questions',
            'documentation_score',
            'documentation_max',
            'documentation_questions',
            'vehicle_exterior_score',
            'vehicle_exterior_max',
            'vehicle_exterior_questions',
            'engine_fluid_score',
            'engine_fluid_max',
            'engine_fluid_questions',
            'interior_cabin_score',
            'interior_cabin_max',
            'interior_cabin_questions',
            'functional_score',
            'functional_max',
            'functional_questions',
            'safety_equipment_score',
            'safety_equipment_max',
            'safety_equipment_questions',
            'brakes_steering_score',
            'brakes_steering_max',
            'brakes_steering_questions',
            # Totals
            'total_score',
            'max_possible_score',
            'total_questions',
            'score_percentage',
            'score_level',
            'score_level_display',
            'risk_status',
            'risk_status_display',
            'critical_failures',
            'has_critical_failures',
            'is_cleared_for_travel',
            'clearance_notes',
            'section_summary',
            'total_summary',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'inspection', 
            'health_fitness_score', 'health_fitness_max', 'health_fitness_questions',
            'documentation_score', 'documentation_max', 'documentation_questions',
            'vehicle_exterior_score', 'vehicle_exterior_max', 'vehicle_exterior_questions',
            'engine_fluid_score', 'engine_fluid_max', 'engine_fluid_questions',
            'interior_cabin_score', 'interior_cabin_max', 'interior_cabin_questions',
            'functional_score', 'functional_max', 'functional_questions',
            'safety_equipment_score', 'safety_equipment_max', 'safety_equipment_questions',
            'brakes_steering_score', 'brakes_steering_max', 'brakes_steering_questions',
            'total_score', 'max_possible_score', 'total_questions', 'score_percentage',
            'score_level', 'risk_status', 'critical_failures', 'has_critical_failures',
            'is_cleared_for_travel', 'clearance_notes',
            'created_at', 'updated_at',
        ]
    
    def get_section_summary(self, obj):
        return obj.get_section_summary()
    
    def get_total_summary(self, obj):
        return obj.get_total_summary()
    
    def get_score_level_display(self, obj):
        return obj.get_score_level_display()
    
    def get_risk_status_display(self, obj):
        return obj.get_risk_status_display()
