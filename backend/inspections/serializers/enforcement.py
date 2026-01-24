from rest_framework import serializers
from ..models import CorrectiveMeasure, EnforcementAction


class CorrectiveMeasureSerializer(serializers.ModelSerializer):
    """Serializer for Corrective Measure"""
    
    # Allow empty strings to be converted to None
    due_date = serializers.DateField(required=False, allow_null=True)
    completed_date = serializers.DateField(required=False, allow_null=True)
    
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
    
    def to_internal_value(self, data):
        """Convert empty strings to None for date fields"""
        if 'due_date' in data and data['due_date'] == '':
            data = data.copy()
            data['due_date'] = None
        if 'completed_date' in data and data['completed_date'] == '':
            data = data.copy()
            data['completed_date'] = None
        return super().to_internal_value(data)
    
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
    
    # Allow empty strings to be converted to None
    start_date = serializers.DateField(required=False, allow_null=True)
    end_date = serializers.DateField(required=False, allow_null=True)
    
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
    
    def to_internal_value(self, data):
        """Convert empty strings to None for date fields"""
        if 'start_date' in data and data['start_date'] == '':
            data = data.copy()
            data['start_date'] = None
        if 'end_date' in data and data['end_date'] == '':
            data = data.copy()
            data['end_date'] = None
        return super().to_internal_value(data)
    
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
