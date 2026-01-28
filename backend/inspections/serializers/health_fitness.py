from rest_framework import serializers
from ..models import HealthFitnessCheck


class HealthFitnessCheckSerializer(serializers.ModelSerializer):
    """Serializer for Health & Fitness Check"""
    
    # Read-only computed fields
    score_earned = serializers.SerializerMethodField()
    score_max = serializers.SerializerMethodField()
    score_percentage = serializers.SerializerMethodField()
    is_travel_cleared = serializers.SerializerMethodField()
    clearance_message = serializers.SerializerMethodField()
    score_breakdown = serializers.SerializerMethodField()
    
    class Meta:
        model = HealthFitnessCheck
        fields = [
            'id',
            'inspection',
            'adequate_rest',
            'rest_clearance_status',
            'alcohol_test_status',
            'alcohol_test_remarks',
            'temperature_check_status',
            'temperature_value',
            'fit_for_duty',
            'medication_status',
            'medication_remarks',
            'no_health_impairment',
            'fatigue_checklist_completed',
            'fatigue_remarks',
            'section_score',
            'max_possible_score',
            'score_earned',
            'score_max',
            'score_percentage',
            'is_travel_cleared',
            'clearance_message',
            'score_breakdown',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id', 'inspection', 'rest_clearance_status', 
            'section_score', 'max_possible_score',
            'created_at', 'updated_at'
        ]
    
    def get_score_earned(self, obj):
        earned, _, _ = obj.calculate_score()
        return earned
    
    def get_score_max(self, obj):
        _, max_score, _ = obj.calculate_score()
        return max_score
    
    def get_score_percentage(self, obj):
        _, _, percentage = obj.calculate_score()
        return percentage
    
    def get_is_travel_cleared(self, obj):
        return obj.is_travel_cleared()
    
    def get_clearance_message(self, obj):
        return obj.get_clearance_message()
    
    def get_score_breakdown(self, obj):
        return obj.get_score_breakdown()
    
    def validate_alcohol_test_remarks(self, value):
        """Validate alcohol test remarks when test fails"""
        # This will be checked in the validate method with access to all fields
        return value
    
    def validate_medication_remarks(self, value):
        """Validate medication remarks when on medication"""
        # This will be checked in the validate method with access to all fields
        return value
    
    def validate_temperature_value(self, value):
        """Validate temperature range"""
        if value is not None:
            if not (35.0 <= value <= 39.0):
                raise serializers.ValidationError(
                    "Temperature value should be between 35.0°C and 39.0°C."
                )
        return value
    
    def validate(self, attrs):
        """Cross-field validation"""
        # Get values from attrs or instance if updating
        adequate_rest = attrs.get('adequate_rest')
        if adequate_rest is None and self.instance:
            adequate_rest = self.instance.adequate_rest
        
        alcohol_status = attrs.get('alcohol_test_status')
        if not alcohol_status and self.instance:
            alcohol_status = self.instance.alcohol_test_status
        
        alcohol_remarks = attrs.get('alcohol_test_remarks', '')
        if not alcohol_remarks and self.instance:
            alcohol_remarks = self.instance.alcohol_test_remarks
        
        medication_status = attrs.get('medication_status')
        if medication_status is None and self.instance:
            medication_status = self.instance.medication_status
        
        medication_remarks = attrs.get('medication_remarks', '')
        if not medication_remarks and self.instance:
            medication_remarks = self.instance.medication_remarks
        
        fit_for_duty = attrs.get('fit_for_duty')
        if fit_for_duty is None and self.instance:
            fit_for_duty = self.instance.fit_for_duty
        
        # CRITICAL: Validate adequate rest - driver must have rested 8+ hours
        if adequate_rest is False:
            raise serializers.ValidationError({
                'adequate_rest': 'Driver has not rested for 8 hours or more. Driver should NOT travel.',
                'travel_blocked': True,
                'block_message': '⚠️ TRAVEL NOT PERMITTED: Driver has not had adequate rest (8+ hours). The driver should not travel until they have rested sufficiently.'
            })
        
        # Validate alcohol test failure requires remarks
        if alcohol_status == 'fail':
            if not alcohol_remarks or not alcohol_remarks.strip():
                raise serializers.ValidationError({
                    'alcohol_test_remarks': 'Remarks required when alcohol test fails.'
                })
        
        # Validate medication status requires remarks
        if medication_status:
            if not medication_remarks or not medication_remarks.strip():
                raise serializers.ValidationError({
                    'medication_remarks': 'Medication details required when driver is on medication.'
                })
        
        # Validate fit for duty
        if not fit_for_duty:
            raise serializers.ValidationError({
                'error': 'Driver not fit for duty. Inspection cannot proceed.'
            })
        
        return attrs
