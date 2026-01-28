from rest_framework import serializers
from ..models import PreTripScoreSummary


class PreTripScoreSummarySerializer(serializers.ModelSerializer):
    """Serializer for Pre-Trip Score Summary"""
    
    section_summary = serializers.SerializerMethodField()
    score_level_display = serializers.SerializerMethodField()
    
    class Meta:
        model = PreTripScoreSummary
        fields = [
            'id',
            'inspection',
            'health_fitness_score',
            'health_fitness_max',
            'documentation_score',
            'documentation_max',
            'vehicle_exterior_score',
            'vehicle_exterior_max',
            'engine_fluid_score',
            'engine_fluid_max',
            'interior_cabin_score',
            'interior_cabin_max',
            'functional_score',
            'functional_max',
            'safety_equipment_score',
            'safety_equipment_max',
            'total_score',
            'max_possible_score',
            'score_percentage',
            'score_level',
            'score_level_display',
            'critical_failures',
            'has_critical_failures',
            'is_cleared_for_travel',
            'clearance_notes',
            'section_summary',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'inspection', 
            'health_fitness_score', 'health_fitness_max',
            'documentation_score', 'documentation_max',
            'vehicle_exterior_score', 'vehicle_exterior_max',
            'engine_fluid_score', 'engine_fluid_max',
            'interior_cabin_score', 'interior_cabin_max',
            'functional_score', 'functional_max',
            'safety_equipment_score', 'safety_equipment_max',
            'total_score', 'max_possible_score', 'score_percentage',
            'score_level', 'critical_failures', 'has_critical_failures',
            'is_cleared_for_travel', 'clearance_notes',
            'created_at', 'updated_at',
        ]
    
    def get_section_summary(self, obj):
        return obj.get_section_summary()
    
    def get_score_level_display(self, obj):
        return obj.get_score_level_display()
