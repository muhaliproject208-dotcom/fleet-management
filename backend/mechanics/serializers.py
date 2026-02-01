from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Mechanic, CertificationStatus
import re

User = get_user_model()


class CreatedBySerializer(serializers.ModelSerializer):
    """Nested serializer for created_by user information"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'full_name', 'email']
        read_only_fields = ['id', 'full_name', 'email']


class MechanicListSerializer(serializers.ModelSerializer):
    """Serializer for listing mechanics (compact view)"""
    certification_status_display = serializers.CharField(
        source='get_certification_status_display', 
        read_only=True
    )
    
    class Meta:
        model = Mechanic
        fields = [
            'id',
            'mechanic_id',
            'full_name',
            'specialization',
            'phone_number',
            'certification_status',
            'certification_status_display',
            'is_active'
        ]
        read_only_fields = ['id', 'mechanic_id', 'certification_status_display']
    
    def validate_phone_number(self, value):
        """Validate phone number format"""
        if not value:
            raise serializers.ValidationError("Phone number is required.")
        
        if not value.startswith('+'):
            raise serializers.ValidationError(
                "Phone number must start with + and country code."
            )
        
        # Basic validation for phone format (+ followed by digits)
        if not re.match(r'^\+\d{10,15}$', value):
            raise serializers.ValidationError(
                "Invalid phone number format. Expected format: +260977654321"
            )
        
        return value
    
    def validate_specialization(self, value):
        """Validate specialization is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Specialization cannot be empty.")
        
        return value.strip()


class MechanicDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed mechanic view with all fields"""
    created_by = CreatedBySerializer(read_only=True)
    certification_status_display = serializers.CharField(
        source='get_certification_status_display', 
        read_only=True
    )
    
    class Meta:
        model = Mechanic
        fields = [
            'id',
            'mechanic_id',
            'full_name',
            'specialization',
            'phone_number',
            'certification_status',
            'certification_status_display',
            'is_active',
            'created_at',
            'updated_at',
            'created_by'
        ]
        read_only_fields = ['id', 'mechanic_id', 'certification_status_display', 'created_at', 'updated_at', 'created_by']
    
    def validate_phone_number(self, value):
        """Validate phone number format"""
        if not value:
            raise serializers.ValidationError("Phone number is required.")
        
        if not value.startswith('+'):
            raise serializers.ValidationError(
                "Phone number must start with + and country code."
            )
        
        # Basic validation for phone format (+ followed by digits)
        if not re.match(r'^\+\d{10,15}$', value):
            raise serializers.ValidationError(
                "Invalid phone number format. Expected format: +260977654321"
            )
        
        return value
    
    def validate_specialization(self, value):
        """Validate specialization is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Specialization cannot be empty.")
        
        return value.strip()
