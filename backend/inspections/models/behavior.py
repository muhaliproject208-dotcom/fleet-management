from django.db import models
from django.core.exceptions import ValidationError
from .base import PreTripInspection


class BehaviorStatus(models.TextChoices):
    """Status choices for behavior monitoring"""
    COMPLIANT = 'compliant', 'Compliant'
    VIOLATION = 'violation', 'Violation'
    NONE = 'none', 'None'


class TripBehaviorMonitoring(models.Model):
    """Trip behavior monitoring and tracking"""
    
    class BehaviorItems(models.TextChoices):
        SPEED_SCHOOL_ZONE = 'speed_school_zone', 'Speed in School Zone'
        SPEED_MARKET_AREA = 'speed_market_area', 'Speed in Market Area'
        MAX_SPEED_OPEN_ROAD = 'max_speed_open_road', 'Max Speed on Open Road'
        RAILWAY_CROSSING = 'railway_crossing', 'Railway Crossing'
        TOLL_GATE = 'toll_gate', 'Toll Gate'
        HAZARDOUS_ZONE_SPEED = 'hazardous_zone_speed', 'Speed in Hazardous Zone'
        EXCESSIVE_DRIVING = 'excessive_driving', 'Excessive Driving'
        TRAFFIC_INFRACTIONS = 'traffic_infractions', 'Traffic Infractions'
        INCIDENTS = 'incidents', 'Incidents'
        SCHEDULED_BREAKS = 'scheduled_breaks', 'Scheduled Breaks'
        FATIGUE_REPORTING = 'fatigue_reporting', 'Fatigue Reporting'
        REST_STOPS_USAGE = 'rest_stops_usage', 'Rest Stops Usage'
    
    inspection = models.ForeignKey(
        PreTripInspection,
        on_delete=models.CASCADE,
        related_name='trip_behaviors',
        help_text="Associated pre-trip inspection"
    )
    behavior_item = models.CharField(
        max_length=100,
        choices=BehaviorItems.choices,
        help_text="Behavior item being monitored"
    )
    status = models.CharField(
        max_length=15,
        choices=BehaviorStatus.choices,
        help_text="Compliance status"
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about the behavior"
    )
    violation_points = models.IntegerField(
        default=0,
        help_text="Violation points (auto-calculated)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Trip Behavior Monitoring'
        verbose_name_plural = 'Trip Behavior Monitoring'
    
    def __str__(self):
        return f"{self.inspection.inspection_id} - {self.behavior_item}: {self.status}"
    
    def calculate_points(self):
        """Calculate violation points based on behavior_item and status"""
        if self.status != BehaviorStatus.VIOLATION:
            return 0
        
        # Points mapping for violations - must match frontend VIOLATION_POINTS
        points_map = {
            self.BehaviorItems.SPEED_SCHOOL_ZONE: 5,
            self.BehaviorItems.SPEED_MARKET_AREA: 5,
            self.BehaviorItems.MAX_SPEED_OPEN_ROAD: 3,
            self.BehaviorItems.RAILWAY_CROSSING: 10,
            self.BehaviorItems.TOLL_GATE: 2,
            self.BehaviorItems.HAZARDOUS_ZONE_SPEED: 10,
            self.BehaviorItems.EXCESSIVE_DRIVING: 8,
            self.BehaviorItems.TRAFFIC_INFRACTIONS: 10,
            self.BehaviorItems.INCIDENTS: 15,
            self.BehaviorItems.SCHEDULED_BREAKS: 3,
            self.BehaviorItems.FATIGUE_REPORTING: 5,
            self.BehaviorItems.REST_STOPS_USAGE: 2,
        }
        
        return points_map.get(self.behavior_item, 1)
    
    def save(self, *args, **kwargs):
        """Auto-calculate violation points before saving"""
        self.violation_points = self.calculate_points()
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validate model fields"""
        super().clean()
        if self.behavior_item not in self.BehaviorItems.values:
            raise ValidationError({
                'behavior_item': f'Invalid behavior item. Must be one of: {", ".join(self.BehaviorItems.values)}'
            })


class DrivingBehaviorCheck(models.Model):
    """Driving behavior checklist"""
    
    class BehaviorItems(models.TextChoices):
        OBEYS_TRAFFIC_RULES = 'obeys_traffic_rules', 'Obeys Traffic Rules'
        SAFE_SPEED_DISTANCE = 'safe_speed_distance', 'Safe Speed & Distance'
        AVOIDS_HARSH_MANEUVERS = 'avoids_harsh_maneuvers', 'Avoids Harsh Maneuvers'
        NO_PHONE_USE = 'no_phone_use', 'No Phone Use While Driving'
        HEADLIGHTS_VISIBILITY = 'headlights_visibility', 'Headlights & Visibility'
        LOAD_SECURITY = 'load_security', 'Load Security'
        ABNORMAL_SOUNDS_REPORTING = 'abnormal_sounds_reporting', 'Reports Abnormal Sounds'
        NO_OVERLOADING = 'no_overloading', 'No Overloading'
        BREAKDOWN_REPORTING = 'breakdown_reporting', 'Reports Breakdowns'
        EMERGENCY_PROCEDURES = 'emergency_procedures', 'Follows Emergency Procedures'
        CONTACT_CONTROL_CENTER = 'contact_control_center', 'Contacts Control Center'
    
    inspection = models.ForeignKey(
        PreTripInspection,
        on_delete=models.CASCADE,
        related_name='driving_behaviors',
        help_text="Associated pre-trip inspection"
    )
    behavior_item = models.CharField(
        max_length=100,
        choices=BehaviorItems.choices,
        help_text="Driving behavior being checked"
    )
    status = models.BooleanField(
        help_text="Whether the behavior is compliant (Yes/No)"
    )
    remarks = models.CharField(
        max_length=300,
        blank=True,
        help_text="Additional remarks"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Driving Behavior Check'
        verbose_name_plural = 'Driving Behavior Checks'
    
    def __str__(self):
        status_text = "✓" if self.status else "✗"
        return f"{self.inspection.inspection_id} - {self.behavior_item}: {status_text}"
    
    def clean(self):
        """Validate model fields"""
        super().clean()
        if self.behavior_item not in self.BehaviorItems.values:
            raise ValidationError({
                'behavior_item': f'Invalid behavior item. Must be one of: {", ".join(self.BehaviorItems.values)}'
            })
