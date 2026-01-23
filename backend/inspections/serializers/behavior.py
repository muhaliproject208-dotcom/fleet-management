from rest_framework import serializers
from ..models import TripBehaviorMonitoring, DrivingBehaviorCheck


class TripBehaviorMonitoringSerializer(serializers.ModelSerializer):
    """Serializer for Trip Behavior Monitoring"""
    
    class Meta:
        model = TripBehaviorMonitoring
        fields = [
            'id',
            'inspection',
            'behavior_item',
            'status',
            'notes',
            'violation_points',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'inspection', 'violation_points', 'created_at', 'updated_at']
    
    def validate_behavior_item(self, value):
        """Validate behavior_item is valid"""
        valid_items = TripBehaviorMonitoring.BehaviorItems.values
        if value not in valid_items:
            raise serializers.ValidationError(
                f'Invalid behavior item. Must be one of: {", ".join(valid_items)}'
            )
        return value


class DrivingBehaviorCheckSerializer(serializers.ModelSerializer):
    """Serializer for Driving Behavior Check"""
    
    class Meta:
        model = DrivingBehaviorCheck
        fields = [
            'id',
            'inspection',
            'behavior_item',
            'status',
            'remarks',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'inspection', 'created_at', 'updated_at']
    
    def validate_behavior_item(self, value):
        """Validate behavior_item is valid"""
        valid_items = DrivingBehaviorCheck.BehaviorItems.values
        if value not in valid_items:
            raise serializers.ValidationError(
                f'Invalid behavior item. Must be one of: {", ".join(valid_items)}'
            )
        return value
