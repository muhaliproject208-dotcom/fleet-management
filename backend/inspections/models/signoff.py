from django.db import models
from django.core.exceptions import ValidationError
from .base import PreTripInspection


class SignOffRole(models.TextChoices):
    """Sign-off role choices"""
    DRIVER = 'driver', 'Driver'
    SUPERVISOR = 'supervisor', 'Supervisor'
    MECHANIC = 'mechanic', 'Mechanic'


class InspectionSignOff(models.Model):
    """Inspection sign-offs for driver, supervisor, and mechanic"""
    
    inspection = models.ForeignKey(
        PreTripInspection,
        on_delete=models.CASCADE,
        related_name='sign_offs',
        help_text="Associated pre-trip inspection"
    )
    role = models.CharField(
        max_length=20,
        choices=SignOffRole.choices,
        help_text="Role of the person signing off"
    )
    signer_name = models.CharField(
        max_length=100,
        help_text="Name of the person signing off"
    )
    signed_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when signed"
    )
    
    class Meta:
        ordering = ['-signed_at']
        verbose_name = 'Inspection Sign-Off'
        verbose_name_plural = 'Inspection Sign-Offs'
        unique_together = ('inspection', 'role')
        constraints = [
            models.UniqueConstraint(
                fields=['inspection', 'role'],
                name='unique_inspection_role_signoff'
            )
        ]
    
    def __str__(self):
        return f"{self.inspection.inspection_id} - {self.role}: {self.signer_name}"
    
    def clean(self):
        """Validate model fields"""
        super().clean()
        
        # Validate role is valid
        if self.role not in SignOffRole.values:
            raise ValidationError({
                'role': f'Invalid role. Must be one of: {", ".join(SignOffRole.values)}'
            })
        
        # Validate signer name is provided
        if not self.signer_name or not self.signer_name.strip():
            raise ValidationError({
                'signer_name': 'Signer name is required.'
            })
