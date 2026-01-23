from rest_framework import serializers
from ..models import HealthFitnessCheck


class HealthFitnessCheckSerializer(serializers.ModelSerializer):
    """Serializer for Health & Fitness Check"""
    
    class Meta:
        model = HealthFitnessCheck
        fields = [
            'id',
            'inspection',
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
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'inspection', 'created_at', 'updated_at']
    
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
