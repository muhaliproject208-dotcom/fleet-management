from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings


class Vehicle(models.Model):
    """
    Vehicle model for fleet management system.
    Vehicles are selected during pre-trip inspections and can be assigned to drivers.
    One-to-one relationship: Each vehicle can only have one driver and vice versa.
    """
    
    vehicle_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        db_index=True,
        help_text="Auto-generated vehicle ID in format VEH-XXXX"
    )
    registration_number = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text="Vehicle registration number (e.g., ALB 9345)"
    )
    vehicle_type = models.CharField(
        max_length=50,
        help_text="Vehicle type (e.g., Freight Truck, Van, Pickup)"
    )
    driver = models.OneToOneField(
        'drivers.Driver',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_vehicle',
        help_text="Driver assigned to this vehicle (one-to-one relationship)"
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Indicates if the vehicle is currently active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_vehicles',
        help_text="User who created this vehicle record"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['vehicle_id'], name='vehicles_vehicle_id_idx'),
            models.Index(fields=['registration_number'], name='vehicles_registration_idx'),
            models.Index(fields=['is_active'], name='vehicles_ve_is_acti_53dbe5_idx'),
        ]
        verbose_name = 'Vehicle'
        verbose_name_plural = 'Vehicles'
    
    def __str__(self):
        return f"{self.vehicle_id} - {self.registration_number}"
    
    def save(self, *args, **kwargs):
        """Override save to auto-generate vehicle_id and normalize registration number"""
        if not self.vehicle_id:
            self.vehicle_id = self._generate_vehicle_id()
        
        # Normalize registration number to uppercase
        if self.registration_number:
            self.registration_number = self.registration_number.upper()
        
        super().save(*args, **kwargs)
    
    def _generate_vehicle_id(self):
        """Generate vehicle ID in format VEH-XXXX (4-digit sequential)"""
        last_vehicle = Vehicle.objects.all().order_by('-vehicle_id').first()
        
        if last_vehicle and last_vehicle.vehicle_id:
            try:
                # Extract the numeric part from the last vehicle_id
                last_number = int(last_vehicle.vehicle_id.split('-')[1])
                new_number = last_number + 1
            except (IndexError, ValueError):
                new_number = 1
        else:
            new_number = 1
        
        return f"VEH-{new_number:04d}"
    
    def clean(self):
        """Validate model fields"""
        super().clean()
        
        # Validate registration number format (alphanumeric with spaces)
        if self.registration_number:
            import re
            if not re.match(r'^[A-Z0-9\s]+$', self.registration_number.upper()):
                raise ValidationError({
                    'registration_number': 'Registration number must contain only alphanumeric characters and spaces.'
                })
        
        # Validate vehicle type is not empty
        if not self.vehicle_type or not self.vehicle_type.strip():
            raise ValidationError({
                'vehicle_type': 'Vehicle type cannot be empty.'
            })
    
    def delete(self, *args, **kwargs):
        """Soft delete by setting is_active to False"""
        self.is_active = False
        self.save()
