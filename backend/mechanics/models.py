from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings


class CertificationStatus(models.TextChoices):
    """Status choices for mechanic certification"""
    CERTIFIED = 'certified', 'Certified'
    NOT_CERTIFIED = 'not_certified', 'Not Certified'


class ServiceType(models.TextChoices):
    """Service type choices for vehicle maintenance"""
    FULL_SERVICE = 'full_service', 'Full Service'
    PARTIAL_SERVICE = 'partial_service', 'Partial Service'


class Mechanic(models.Model):
    """
    Mechanic model for fleet management system.
    Mechanics are non-login users who can be optionally assigned during inspections.
    """
    
    mechanic_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        db_index=True,
        help_text="Auto-generated mechanic ID in format MECH-XXXX"
    )
    full_name = models.CharField(max_length=100)
    specialization = models.CharField(
        max_length=100,
        help_text="Mechanic's specialization (e.g., General Mechanic, Diesel Specialist)"
    )
    phone_number = models.CharField(
        max_length=20,
        help_text="Phone number with country code (e.g., +260977654321)"
    )
    
    # Certification Status
    certification_status = models.CharField(
        max_length=20,
        choices=CertificationStatus.choices,
        default=CertificationStatus.NOT_CERTIFIED,
        help_text="Certification status of the mechanic"
    )
    
    # Last maintenance date (based on trip)
    last_vehicle_maintenance_date = models.DateField(
        null=True,
        blank=True,
        help_text="Last date the mechanic performed vehicle maintenance based on trip"
    )
    
    # Last servicing date (Manufacturing Mileage based)
    last_full_service_date = models.DateField(
        null=True,
        blank=True,
        help_text="Last date of full service based on manufacturing mileage"
    )
    last_partial_service_date = models.DateField(
        null=True,
        blank=True,
        help_text="Last date of partial service based on manufacturing mileage"
    )
    
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Indicates if the mechanic is currently active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_mechanics',
        help_text="User who created this mechanic record"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['mechanic_id'], name='mechanics_mechanic_id_idx'),
            models.Index(fields=['is_active'], name='mechanics_m_is_acti_03eba4_idx'),
        ]
        verbose_name = 'Mechanic'
        verbose_name_plural = 'Mechanics'
    
    def __str__(self):
        return f"{self.mechanic_id} - {self.full_name}"
    
    def save(self, *args, **kwargs):
        """Override save to auto-generate mechanic_id if not exists"""
        if not self.mechanic_id:
            self.mechanic_id = self._generate_mechanic_id()
        super().save(*args, **kwargs)
    
    def _generate_mechanic_id(self):
        """Generate mechanic ID in format MECH-XXXX (4-digit sequential)"""
        last_mechanic = Mechanic.objects.all().order_by('-mechanic_id').first()
        
        if last_mechanic and last_mechanic.mechanic_id:
            try:
                # Extract the numeric part from the last mechanic_id
                last_number = int(last_mechanic.mechanic_id.split('-')[1])
                new_number = last_number + 1
            except (IndexError, ValueError):
                new_number = 1
        else:
            new_number = 1
        
        return f"MECH-{new_number:04d}"
    
    def clean(self):
        """Validate model fields"""
        super().clean()
        
        # Validate phone number format
        if self.phone_number and not self.phone_number.startswith('+'):
            raise ValidationError({
                'phone_number': 'Phone number must start with + and country code.'
            })
        
        # Validate specialization is not empty
        if not self.specialization or not self.specialization.strip():
            raise ValidationError({
                'specialization': 'Specialization cannot be empty.'
            })
    
    def delete(self, *args, **kwargs):
        """Soft delete by setting is_active to False"""
        self.is_active = False
        self.save()
