from rest_framework import serializers
from ..models import (
    PreTripScoreSummary,
    PostChecklistScoreSummary,
    FinalScoreSummary,
    TOTAL_PRECHECKLIST_QUESTIONS,
    TOTAL_POSTCHECKLIST_QUESTIONS,
    SECTION_WEIGHTS,
    POST_SECTION_QUESTIONS,
)


class PreTripScoreSummarySerializer(serializers.ModelSerializer):
    """Serializer for Pre-Trip Score Summary"""
    
    section_summary = serializers.SerializerMethodField()
    total_summary = serializers.SerializerMethodField()
    score_level_display = serializers.SerializerMethodField()
    risk_status_display = serializers.SerializerMethodField()
    total_prechecklist_questions = serializers.SerializerMethodField()
    section_weights = serializers.SerializerMethodField()
    
    class Meta:
        model = PreTripScoreSummary
        fields = [
            'id',
            'inspection',
            # Section scores with questions count, percentages and risk levels
            'health_fitness_score',
            'health_fitness_max',
            'health_fitness_questions',
            'health_fitness_percentage',
            'health_fitness_risk',
            'documentation_score',
            'documentation_max',
            'documentation_questions',
            'documentation_percentage',
            'documentation_risk',
            'vehicle_exterior_score',
            'vehicle_exterior_max',
            'vehicle_exterior_questions',
            'vehicle_exterior_percentage',
            'vehicle_exterior_risk',
            'engine_fluid_score',
            'engine_fluid_max',
            'engine_fluid_questions',
            'engine_fluid_percentage',
            'engine_fluid_risk',
            'interior_cabin_score',
            'interior_cabin_max',
            'interior_cabin_questions',
            'interior_cabin_percentage',
            'interior_cabin_risk',
            'functional_score',
            'functional_max',
            'functional_questions',
            'functional_percentage',
            'functional_risk',
            'safety_equipment_score',
            'safety_equipment_max',
            'safety_equipment_questions',
            'safety_equipment_percentage',
            'safety_equipment_risk',
            'brakes_steering_score',
            'brakes_steering_max',
            'brakes_steering_questions',
            'brakes_steering_percentage',
            'brakes_steering_risk',
            # Totals
            'total_score',
            'max_possible_score',
            'total_questions',
            'total_prechecklist_questions',
            'section_weights',
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
            'health_fitness_percentage', 'health_fitness_risk',
            'documentation_score', 'documentation_max', 'documentation_questions',
            'documentation_percentage', 'documentation_risk',
            'vehicle_exterior_score', 'vehicle_exterior_max', 'vehicle_exterior_questions',
            'vehicle_exterior_percentage', 'vehicle_exterior_risk',
            'engine_fluid_score', 'engine_fluid_max', 'engine_fluid_questions',
            'engine_fluid_percentage', 'engine_fluid_risk',
            'interior_cabin_score', 'interior_cabin_max', 'interior_cabin_questions',
            'interior_cabin_percentage', 'interior_cabin_risk',
            'functional_score', 'functional_max', 'functional_questions',
            'functional_percentage', 'functional_risk',
            'safety_equipment_score', 'safety_equipment_max', 'safety_equipment_questions',
            'safety_equipment_percentage', 'safety_equipment_risk',
            'brakes_steering_score', 'brakes_steering_max', 'brakes_steering_questions',
            'brakes_steering_percentage', 'brakes_steering_risk',
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
    
    def get_total_prechecklist_questions(self, obj):
        return TOTAL_PRECHECKLIST_QUESTIONS
    
    def get_section_weights(self, obj):
        return SECTION_WEIGHTS


class PostChecklistScoreSummarySerializer(serializers.ModelSerializer):
    """Serializer for Post-Checklist Score Summary"""
    
    section_summary = serializers.SerializerMethodField()
    trip_behavior_risk_display = serializers.SerializerMethodField()
    driving_behavior_risk_display = serializers.SerializerMethodField()
    post_trip_report_risk_display = serializers.SerializerMethodField()
    total_postchecklist_questions = serializers.SerializerMethodField()
    risk_status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = PostChecklistScoreSummary
        fields = [
            'id',
            'inspection',
            # Trip Behavior
            'trip_behavior_score',
            'trip_behavior_max',
            'trip_behavior_questions',
            'trip_behavior_percentage',
            'trip_behavior_risk',
            'trip_behavior_risk_display',
            # Driving Behavior
            'driving_behavior_score',
            'driving_behavior_max',
            'driving_behavior_questions',
            'driving_behavior_percentage',
            'driving_behavior_risk',
            'driving_behavior_risk_display',
            # Post-Trip Report
            'post_trip_report_score',
            'post_trip_report_max',
            'post_trip_report_questions',
            'post_trip_report_percentage',
            'post_trip_report_risk',
            'post_trip_report_risk_display',
            # Totals
            'total_score',
            'max_possible_score',
            'total_questions',
            'total_postchecklist_questions',
            'score_percentage',
            'risk_status',
            'risk_status_display',
            'section_summary',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields
    
    def get_section_summary(self, obj):
        return obj.get_section_summary()
    
    def get_trip_behavior_risk_display(self, obj):
        from ..models import get_section_risk_display
        return get_section_risk_display(obj.trip_behavior_risk)
    
    def get_driving_behavior_risk_display(self, obj):
        from ..models import get_section_risk_display
        return get_section_risk_display(obj.driving_behavior_risk)
    
    def get_post_trip_report_risk_display(self, obj):
        from ..models import get_section_risk_display
        return get_section_risk_display(obj.post_trip_report_risk)
    
    def get_total_postchecklist_questions(self, obj):
        return TOTAL_POSTCHECKLIST_QUESTIONS
    
    def get_risk_status_display(self, obj):
        from ..models import get_section_risk_display
        return get_section_risk_display(obj.risk_status)


class FinalScoreSummarySerializer(serializers.ModelSerializer):
    """Serializer for Final Score Summary"""
    
    breakdown = serializers.SerializerMethodField()
    final_risk_display = serializers.SerializerMethodField()
    final_status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = FinalScoreSummary
        fields = [
            'id',
            'inspection',
            # Pre-Checklist (50%)
            'pre_checklist_score',
            'pre_checklist_max',
            'pre_checklist_percentage',
            'pre_checklist_weighted',
            # Post-Checklist (50%)
            'post_checklist_score',
            'post_checklist_max',
            'post_checklist_percentage',
            'post_checklist_weighted',
            # Final Results
            'final_percentage',
            'final_risk_level',
            'final_risk_display',
            'final_status',
            'final_status_display',
            'final_comment',
            'breakdown',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields
    
    def get_breakdown(self, obj):
        return obj.get_breakdown()
    
    def get_final_risk_display(self, obj):
        from ..models import get_final_risk_display
        return get_final_risk_display(obj.final_risk_level)
    
    def get_final_status_display(self, obj):
        return obj.get_final_status_display()
