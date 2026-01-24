from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings


class Driver(models.Model):
    """
    Driver model for fleet management system.
    Drivers are non-login users who will be selected via dropdowns during inspections.
    """
    
    driver_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        db_index=True,
        help_text="Auto-generated driver ID in format DRV-XXXX"
    )
    full_name = models.CharField(max_length=100)
    license_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Driver's license number (must be unique)"
    )
    phone_number = models.CharField(
        max_length=20,
        help_text="Phone number with country code (e.g., +260971234567)"
    )
    email = models.EmailField(blank=True, null=True)
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Indicates if the driver is currently active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_drivers',
        help_text="User who created this driver record"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['driver_id'], name='drivers_driver_id_idx'),
            models.Index(fields=['license_number'], name='drivers_license_idx'),
            models.Index(fields=['is_active'], name='drivers_dri_is_acti_7c5f39_idx'),
        ]
        verbose_name = 'Driver'
        verbose_name_plural = 'Drivers'
    
    def __str__(self):
        return f"{self.driver_id} - {self.full_name}"
    
    def save(self, *args, **kwargs):
        """Override save to auto-generate driver_id if not exists"""
        if not self.driver_id:
            self.driver_id = self._generate_driver_id()
        super().save(*args, **kwargs)
    
    def _generate_driver_id(self):
        """Generate driver ID in format DRV-XXXX (4-digit sequential)"""
        last_driver = Driver.objects.all().order_by('-driver_id').first()
        
        if last_driver and last_driver.driver_id:
            try:
                # Extract the numeric part from the last driver_id
                last_number = int(last_driver.driver_id.split('-')[1])
                new_number = last_number + 1
            except (IndexError, ValueError):
                new_number = 1
        else:
            new_number = 1
        
        return f"DRV-{new_number:04d}"
    
    def clean(self):
        """Validate model fields"""
        super().clean()
        
        # Validate phone number format
        if self.phone_number and not self.phone_number.startswith('+'):
            raise ValidationError({
                'phone_number': 'Phone number must start with + and country code.'
            })
    
    def delete(self, *args, **kwargs):
        """Soft delete by setting is_active to False"""
        self.is_active = False
        self.save()
    
    def get_average_risk_score(self):
        """Calculate average risk score across all completed trips"""
        from django.db.models import Avg
        from inspections.models import PreTripInspection, RiskScoreSummary
        
        # Get all approved inspections for this driver that have risk scores
        inspections = PreTripInspection.objects.filter(
            driver=self,
            status__in=['approved', 'post_trip_completed']
        ).values_list('id', flat=True)
        
        # Calculate average of total_points_this_trip
        avg = RiskScoreSummary.objects.filter(
            inspection_id__in=inspections
        ).aggregate(avg_score=Avg('total_points_this_trip'))['avg_score']
        
        return round(avg, 2) if avg is not None else None
    
    def get_risk_level(self):
        """Get risk level based on average risk score"""
        avg_score = self.get_average_risk_score()
        if avg_score is None:
            return 'N/A'
        elif avg_score <= 3:
            return 'Low'
        elif avg_score <= 9:
            return 'Medium'
        else:
            return 'High'
