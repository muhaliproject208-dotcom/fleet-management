from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Driver
import re

User = get_user_model()


class CreatedBySerializer(serializers.ModelSerializer):
    """Nested serializer for created_by user information"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'full_name', 'email']
        read_only_fields = ['id', 'full_name', 'email']


class DriverListSerializer(serializers.ModelSerializer):
    """Serializer for listing drivers (compact view)"""
    average_risk_score = serializers.SerializerMethodField()
    risk_level = serializers.SerializerMethodField()
    
    class Meta:
        model = Driver
        fields = [
            'id',
            'driver_id',
            'full_name',
            'license_number',
            'phone_number',
            'is_active',
            'average_risk_score',
            'risk_level'
        ]
        read_only_fields = ['id', 'driver_id', 'average_risk_score', 'risk_level']
    
    def get_average_risk_score(self, obj):
        """Get average risk score for driver"""
        return obj.get_average_risk_score()
    
    def get_risk_level(self, obj):
        """Get risk level for driver"""
        return obj.get_risk_level()
    
    def validate_license_number(self, value):
        """Validate license number format and uniqueness"""
        if not value:
            raise serializers.ValidationError("License number is required.")
        
        # Allow alphanumeric characters and dashes
        if not re.match(r'^[A-Za-z0-9\-]+$', value):
            raise serializers.ValidationError(
                "License number must contain only alphanumeric characters and dashes."
            )
        
        # Check uniqueness (excluding current instance during updates)
        instance_id = self.instance.id if self.instance else None
        if Driver.objects.filter(license_number=value).exclude(id=instance_id).exists():
            raise serializers.ValidationError(
                "Driver with this license number already exists."
            )
        
        return value
    
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
                "Invalid phone number format. Expected format: +260971234567"
            )
        
        return value


class DriverDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed driver view with all fields"""
    created_by = CreatedBySerializer(read_only=True)
    average_risk_score = serializers.SerializerMethodField()
    risk_level = serializers.SerializerMethodField()
    
    class Meta:
        model = Driver
        fields = [
            'id',
            'driver_id',
            'full_name',
            'license_number',
            'phone_number',
            'email',
            'is_active',
            'average_risk_score',
            'risk_level',
            'created_at',
            'updated_at',
            'created_by'
        ]
        read_only_fields = ['id', 'driver_id', 'created_at', 'updated_at', 'created_by', 'average_risk_score', 'risk_level']
    
    def get_average_risk_score(self, obj):
        """Get average risk score for driver"""
        return obj.get_average_risk_score()
    
    def get_risk_level(self, obj):
        """Get risk level for driver"""
        return obj.get_risk_level()
    
    def validate_license_number(self, value):
        """Validate license number format and uniqueness"""
        if not value:
            raise serializers.ValidationError("License number is required.")
        
        # Allow alphanumeric characters and dashes
        if not re.match(r'^[A-Za-z0-9\-]+$', value):
            raise serializers.ValidationError(
                "License number must contain only alphanumeric characters and dashes."
            )
        
        # Check uniqueness (excluding current instance during updates)
        instance_id = self.instance.id if self.instance else None
        if Driver.objects.filter(license_number=value).exclude(id=instance_id).exists():
            raise serializers.ValidationError(
                "Driver with this license number already exists."
            )
        
        return value
    
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
                "Invalid phone number format. Expected format: +260971234567"
            )
        
        return value
    
    def validate(self, attrs):
        """Additional validation for deactivation"""
        # Check if trying to deactivate a driver
        if self.instance and 'is_active' in attrs and not attrs['is_active']:
            # Check if driver is referenced in any inspection
            # This will be implemented when inspection module is added
            # For now, we'll allow deactivation
            pass
        
        return attrs
