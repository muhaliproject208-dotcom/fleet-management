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
        help_text="Calculated score for this section (points earned)"
    )
    max_possible_score = models.IntegerField(
        default=7,  # 7 questions * 1 point each
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
        Each question = 1 point. Returns tuple of (earned_score, max_score, section_percentage)
        """
        earned = 0
        max_score = 7  # 7 questions in health & fitness section
        
        # Adequate Rest - 1 point
        if self.adequate_rest is True:
            earned += 1
        
        # Alcohol Test - 1 point
        if self.alcohol_test_status == HealthCheckStatus.PASS:
            earned += 1
        
        # Fit for Duty - 1 point
        if self.fit_for_duty:
            earned += 1
        
        # No Health Impairment - 1 point
        if self.no_health_impairment:
            earned += 1
        
        # Fatigue Checklist - 1 point
        if self.fatigue_checklist_completed:
            earned += 1
        
        # Temperature Check - 1 point
        if self.temperature_check_status == HealthCheckStatus.PASS:
            earned += 1
        
        # Not on Medication - 1 point
        if not self.medication_status:
            earned += 1
        
        # Section percentage = (earned / max_score) * 100
        section_percentage = round((earned / max_score) * 100, 1) if max_score > 0 else 0
        return earned, max_score, section_percentage
    
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
        """Return detailed score breakdown for each item (1 point per question)"""
        from .scoring import TOTAL_PRECHECKLIST_QUESTIONS, get_section_risk_level, get_section_risk_display
        
        breakdown = []
        total_earned = 0
        max_score = 7  # 7 questions total
        
        # Check each item and build breakdown
        items = [
            {
                'item': 'Adequate Rest (8+ hours)',
                'earned': 1 if self.adequate_rest is True else 0,
                'status': 'Yes' if self.adequate_rest is True else ('No' if self.adequate_rest is False else 'N/A'),
                'critical': True
            },
            {
                'item': 'Alcohol/Drug Test',
                'earned': 1 if self.alcohol_test_status == HealthCheckStatus.PASS else 0,
                'status': self.get_alcohol_test_status_display(),
                'critical': True
            },
            {
                'item': 'Fit for Duty',
                'earned': 1 if self.fit_for_duty else 0,
                'status': 'Yes' if self.fit_for_duty else 'No',
                'critical': True
            },
            {
                'item': 'No Health Impairment',
                'earned': 1 if self.no_health_impairment else 0,
                'status': 'Yes' if self.no_health_impairment else 'No',
                'critical': True
            },
            {
                'item': 'Fatigue Checklist Completed',
                'earned': 1 if self.fatigue_checklist_completed else 0,
                'status': 'Yes' if self.fatigue_checklist_completed else 'No',
                'critical': False
            },
            {
                'item': 'Temperature Check',
                'earned': 1 if self.temperature_check_status == HealthCheckStatus.PASS else 0,
                'status': self.get_temperature_check_status_display(),
                'critical': False
            },
            {
                'item': 'Not on Medication',
                'earned': 1 if not self.medication_status else 0,
                'status': 'No medication' if not self.medication_status else 'On medication',
                'critical': False
            },
        ]
        
        for item in items:
            total_earned += item['earned']
            breakdown.append(item)
        
        # Calculate section and total percentages
        section_percentage = round((total_earned / max_score) * 100, 1) if max_score > 0 else 0
        total_percentage = round((total_earned / TOTAL_PRECHECKLIST_QUESTIONS) * 100, 2)
        risk_level = get_section_risk_level(section_percentage)
        
        return {
            'items': breakdown,
            'total': total_earned,
            'max': max_score,
            'section_percentage': section_percentage,
            'total_percentage': total_percentage,
            'risk_level': risk_level,
            'risk_display': get_section_risk_display(risk_level)
        }
    
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
