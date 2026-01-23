from rest_framework import serializers
from ..models import CorrectiveMeasure, EnforcementAction


class CorrectiveMeasureSerializer(serializers.ModelSerializer):
    """Serializer for Corrective Measure"""
    
    class Meta:
        model = CorrectiveMeasure
        fields = [
            'id',
            'inspection',
            'measure_type',
            'required',
            'due_date',
            'completed',
            'completed_date',
            'notes',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'inspection', 'created_at', 'updated_at']
    
    def validate(self, attrs):
        """Cross-field validation"""
        completed = attrs.get('completed')
        if completed is None and self.instance:
            completed = self.instance.completed
        
        completed_date = attrs.get('completed_date')
        if not completed_date and self.instance:
            completed_date = self.instance.completed_date
        
        # If completed, must have completion date
        if completed and not completed_date:
            raise serializers.ValidationError({
                'completed_date': 'Completion date required when measure is marked as completed.'
            })
        
        # If not completed, should not have completion date
        if not completed and completed_date:
            raise serializers.ValidationError({
                'completed': 'Cannot set completion date without marking as completed.'
            })
        
        return attrs


class EnforcementActionSerializer(serializers.ModelSerializer):
    """Serializer for Enforcement Action"""
    
    class Meta:
        model = EnforcementAction
        fields = [
            'id',
            'inspection',
            'action_type',
            'is_applied',
            'start_date',
            'end_date',
            'notes',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'inspection', 'created_at', 'updated_at']
    
    def validate(self, attrs):
        """Cross-field validation"""
        is_applied = attrs.get('is_applied')
        if is_applied is None and self.instance:
            is_applied = self.instance.is_applied
        
        start_date = attrs.get('start_date')
        if not start_date and self.instance:
            start_date = self.instance.start_date
        
        action_type = attrs.get('action_type')
        if not action_type and self.instance:
            action_type = self.instance.action_type
        
        end_date = attrs.get('end_date')
        if not end_date and self.instance:
            end_date = self.instance.end_date
        
        # If applied, must have start date
        if is_applied and not start_date:
            raise serializers.ValidationError({
                'start_date': 'Start date required when action is applied.'
            })
        
        # For suspension, validate dates
        if action_type == 'suspension':
            if end_date and start_date:
                if end_date <= start_date:
                    raise serializers.ValidationError({
                        'end_date': 'End date must be after start date for suspension.'
                    })
        
        return attrs
