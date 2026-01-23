from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from .base import PreTripInspection


class RiskLevel(models.TextChoices):
    """Risk level choices"""
    LOW = 'low', 'Low'
    MEDIUM = 'medium', 'Medium'
    HIGH = 'high', 'High'


class PostTripReport(models.Model):
    """Post-trip reporting and assessment"""
    
    inspection = models.OneToOneField(
        PreTripInspection,
        on_delete=models.CASCADE,
        related_name='post_trip',
        help_text="Associated pre-trip inspection"
    )
    vehicle_fault_submitted = models.BooleanField(
        default=False,
        help_text="Vehicle fault report submitted"
    )
    fault_notes = models.TextField(
        blank=True,
        help_text="Details about vehicle faults"
    )
    final_inspection_signed = models.BooleanField(
        default=False,
        help_text="Final inspection signed off"
    )
    compliance_with_policy = models.BooleanField(
        default=True,
        help_text="Driver complied with company policy"
    )
    attitude_cooperation = models.BooleanField(
        default=True,
        help_text="Driver showed good attitude and cooperation"
    )
    incidents_recorded = models.BooleanField(
        default=False,
        help_text="Any incidents recorded during trip"
    )
    incident_notes = models.TextField(
        blank=True,
        help_text="Details about incidents"
    )
    total_trip_duration = models.CharField(
        max_length=50,
        blank=True,
        help_text="Total trip duration (e.g., 6 hrs 30 mins)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Post-Trip Report'
        verbose_name_plural = 'Post-Trip Reports'
    
    def __str__(self):
        return f"{self.inspection.inspection_id} - Post-Trip Report"
    
    def clean(self):
        """Validate model fields"""
        super().clean()
        
        # If vehicle fault submitted, notes should be provided
        if self.vehicle_fault_submitted and not self.fault_notes.strip():
            raise ValidationError({
                'fault_notes': 'Fault details required when vehicle fault is submitted.'
            })
        
        # If incidents recorded, notes should be provided
        if self.incidents_recorded and not self.incident_notes.strip():
            raise ValidationError({
                'incident_notes': 'Incident details required when incidents are recorded.'
            })


class RiskScoreSummary(models.Model):
    """Risk score calculation and 30-day rolling assessment"""
    
    inspection = models.OneToOneField(
        PreTripInspection,
        on_delete=models.CASCADE,
        related_name='risk_score',
        help_text="Associated pre-trip inspection"
    )
    total_points_this_trip = models.IntegerField(
        default=0,
        help_text="Total violation points for this trip"
    )
    risk_level = models.CharField(
        max_length=10,
        choices=RiskLevel.choices,
        default=RiskLevel.LOW,
        help_text="Risk level for this trip"
    )
    total_points_30_days = models.IntegerField(
        default=0,
        help_text="Total violation points in last 30 days"
    )
    risk_level_30_days = models.CharField(
        max_length=10,
        choices=RiskLevel.choices,
        default=RiskLevel.LOW,
        help_text="Risk level for last 30 days"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Risk Score Summary'
        verbose_name_plural = 'Risk Score Summaries'
    
    def __str__(self):
        return f"{self.inspection.inspection_id} - Risk: {self.risk_level} (30d: {self.risk_level_30_days})"
    
    def calculate_trip_points(self):
        """Calculate total violation points from trip behaviors"""
        total = 0
        for behavior in self.inspection.trip_behaviors.all():
            total += behavior.violation_points
        return total
    
    def calculate_30_day_points(self, driver):
        """Calculate total points from last 30 days for the driver"""
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        # Get all inspections for this driver in last 30 days
        recent_inspections = PreTripInspection.objects.filter(
            driver=driver,
            inspection_date__gte=thirty_days_ago.date()
        )
        
        total = 0
        for inspection in recent_inspections:
            # Sum all violation points from trip behaviors
            for behavior in inspection.trip_behaviors.all():
                total += behavior.violation_points
        
        return total
    
    def determine_risk_level(self, points):
        """
        Determine risk level based on points:
        0-3: low
        4-9: medium
        10+: high
        """
        if points >= 10:
            return RiskLevel.HIGH
        elif points >= 4:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def save(self, *args, **kwargs):
        """Auto-calculate all fields before saving"""
        # Calculate this trip's points
        self.total_points_this_trip = self.calculate_trip_points()
        self.risk_level = self.determine_risk_level(self.total_points_this_trip)
        
        # Calculate 30-day points
        if self.inspection and self.inspection.driver:
            self.total_points_30_days = self.calculate_30_day_points(self.inspection.driver)
            self.risk_level_30_days = self.determine_risk_level(self.total_points_30_days)
        
        super().save(*args, **kwargs)
