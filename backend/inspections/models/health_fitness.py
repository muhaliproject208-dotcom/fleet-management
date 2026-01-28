from django.db import models
from django.core.exceptions import ValidationError
from .base import PreTripInspection


class HealthCheckStatus(models.TextChoices):
    """Status choices for health checks"""
    PASS = 'pass', 'Pass'
    FAIL = 'fail', 'Fail'


# Scoring weights for health & fitness items (higher = more critical)
HEALTH_FITNESS_SCORES = {
    'adequate_rest': 100,  # Critical - driver must have rested 8hrs+
    'alcohol_test': 100,  # Critical - zero tolerance
    'fit_for_duty': 90,  # Critical - overall fitness
    'no_health_impairment': 80,  # High importance
    'fatigue_checklist': 70,  # High importance
    'temperature_check': 50,  # Medium importance
    'medication_status': 40,  # Medium importance (informational)
}


class HealthFitnessCheck(models.Model):
    """
    Health and Fitness Check model for pre-trip inspections.
    OneToOne relationship with PreTripInspection.
    Includes scoring based on importance/intensity of each check.
    """
    
    inspection = models.OneToOneField(
        PreTripInspection,
        on_delete=models.CASCADE,
        related_name='health_fitness',
        help_text="Associated pre-trip inspection"
    )
    
    # Fatigue / Rest Clearance - CRITICAL CHECK
    adequate_rest = models.BooleanField(
        null=True,
        blank=True,
        help_text="Has the driver rested for 8 hours or more?"
    )
    rest_clearance_status = models.CharField(
        max_length=20,
        choices=[
            ('cleared', 'Cleared for Travel'),
            ('not_cleared', 'Not Cleared - Insufficient Rest'),
        ],
        blank=True,
        help_text="Travel clearance based on rest status"
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
    
    # Scoring fields
    section_score = models.IntegerField(
        default=0,
        help_text="Calculated score for this section (0-100)"
    )
    max_possible_score = models.IntegerField(
        default=530,  # Sum of all HEALTH_FITNESS_SCORES values
        help_text="Maximum possible score for this section"
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
    
    def calculate_score(self):
        """
        Calculate the health & fitness score based on check results.
        Returns tuple of (earned_score, max_score, percentage)
        """
        earned = 0
        max_score = sum(HEALTH_FITNESS_SCORES.values())
        
        # Adequate Rest - Critical (100 points)
        if self.adequate_rest is True:
            earned += HEALTH_FITNESS_SCORES['adequate_rest']
        
        # Alcohol Test (100 points)
        if self.alcohol_test_status == HealthCheckStatus.PASS:
            earned += HEALTH_FITNESS_SCORES['alcohol_test']
        
        # Fit for Duty (90 points)
        if self.fit_for_duty:
            earned += HEALTH_FITNESS_SCORES['fit_for_duty']
        
        # No Health Impairment (80 points)
        if self.no_health_impairment:
            earned += HEALTH_FITNESS_SCORES['no_health_impairment']
        
        # Fatigue Checklist (70 points)
        if self.fatigue_checklist_completed:
            earned += HEALTH_FITNESS_SCORES['fatigue_checklist']
        
        # Temperature Check (50 points)
        if self.temperature_check_status == HealthCheckStatus.PASS:
            earned += HEALTH_FITNESS_SCORES['temperature_check']
        
        # Medication Status - Give points if NOT on medication (40 points)
        if not self.medication_status:
            earned += HEALTH_FITNESS_SCORES['medication_status']
        
        percentage = round((earned / max_score) * 100, 1) if max_score > 0 else 0
        return earned, max_score, percentage
    
    def save(self, *args, **kwargs):
        """Override save to calculate score and set clearance status"""
        # Set rest clearance status based on adequate_rest
        if self.adequate_rest is True:
            self.rest_clearance_status = 'cleared'
        elif self.adequate_rest is False:
            self.rest_clearance_status = 'not_cleared'
        
        # Calculate and store score
        earned, max_score, _ = self.calculate_score()
        self.section_score = earned
        self.max_possible_score = max_score
        
        super().save(*args, **kwargs)
    
    def is_passed(self):
        """
        Return True if all critical checks pass.
        Critical checks: adequate rest, alcohol test pass, fit for duty, no health impairment
        """
        return (
            self.adequate_rest is True and
            self.alcohol_test_status == HealthCheckStatus.PASS and
            self.fit_for_duty and
            self.no_health_impairment
        )
    
    def is_travel_cleared(self):
        """
        Return True if driver is cleared for travel.
        Requires adequate rest (8+ hours) among other checks.
        """
        if self.adequate_rest is not True:
            return False
        return self.is_passed()
    
    def get_clearance_message(self):
        """Return appropriate message based on clearance status"""
        if self.adequate_rest is False:
            return "⚠️ DRIVER NOT CLEARED FOR TRAVEL: Driver has not rested for 8 hours or more. Travel is not permitted."
        elif not self.is_passed():
            return "⚠️ DRIVER NOT CLEARED: One or more critical health checks failed."
        return "✓ Driver cleared for travel."
    
    def get_score_breakdown(self):
        """Return detailed score breakdown for each item"""
        breakdown = []
        
        breakdown.append({
            'item': 'Adequate Rest (8+ hours)',
            'weight': HEALTH_FITNESS_SCORES['adequate_rest'],
            'earned': HEALTH_FITNESS_SCORES['adequate_rest'] if self.adequate_rest is True else 0,
            'status': 'Yes' if self.adequate_rest is True else ('No' if self.adequate_rest is False else 'N/A'),
            'critical': True
        })
        
        breakdown.append({
            'item': 'Alcohol/Drug Test',
            'weight': HEALTH_FITNESS_SCORES['alcohol_test'],
            'earned': HEALTH_FITNESS_SCORES['alcohol_test'] if self.alcohol_test_status == HealthCheckStatus.PASS else 0,
            'status': self.get_alcohol_test_status_display(),
            'critical': True
        })
        
        breakdown.append({
            'item': 'Fit for Duty',
            'weight': HEALTH_FITNESS_SCORES['fit_for_duty'],
            'earned': HEALTH_FITNESS_SCORES['fit_for_duty'] if self.fit_for_duty else 0,
            'status': 'Yes' if self.fit_for_duty else 'No',
            'critical': True
        })
        
        breakdown.append({
            'item': 'No Health Impairment',
            'weight': HEALTH_FITNESS_SCORES['no_health_impairment'],
            'earned': HEALTH_FITNESS_SCORES['no_health_impairment'] if self.no_health_impairment else 0,
            'status': 'Yes' if self.no_health_impairment else 'No',
            'critical': True
        })
        
        breakdown.append({
            'item': 'Fatigue Checklist Completed',
            'weight': HEALTH_FITNESS_SCORES['fatigue_checklist'],
            'earned': HEALTH_FITNESS_SCORES['fatigue_checklist'] if self.fatigue_checklist_completed else 0,
            'status': 'Yes' if self.fatigue_checklist_completed else 'No',
            'critical': False
        })
        
        breakdown.append({
            'item': 'Temperature Check',
            'weight': HEALTH_FITNESS_SCORES['temperature_check'],
            'earned': HEALTH_FITNESS_SCORES['temperature_check'] if self.temperature_check_status == HealthCheckStatus.PASS else 0,
            'status': self.get_temperature_check_status_display(),
            'critical': False
        })
        
        breakdown.append({
            'item': 'Not on Medication',
            'weight': HEALTH_FITNESS_SCORES['medication_status'],
            'earned': HEALTH_FITNESS_SCORES['medication_status'] if not self.medication_status else 0,
            'status': 'No medication' if not self.medication_status else 'On medication',
            'critical': False
        })
        
        return breakdown
    
    def clean(self):
        """Validate model fields"""
        super().clean()
        
        # Critical: Driver must have adequate rest to proceed
        if self.adequate_rest is False:
            raise ValidationError({
                'adequate_rest': 'Driver has not rested for 8 hours or more. Driver should NOT travel.'
            })
        
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
