from rest_framework import serializers
from ..models import (
    VehicleExteriorCheck,
    EngineFluidCheck,
    InteriorCabinCheck,
    FunctionalCheck,
    SafetyEquipmentCheck,
)


class VehicleExteriorCheckSerializer(serializers.ModelSerializer):
    """Serializer for Vehicle Exterior Checks"""
    
    class Meta:
        model = VehicleExteriorCheck
        fields = [
            'id',
            'inspection',
            'check_item',
            'status',
            'remarks',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'inspection', 'created_at', 'updated_at']
    
    def validate_check_item(self, value):
        """Validate check_item is valid for exterior checks"""
        valid_items = VehicleExteriorCheck.ExteriorItems.values
        if value not in valid_items:
            raise serializers.ValidationError(
                f'Invalid exterior check item. Must be one of: {", ".join(valid_items)}'
            )
        return value


class EngineFluidCheckSerializer(serializers.ModelSerializer):
    """Serializer for Engine & Fluid Checks"""
    
    class Meta:
        model = EngineFluidCheck
        fields = [
            'id',
            'inspection',
            'check_item',
            'status',
            'remarks',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'inspection', 'created_at', 'updated_at']
    
    def validate_check_item(self, value):
        """Validate check_item is valid for engine/fluid checks"""
        valid_items = EngineFluidCheck.FluidItems.values
        if value not in valid_items:
            raise serializers.ValidationError(
                f'Invalid fluid check item. Must be one of: {", ".join(valid_items)}'
            )
        return value


class InteriorCabinCheckSerializer(serializers.ModelSerializer):
    """Serializer for Interior & Cabin Checks"""
    
    class Meta:
        model = InteriorCabinCheck
        fields = [
            'id',
            'inspection',
            'check_item',
            'status',
            'remarks',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'inspection', 'created_at', 'updated_at']
    
    def validate_check_item(self, value):
        """Validate check_item is valid for interior checks"""
        valid_items = InteriorCabinCheck.InteriorItems.values
        if value not in valid_items:
            raise serializers.ValidationError(
                f'Invalid interior check item. Must be one of: {", ".join(valid_items)}'
            )
        return value


class FunctionalCheckSerializer(serializers.ModelSerializer):
    """Serializer for Functional Checks"""
    
    class Meta:
        model = FunctionalCheck
        fields = [
            'id',
            'inspection',
            'check_item',
            'status',
            'remarks',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'inspection', 'created_at', 'updated_at']
    
    def validate_check_item(self, value):
        """Validate check_item is valid for functional checks"""
        valid_items = FunctionalCheck.FunctionalItems.values
        if value not in valid_items:
            raise serializers.ValidationError(
                f'Invalid functional check item. Must be one of: {", ".join(valid_items)}'
            )
        return value


class SafetyEquipmentCheckSerializer(serializers.ModelSerializer):
    """Serializer for Safety Equipment Checks"""
    
    class Meta:
        model = SafetyEquipmentCheck
        fields = [
            'id',
            'inspection',
            'check_item',
            'status',
            'remarks',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'inspection', 'created_at', 'updated_at']
    
    def validate_check_item(self, value):
        """Validate check_item is valid for safety equipment checks"""
        valid_items = SafetyEquipmentCheck.SafetyItems.values
        if value not in valid_items:
            raise serializers.ValidationError(
                f'Invalid safety equipment item. Must be one of: {", ".join(valid_items)}'
            )
        return value
