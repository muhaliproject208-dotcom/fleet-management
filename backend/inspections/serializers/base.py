from rest_framework import serializers
from django.contrib.auth import get_user_model
from datetime import date

from ..models import PreTripInspection, InspectionStatus
from drivers.models import Driver
from vehicles.models import Vehicle
from mechanics.models import Mechanic

User = get_user_model()


class DriverBasicSerializer(serializers.ModelSerializer):
    """Nested serializer for driver information"""
    class Meta:
        model = Driver
        fields = ['id', 'driver_id', 'full_name']
        read_only_fields = ['id', 'driver_id', 'full_name']


class VehicleBasicSerializer(serializers.ModelSerializer):
    """Nested serializer for vehicle information"""
    class Meta:
        model = Vehicle
        fields = ['id', 'vehicle_id', 'registration_number']
        read_only_fields = ['id', 'vehicle_id', 'registration_number']


class VehicleDetailedSerializer(serializers.ModelSerializer):
    """Nested serializer for vehicle information with type"""
    class Meta:
        model = Vehicle
        fields = ['id', 'vehicle_id', 'registration_number', 'vehicle_type']
        read_only_fields = ['id', 'vehicle_id', 'registration_number', 'vehicle_type']


class UserBasicSerializer(serializers.ModelSerializer):
    """Nested serializer for user information"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'full_name']
        read_only_fields = ['id', 'full_name']


class UserDetailedSerializer(serializers.ModelSerializer):
    """Nested serializer for user information with email"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'full_name', 'email']
        read_only_fields = ['id', 'full_name', 'email']


class MechanicBasicSerializer(serializers.ModelSerializer):
    """Nested serializer for mechanic information"""
    class Meta:
        model = Mechanic
        fields = ['id', 'mechanic_id', 'full_name']
        read_only_fields = ['id', 'mechanic_id', 'full_name']


class InspectionListSerializer(serializers.ModelSerializer):
    """Serializer for listing inspections (compact view)"""
    driver = DriverBasicSerializer(read_only=True)
    vehicle = VehicleBasicSerializer(read_only=True)
    supervisor = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = PreTripInspection
        fields = [
            'id',
            'inspection_id',
            'inspection_date',
            'route',
            'status',
            'driver',
            'vehicle',
            'supervisor',
            'created_at'
        ]
        read_only_fields = fields


class InspectionDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed inspection view with all fields"""
    driver = DriverBasicSerializer(read_only=True)
    vehicle = VehicleDetailedSerializer(read_only=True)
    supervisor = UserDetailedSerializer(read_only=True)
    mechanic = MechanicBasicSerializer(read_only=True)
    approved_by = UserDetailedSerializer(read_only=True)
    
    class Meta:
        model = PreTripInspection
        fields = [
            'id',
            'inspection_id',
            'inspection_date',
            'route',
            'approved_driving_hours',
            'approved_rest_stops',
            'status',
            'driver',
            'vehicle',
            'supervisor',
            'mechanic',
            'approved_by',
            'approval_status_updated_at',
            'rejection_reason',
            'created_at',
            'updated_at'
        ]
        read_only_fields = fields


class InspectionCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating inspections"""
    
    class Meta:
        model = PreTripInspection
        fields = [
            'id',
            'inspection_id',
            'driver',
            'vehicle',
            'mechanic',
            'inspection_date',
            'route',
            'approved_driving_hours',
            'approved_rest_stops',
            'status',
            'supervisor',
            'approved_by',
            'rejection_reason',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'inspection_id',
            'status',
            'supervisor',
            'approved_by',
            'rejection_reason',
            'created_at',
            'updated_at'
        ]
    
    def validate_driver(self, value):
        """Validate driver is active"""
        if not value.is_active:
            raise serializers.ValidationError("Selected driver is not active.")
        return value
    
    def validate_vehicle(self, value):
        """Validate vehicle is active"""
        if not value.is_active:
            raise serializers.ValidationError("Selected vehicle is not active.")
        return value
    
    def validate_mechanic(self, value):
        """Validate mechanic is active (if provided)"""
        if value and not value.is_active:
            raise serializers.ValidationError("Selected mechanic is not active.")
        return value
    
    def validate_inspection_date(self, value):
        """Validate inspection date cannot be in the future"""
        if value > date.today():
            raise serializers.ValidationError("Inspection date cannot be in the future.")
        return value
    
    def validate(self, attrs):
        """Additional validation"""
        # Check if trying to edit a submitted/approved inspection
        if self.instance and not self.instance.can_edit():
            raise serializers.ValidationError({
                'error': f"Cannot edit inspection after submission. Current status: {self.instance.status}"
            })
        
        return attrs
    
    def create(self, validated_data):
        """Create inspection with supervisor set to current user"""
        # Supervisor will be set in the view's perform_create
        return super().create(validated_data)
