from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Vehicle
from drivers.models import Driver
import re

User = get_user_model()


class CreatedBySerializer(serializers.ModelSerializer):
    """Nested serializer for created_by user information"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'full_name', 'email']
        read_only_fields = ['id', 'full_name', 'email']


class DriverBasicSerializer(serializers.ModelSerializer):
    """Nested serializer for driver information in vehicle details"""
    
    class Meta:
        model = Driver
        fields = ['id', 'driver_id', 'full_name', 'license_number', 'phone_number']
        read_only_fields = ['id', 'driver_id', 'full_name', 'license_number', 'phone_number']


class VehicleListSerializer(serializers.ModelSerializer):
    """Serializer for listing vehicles (compact view)"""
    driver_name = serializers.CharField(source='driver.full_name', read_only=True, allow_null=True)
    
    class Meta:
        model = Vehicle
        fields = [
            'id',
            'vehicle_id',
            'registration_number',
            'vehicle_type',
            'driver_name',
            'is_active'
        ]
        read_only_fields = ['id', 'vehicle_id', 'driver_name']
    
    def validate_registration_number(self, value):
        """Validate registration number format and uniqueness"""
        if not value:
            raise serializers.ValidationError("Registration number is required.")
        
        # Normalize to uppercase
        value = value.upper()
        
        # Allow alphanumeric characters and spaces
        if not re.match(r'^[A-Z0-9\s]+$', value):
            raise serializers.ValidationError(
                "Registration number must contain only alphanumeric characters and spaces."
            )
        
        # Check uniqueness (excluding current instance during updates)
        instance_id = self.instance.id if self.instance else None
        if Vehicle.objects.filter(registration_number=value).exclude(id=instance_id).exists():
            raise serializers.ValidationError(
                "Vehicle with this registration number already exists."
            )
        
        return value
    
    def validate_vehicle_type(self, value):
        """Validate vehicle type is not empty and is a valid choice"""
        if not value or not value.strip():
            raise serializers.ValidationError("Vehicle type cannot be empty.")
        
        value = value.strip()
        valid_choices = [choice[0] for choice in Vehicle.VEHICLE_TYPE_CHOICES]
        if value not in valid_choices:
            raise serializers.ValidationError(
                f"Invalid vehicle type. Must be one of: {', '.join(valid_choices)}"
            )
        
        return value


class VehicleDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed vehicle view with all fields"""
    created_by = CreatedBySerializer(read_only=True)
    driver = DriverBasicSerializer(read_only=True)
    driver_id = serializers.PrimaryKeyRelatedField(
        queryset=Driver.objects.filter(is_active=True),
        source='driver',
        required=False,
        allow_null=True,
        write_only=True,
        help_text="ID of the driver to assign to this vehicle"
    )
    
    class Meta:
        model = Vehicle
        fields = [
            'id',
            'vehicle_id',
            'registration_number',
            'vehicle_type',
            'driver',
            'driver_id',
            'last_vehicle_maintenance_date',
            'last_full_service_date',
            'last_partial_service_date',
            'is_active',
            'created_at',
            'updated_at',
            'created_by'
        ]
        read_only_fields = ['id', 'vehicle_id', 'created_at', 'updated_at', 'created_by', 'driver']
    
    def validate_registration_number(self, value):
        """Validate registration number format and uniqueness"""
        if not value:
            raise serializers.ValidationError("Registration number is required.")
        
        # Normalize to uppercase
        value = value.upper()
        
        # Allow alphanumeric characters and spaces
        if not re.match(r'^[A-Z0-9\s]+$', value):
            raise serializers.ValidationError(
                "Registration number must contain only alphanumeric characters and spaces."
            )
        
        # Check uniqueness (excluding current instance during updates)
        instance_id = self.instance.id if self.instance else None
        if Vehicle.objects.filter(registration_number=value).exclude(id=instance_id).exists():
            raise serializers.ValidationError(
                "Vehicle with this registration number already exists."
            )
        
        return value
    
    def validate_vehicle_type(self, value):
        """Validate vehicle type is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Vehicle type cannot be empty.")
        
        return value.strip()
    
    def validate_driver_id(self, value):
        """Validate driver assignment"""
        if value:
            # Check if driver is already assigned to another vehicle
            existing_vehicle = Vehicle.objects.filter(driver=value).first()
            if existing_vehicle and (not self.instance or existing_vehicle.id != self.instance.id):
                raise serializers.ValidationError(
                    f"Driver {value.full_name} is already assigned to vehicle {existing_vehicle.registration_number}."
                )
        
        return value
    
    def validate(self, attrs):
        """Additional validation for deactivation"""
        # Check if trying to deactivate a vehicle
        if self.instance and 'is_active' in attrs and not attrs['is_active']:
            # Check if vehicle is referenced in any active inspection
            # This will be implemented when inspection module is added
            pass
        
        return attrs
