from rest_framework import serializers
from ..models import InspectionSignOff
from ..models.signoff import SignOffRole


class InspectionSignOffSerializer(serializers.ModelSerializer):
    """Serializer for Inspection Sign-Offs"""
    
    class Meta:
        model = InspectionSignOff
        fields = [
            'id',
            'inspection',
            'role',
            'signer_name',
            'signed_at'
        ]
        read_only_fields = ['id', 'inspection', 'signed_at']
    
    def validate_role(self, value):
        """Validate role is valid"""
        valid_roles = SignOffRole.values
        if value not in valid_roles:
            raise serializers.ValidationError(
                f'Invalid role. Must be one of: {", ".join(valid_roles)}'
            )
        return value
    
    def validate_signer_name(self, value):
        """Validate signer name is provided"""
        if not value or not value.strip():
            raise serializers.ValidationError('Signer name is required.')
        return value.strip()
