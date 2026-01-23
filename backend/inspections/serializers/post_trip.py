from rest_framework import serializers
from ..models import PostTripReport, RiskScoreSummary


class PostTripReportSerializer(serializers.ModelSerializer):
    """Serializer for Post-Trip Report"""
    
    class Meta:
        model = PostTripReport
        fields = [
            'id',
            'inspection',
            'vehicle_fault_submitted',
            'fault_notes',
            'final_inspection_signed',
            'compliance_with_policy',
            'attitude_cooperation',
            'incidents_recorded',
            'incident_notes',
            'total_trip_duration',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'inspection', 'created_at', 'updated_at']
    
    def validate(self, attrs):
        """Cross-field validation"""
        # Get values from attrs or instance if updating
        vehicle_fault = attrs.get('vehicle_fault_submitted')
        if vehicle_fault is None and self.instance:
            vehicle_fault = self.instance.vehicle_fault_submitted
        
        fault_notes = attrs.get('fault_notes', '')
        if not fault_notes and self.instance:
            fault_notes = self.instance.fault_notes
        
        incidents = attrs.get('incidents_recorded')
        if incidents is None and self.instance:
            incidents = self.instance.incidents_recorded
        
        incident_notes = attrs.get('incident_notes', '')
        if not incident_notes and self.instance:
            incident_notes = self.instance.incident_notes
        
        # Validate vehicle fault requires notes
        if vehicle_fault and not fault_notes.strip():
            raise serializers.ValidationError({
                'fault_notes': 'Fault details required when vehicle fault is submitted.'
            })
        
        # Validate incidents require notes
        if incidents and not incident_notes.strip():
            raise serializers.ValidationError({
                'incident_notes': 'Incident details required when incidents are recorded.'
            })
        
        return attrs


class RiskScoreSummarySerializer(serializers.ModelSerializer):
    """Serializer for Risk Score Summary"""
    
    class Meta:
        model = RiskScoreSummary
        fields = [
            'id',
            'inspection',
            'total_points_this_trip',
            'risk_level',
            'total_points_30_days',
            'risk_level_30_days',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'inspection',
            'total_points_this_trip',
            'risk_level',
            'total_points_30_days',
            'risk_level_30_days',
            'created_at',
            'updated_at'
        ]
