from rest_framework import serializers
from ..models import SupervisorRemarks, EvaluationSummary


class SupervisorRemarksSerializer(serializers.ModelSerializer):
    """Serializer for Supervisor Remarks"""
    
    class Meta:
        model = SupervisorRemarks
        fields = [
            'id',
            'inspection',
            'supervisor_name',
            'remarks',
            'recommendation',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'inspection', 'supervisor_name', 'created_at', 'updated_at']


class EvaluationSummarySerializer(serializers.ModelSerializer):
    """Serializer for Evaluation Summary"""
    average_score = serializers.SerializerMethodField()
    
    class Meta:
        model = EvaluationSummary
        fields = [
            'id',
            'inspection',
            'pre_trip_inspection_score',
            'driving_conduct_score',
            'incident_management_score',
            'post_trip_reporting_score',
            'compliance_documentation_score',
            'average_score',
            'overall_performance',
            'comments',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'inspection', 'overall_performance', 'average_score', 'created_at', 'updated_at']
    
    def get_average_score(self, obj):
        """Return calculated average score"""
        return round(obj.calculate_average_score(), 2)
    
    def validate_pre_trip_inspection_score(self, value):
        """Validate score is between 1 and 5"""
        if value < 1 or value > 5:
            raise serializers.ValidationError('Score must be between 1 and 5.')
        return value
    
    def validate_driving_conduct_score(self, value):
        """Validate score is between 1 and 5"""
        if value < 1 or value > 5:
            raise serializers.ValidationError('Score must be between 1 and 5.')
        return value
    
    def validate_incident_management_score(self, value):
        """Validate score is between 1 and 5"""
        if value < 1 or value > 5:
            raise serializers.ValidationError('Score must be between 1 and 5.')
        return value
    
    def validate_post_trip_reporting_score(self, value):
        """Validate score is between 1 and 5"""
        if value < 1 or value > 5:
            raise serializers.ValidationError('Score must be between 1 and 5.')
        return value
    
    def validate_compliance_documentation_score(self, value):
        """Validate score is between 1 and 5"""
        if value < 1 or value > 5:
            raise serializers.ValidationError('Score must be between 1 and 5.')
        return value
