from django.db import models
from django.core.exceptions import ValidationError
from .base import PreTripInspection


class CheckStatus(models.TextChoices):
    """Status choices for checks"""
    PASS = 'pass', 'Pass'
    FAIL = 'fail', 'Fail'


class BaseVehicleCheck(models.Model):
    """Abstract base model for all vehicle inspection checks"""
    
    inspection = models.ForeignKey(
        PreTripInspection,
        on_delete=models.CASCADE,
        help_text="Associated pre-trip inspection"
    )
    check_item = models.CharField(
        max_length=100,
        help_text="Item being checked"
    )
    status = models.CharField(
        max_length=10,
        choices=CheckStatus.choices,
        help_text="Pass or fail status"
    )
    remarks = models.TextField(
        blank=True,
        help_text="Additional remarks or observations"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
        ordering = ['-created_at']
    
    def has_critical_failure(self):
        """
        Return True if this check item is critical and status is fail.
        To be overridden in subclasses to define critical items.
        """
        return False
    
    def __str__(self):
        return f"{self.inspection.inspection_id} - {self.check_item}: {self.status}"


class VehicleExteriorCheck(BaseVehicleCheck):
    """Vehicle exterior inspection checks"""
    
    inspection = models.ForeignKey(
        PreTripInspection,
        on_delete=models.CASCADE,
        related_name='exterior_checks',
        help_text="Associated pre-trip inspection"
    )
    
    class ExteriorItems(models.TextChoices):
        TIRES = 'tires', 'Tires'
        LIGHTS = 'lights', 'Lights'
        MIRRORS = 'mirrors', 'Mirrors'
        WINDSHIELD = 'windshield', 'Windshield'
        BODY_CONDITION = 'body_condition', 'Body Condition'
        LOOSE_PARTS = 'loose_parts', 'Loose Parts'
        LEAKS = 'leaks', 'Leaks'
    
    class Meta:
        verbose_name = 'Vehicle Exterior Check'
        verbose_name_plural = 'Vehicle Exterior Checks'
        ordering = ['-created_at']
    
    def has_critical_failure(self):
        """Tires and lights are critical items"""
        critical_items = [self.ExteriorItems.TIRES, self.ExteriorItems.LIGHTS]
        return self.check_item in critical_items and self.status == CheckStatus.FAIL
    
    def clean(self):
        """Validate check_item is valid for exterior checks"""
        super().clean()
        if self.check_item not in self.ExteriorItems.values:
            raise ValidationError({
                'check_item': f'Invalid exterior check item. Must be one of: {", ".join(self.ExteriorItems.values)}'
            })


class EngineFluidCheck(BaseVehicleCheck):
    """Engine and fluid inspection checks"""
    
    inspection = models.ForeignKey(
        PreTripInspection,
        on_delete=models.CASCADE,
        related_name='engine_fluid_checks',
        help_text="Associated pre-trip inspection"
    )
    
    class FluidItems(models.TextChoices):
        ENGINE_OIL = 'engine_oil', 'Engine Oil'
        COOLANT = 'coolant', 'Coolant'
        BRAKE_FLUID = 'brake_fluid', 'Brake Fluid'
        TRANSMISSION_FLUID = 'transmission_fluid', 'Transmission Fluid'
        POWER_STEERING_FLUID = 'power_steering_fluid', 'Power Steering Fluid'
        BATTERY = 'battery', 'Battery'
    
    class Meta:
        verbose_name = 'Engine & Fluid Check'
        verbose_name_plural = 'Engine & Fluid Checks'
        ordering = ['-created_at']
    
    def has_critical_failure(self):
        """Engine oil and brake fluid are critical items"""
        critical_items = [self.FluidItems.ENGINE_OIL, self.FluidItems.BRAKE_FLUID]
        return self.check_item in critical_items and self.status == CheckStatus.FAIL
    
    def clean(self):
        """Validate check_item is valid for engine/fluid checks"""
        super().clean()
        if self.check_item not in self.FluidItems.values:
            raise ValidationError({
                'check_item': f'Invalid fluid check item. Must be one of: {", ".join(self.FluidItems.values)}'
            })


class InteriorCabinCheck(BaseVehicleCheck):
    """Interior cabin inspection checks"""
    
    inspection = models.ForeignKey(
        PreTripInspection,
        on_delete=models.CASCADE,
        related_name='interior_cabin_checks',
        help_text="Associated pre-trip inspection"
    )
    
    class InteriorItems(models.TextChoices):
        DASHBOARD_INDICATORS = 'dashboard_indicators', 'Dashboard Indicators'
        SEATBELTS = 'seatbelts', 'Seatbelts'
        HORN = 'horn', 'Horn'
        FIRE_EXTINGUISHER = 'fire_extinguisher', 'Fire Extinguisher'
        FIRST_AID_KIT = 'first_aid_kit', 'First Aid Kit'
        SAFETY_TRIANGLES = 'safety_triangles', 'Safety Triangles'
    
    class Meta:
        verbose_name = 'Interior & Cabin Check'
        verbose_name_plural = 'Interior & Cabin Checks'
        ordering = ['-created_at']
    
    def has_critical_failure(self):
        """Seatbelts are critical items"""
        critical_items = [self.InteriorItems.SEATBELTS]
        return self.check_item in critical_items and self.status == CheckStatus.FAIL
    
    def clean(self):
        """Validate check_item is valid for interior checks"""
        super().clean()
        if self.check_item not in self.InteriorItems.values:
            raise ValidationError({
                'check_item': f'Invalid interior check item. Must be one of: {", ".join(self.InteriorItems.values)}'
            })


class FunctionalCheck(BaseVehicleCheck):
    """Functional system inspection checks"""
    
    inspection = models.ForeignKey(
        PreTripInspection,
        on_delete=models.CASCADE,
        related_name='functional_checks',
        help_text="Associated pre-trip inspection"
    )
    
    class FunctionalItems(models.TextChoices):
        BRAKES = 'brakes', 'Brakes'
        STEERING = 'steering', 'Steering'
        SUSPENSION = 'suspension', 'Suspension'
        HVAC = 'hvac', 'HVAC'
    
    class Meta:
        verbose_name = 'Functional Check'
        verbose_name_plural = 'Functional Checks'
        ordering = ['-created_at']
    
    def has_critical_failure(self):
        """Brakes and steering are critical items"""
        critical_items = [self.FunctionalItems.BRAKES, self.FunctionalItems.STEERING]
        return self.check_item in critical_items and self.status == CheckStatus.FAIL
    
    def clean(self):
        """Validate check_item is valid for functional checks"""
        super().clean()
        if self.check_item not in self.FunctionalItems.values:
            raise ValidationError({
                'check_item': f'Invalid functional check item. Must be one of: {", ".join(self.FunctionalItems.values)}'
            })


FunctionalCheck._meta.get_field('inspection').remote_field.related_name = 'functional_checks'


class SafetyEquipmentCheck(BaseVehicleCheck):
    """Safety equipment inspection checks"""
    
    inspection = models.ForeignKey(
        PreTripInspection,
        on_delete=models.CASCADE,
        related_name='safety_equipment_checks',
        help_text="Associated pre-trip inspection"
    )
    
    class SafetyItems(models.TextChoices):
        FIRE_EXTINGUISHER = 'fire_extinguisher', 'Fire Extinguisher'
        FIRST_AID_KIT = 'first_aid_kit', 'First Aid Kit'
        REFLECTIVE_TRIANGLES = 'reflective_triangles', 'Reflective Triangles'
        WHEEL_CHOCKS = 'wheel_chocks', 'Wheel Chocks'
        SPARE_TYRE = 'spare_tyre', 'Spare Tyre'
        TORCH = 'torch', 'Torch'
        EMERGENCY_CONTACTS = 'emergency_contacts', 'Emergency Contacts'
        GPS_TRACKER = 'gps_tracker', 'GPS Tracker'
    
    class Meta:
        verbose_name = 'Safety Equipment Check'
        verbose_name_plural = 'Safety Equipment Checks'
        ordering = ['-created_at']
    
    def has_critical_failure(self):
        """Fire extinguisher and first aid kit are critical items"""
        critical_items = [self.SafetyItems.FIRE_EXTINGUISHER, self.SafetyItems.FIRST_AID_KIT]
        return self.check_item in critical_items and self.status == CheckStatus.FAIL
    
    def clean(self):
        """Validate check_item is valid for safety equipment checks"""
        super().clean()
        if self.check_item not in self.SafetyItems.values:
            raise ValidationError({
                'check_item': f'Invalid safety equipment item. Must be one of: {", ".join(self.SafetyItems.values)}'
            })


SafetyEquipmentCheck._meta.get_field('inspection').remote_field.related_name = 'safety_equipment_checks'


class BrakesSteeringCheck(BaseVehicleCheck):
    """
    Brakes and Steering inspection checks - Critical safety items.
    Separate model to ensure these critical checks are always visible and tracked.
    """
    
    inspection = models.ForeignKey(
        PreTripInspection,
        on_delete=models.CASCADE,
        related_name='brakes_steering_checks',
        help_text="Associated pre-trip inspection"
    )
    
    class BrakesSteeringItems(models.TextChoices):
        BRAKES_CONDITION = 'brakes_condition', 'Brakes Condition'
        BRAKE_PADS = 'brake_pads', 'Brake Pads'
        BRAKE_FLUID_LEVEL = 'brake_fluid_level', 'Brake Fluid Level'
        BRAKE_LINES = 'brake_lines', 'Brake Lines'
        HANDBRAKE = 'handbrake', 'Handbrake/Parking Brake'
        STEERING_WHEEL = 'steering_wheel', 'Steering Wheel'
        STEERING_RESPONSE = 'steering_response', 'Steering Response'
        POWER_STEERING = 'power_steering', 'Power Steering'
        STEERING_FLUID = 'steering_fluid', 'Steering Fluid Level'
    
    class Meta:
        verbose_name = 'Brakes & Steering Check'
        verbose_name_plural = 'Brakes & Steering Checks'
        ordering = ['-created_at']
    
    def has_critical_failure(self):
        """All brakes and steering items are critical"""
        return self.status == CheckStatus.FAIL
    
    def clean(self):
        """Validate check_item is valid for brakes/steering checks"""
        super().clean()
        if self.check_item not in self.BrakesSteeringItems.values:
            raise ValidationError({
                'check_item': f'Invalid brakes/steering check item. Must be one of: {", ".join(self.BrakesSteeringItems.values)}'
            })


BrakesSteeringCheck._meta.get_field('inspection').remote_field.related_name = 'brakes_steering_checks'
