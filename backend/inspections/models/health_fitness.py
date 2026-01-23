from django.db import models
from django.core.exceptions import ValidationError
from .base import PreTripInspection


class HealthCheckStatus(models.TextChoices):
    """Status choices for health checks"""
    PASS = 'pass', 'Pass'
    FAIL = 'fail', 'Fail'


class HealthFitnessCheck(models.Model):
    """
    Health and Fitness Check model for pre-trip inspections.
    OneToOne relationship with PreTripInspection.
    """
    
    inspection = models.OneToOneField(
        PreTripInspection,
        on_delete=models.CASCADE,
        related_name='health_fitness',
        help_text="Associated pre-trip inspection"
    )
    alcohol_test_status = models.CharField(
        max_length=10,
        choices=HealthCheckStatus.choices,
        help_text="Result of alcohol test"
    )
    alcohol_test_remarks = models.TextField(
        blank=True,
        help_text="Remarks for alcohol test"
    )
    temperature_check_status = models.CharField(
        max_length=10,
        choices=HealthCheckStatus.choices,
        help_text="Result of temperature check"
    )
    temperature_value = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Temperature value in Celsius (e.g., 36.7)"
    )
    fit_for_duty = models.BooleanField(
        default=True,
        help_text="Whether driver is fit for duty"
    )
    medication_status = models.BooleanField(
        default=False,
        help_text="Whether driver is on medication"
    )
    medication_remarks = models.CharField(
        max_length=200,
        blank=True,
        help_text="Details about medication if applicable"
    )
    no_health_impairment = models.BooleanField(
        default=True,
        help_text="Driver has no health impairments"
    )
    fatigue_checklist_completed = models.BooleanField(
        default=False,
        help_text="Whether fatigue checklist was completed"
    )
    fatigue_remarks = models.CharField(
        max_length=200,
        blank=True,
        help_text="Remarks about fatigue check"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Health & Fitness Check'
        verbose_name_plural = 'Health & Fitness Checks'
    
    def __str__(self):
        status = "Passed" if self.is_passed() else "Failed"
        return f"{self.inspection.inspection_id} - Health Check: {status}"
    
    def is_passed(self):
        """
        Return True if all critical checks pass.
        Critical checks: alcohol test pass, fit for duty, no health impairment
        """
        return (
            self.alcohol_test_status == HealthCheckStatus.PASS and
            self.fit_for_duty and
            self.no_health_impairment
        )
    
    def clean(self):
        """Validate model fields"""
        super().clean()
        
        # Validate alcohol test failure requires remarks
        if self.alcohol_test_status == HealthCheckStatus.FAIL:
            if not self.alcohol_test_remarks or not self.alcohol_test_remarks.strip():
                raise ValidationError({
                    'alcohol_test_remarks': 'Remarks required when alcohol test fails.'
                })
        
        # Validate temperature range
        if self.temperature_value is not None:
            if not (35.0 <= self.temperature_value <= 39.0):
                raise ValidationError({
                    'temperature_value': 'Temperature value should be between 35.0°C and 39.0°C.'
                })
        
        # Validate medication status requires remarks
        if self.medication_status:
            if not self.medication_remarks or not self.medication_remarks.strip():
                raise ValidationError({
                    'medication_remarks': 'Medication details required when driver is on medication.'
                })
        
        # Validate fit for duty
        if not self.fit_for_duty:
            raise ValidationError({
                'fit_for_duty': 'Driver not fit for duty. Inspection cannot proceed.'
            })
