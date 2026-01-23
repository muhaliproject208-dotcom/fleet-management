from django.db import models
from django.core.exceptions import ValidationError
from .base import PreTripInspection


class MeasureType(models.TextChoices):
    """Corrective measure types"""
    SAFETY_TRAINING = 'safety_training', 'Safety Training'
    PERFORMANCE_REVIEW = 'performance_review', 'Performance Review'
    PROBATIONARY_PERIOD = 'probationary_period', 'Probationary Period'
    POLICY_ACKNOWLEDGMENT = 'policy_acknowledgment', 'Policy Acknowledgment'


class ActionType(models.TextChoices):
    """Enforcement action types"""
    VERBAL_WARNING = 'verbal_warning', 'Verbal Warning'
    WRITTEN_WARNING = 'written_warning', 'Written Warning'
    SUSPENSION = 'suspension', 'Suspension'
    FINAL_WARNING = 'final_warning', 'Final Warning'
    TERMINATION = 'termination', 'Termination'
    OTHER = 'other', 'Other'


class CorrectiveMeasure(models.Model):
    """Corrective measures based on inspection results"""
    
    inspection = models.ForeignKey(
        PreTripInspection,
        on_delete=models.CASCADE,
        related_name='corrective_measures',
        help_text="Associated pre-trip inspection"
    )
    measure_type = models.CharField(
        max_length=50,
        choices=MeasureType.choices,
        help_text="Type of corrective measure"
    )
    required = models.BooleanField(
        default=True,
        help_text="Whether this measure is required"
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        help_text="Due date for completion"
    )
    completed = models.BooleanField(
        default=False,
        help_text="Whether the measure has been completed"
    )
    completed_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when measure was completed"
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about the measure"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Corrective Measure'
        verbose_name_plural = 'Corrective Measures'
    
    def __str__(self):
        status = "✓ Completed" if self.completed else "Pending"
        return f"{self.inspection.inspection_id} - {self.measure_type}: {status}"
    
    def clean(self):
        """Validate model fields"""
        super().clean()
        
        # If completed, completed_date should be set
        if self.completed and not self.completed_date:
            raise ValidationError({
                'completed_date': 'Completion date required when measure is marked as completed.'
            })
        
        # If not completed, completed_date should not be set
        if not self.completed and self.completed_date:
            raise ValidationError({
                'completed': 'Cannot set completion date without marking as completed.'
            })


class EnforcementAction(models.Model):
    """Enforcement actions based on inspection results"""
    
    inspection = models.ForeignKey(
        PreTripInspection,
        on_delete=models.CASCADE,
        related_name='enforcement_actions',
        help_text="Associated pre-trip inspection"
    )
    action_type = models.CharField(
        max_length=50,
        choices=ActionType.choices,
        help_text="Type of enforcement action"
    )
    is_applied = models.BooleanField(
        default=False,
        help_text="Whether the action has been applied"
    )
    start_date = models.DateField(
        null=True,
        blank=True,
        help_text="Start date of the action"
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="End date (for suspension)"
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about the action"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Enforcement Action'
        verbose_name_plural = 'Enforcement Actions'
    
    def __str__(self):
        status = "Applied" if self.is_applied else "Pending"
        return f"{self.inspection.inspection_id} - {self.action_type}: {status}"
    
    def clean(self):
        """Validate model fields"""
        super().clean()
        
        # If applied, start_date should be set
        if self.is_applied and not self.start_date:
            raise ValidationError({
                'start_date': 'Start date required when action is applied.'
            })
        
        # For suspension, end_date should be after start_date
        if self.action_type == ActionType.SUSPENSION:
            if self.end_date and self.start_date:
                if self.end_date <= self.start_date:
                    raise ValidationError({
                        'end_date': 'End date must be after start date for suspension.'
                    })
