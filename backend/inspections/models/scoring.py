"""
Pre-Trip Score Summary Model
Calculates and stores overall pre-trip checklist scores.
"""

from django.db import models
from .base import PreTripInspection
from .health_fitness import HEALTH_FITNESS_SCORES


# Scoring weights for documentation items
DOCUMENTATION_SCORES = {
    'certificate_of_fitness': 50,
    'road_tax_valid': 40,
    'insurance_valid': 50,
    'trip_authorization_signed': 40,
    'logbook_present': 30,
    'driver_handbook_present': 20,
    'permits_valid': 40,
    'ppe_available': 30,
    'route_familiarity': 25,
    'emergency_procedures_known': 35,
    'gps_activated': 25,
    'safety_briefing_provided': 30,
    'rtsa_clearance': 40,
}

# Scoring weights for vehicle checks (per item)
VEHICLE_CHECK_SCORES = {
    # Exterior checks
    'tires': 50,  # Critical
    'lights': 45,  # Critical
    'mirrors': 30,
    'windshield': 25,
    'body_condition': 20,
    'loose_parts': 30,
    'leaks': 40,
    
    # Engine checks
    'engine_oil': 50,  # Critical
    'coolant': 35,
    'brake_fluid': 50,  # Critical
    'transmission_fluid': 30,
    'power_steering_fluid': 25,
    'battery': 30,
    
    # Interior checks
    'dashboard_indicators': 25,
    'seatbelts': 50,  # Critical
    'horn': 20,
    'fire_extinguisher': 35,
    'first_aid_kit': 30,
    'safety_triangles': 25,
    
    # Functional checks
    'brakes': 60,  # Very Critical
    'steering': 55,  # Very Critical
    'suspension': 35,
    'hvac': 15,
    
    # Safety equipment
    'reflective_triangles': 25,
    'wheel_chocks': 20,
    'spare_tyre': 30,
    'torch': 15,
    'emergency_contacts': 20,
    'gps_tracker': 25,
}


class ScoreLevel(models.TextChoices):
    """Score level choices"""
    EXCELLENT = 'excellent', 'Excellent (90-100%)'
    GOOD = 'good', 'Good (75-89%)'
    FAIR = 'fair', 'Fair (60-74%)'
    POOR = 'poor', 'Poor (Below 60%)'


class PreTripScoreSummary(models.Model):
    """
    Pre-Trip Score Summary - aggregates all section scores.
    Provides an overall assessment of the pre-trip inspection.
    """
    
    inspection = models.OneToOneField(
        PreTripInspection,
        on_delete=models.CASCADE,
        related_name='pre_trip_score',
        help_text="Associated pre-trip inspection"
    )
    
    # Section scores
    health_fitness_score = models.IntegerField(
        default=0,
        help_text="Health & Fitness section score"
    )
    health_fitness_max = models.IntegerField(
        default=530,
        help_text="Max possible Health & Fitness score"
    )
    
    documentation_score = models.IntegerField(
        default=0,
        help_text="Documentation section score"
    )
    documentation_max = models.IntegerField(
        default=455,
        help_text="Max possible Documentation score"
    )
    
    vehicle_exterior_score = models.IntegerField(
        default=0,
        help_text="Vehicle Exterior checks score"
    )
    vehicle_exterior_max = models.IntegerField(
        default=240,
        help_text="Max possible Exterior score"
    )
    
    engine_fluid_score = models.IntegerField(
        default=0,
        help_text="Engine & Fluid checks score"
    )
    engine_fluid_max = models.IntegerField(
        default=220,
        help_text="Max possible Engine/Fluid score"
    )
    
    interior_cabin_score = models.IntegerField(
        default=0,
        help_text="Interior & Cabin checks score"
    )
    interior_cabin_max = models.IntegerField(
        default=185,
        help_text="Max possible Interior score"
    )
    
    functional_score = models.IntegerField(
        default=0,
        help_text="Functional checks score"
    )
    functional_max = models.IntegerField(
        default=165,
        help_text="Max possible Functional score"
    )
    
    safety_equipment_score = models.IntegerField(
        default=0,
        help_text="Safety Equipment checks score"
    )
    safety_equipment_max = models.IntegerField(
        default=135,
        help_text="Max possible Safety score"
    )
    
    # Overall scores
    total_score = models.IntegerField(
        default=0,
        help_text="Total pre-trip checklist score"
    )
    max_possible_score = models.IntegerField(
        default=1930,
        help_text="Maximum possible total score"
    )
    score_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Overall score percentage"
    )
    score_level = models.CharField(
        max_length=15,
        choices=ScoreLevel.choices,
        default=ScoreLevel.POOR,
        help_text="Overall score level"
    )
    
    # Critical failures tracking
    critical_failures = models.JSONField(
        default=list,
        blank=True,
        help_text="List of critical check failures"
    )
    has_critical_failures = models.BooleanField(
        default=False,
        help_text="Whether any critical checks failed"
    )
    
    # Travel clearance
    is_cleared_for_travel = models.BooleanField(
        default=False,
        help_text="Overall travel clearance status"
    )
    clearance_notes = models.TextField(
        blank=True,
        help_text="Notes about clearance decision"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Pre-Trip Score Summary'
        verbose_name_plural = 'Pre-Trip Score Summaries'
    
    def __str__(self):
        return f"{self.inspection.inspection_id} - Score: {self.score_percentage}% ({self.score_level})"
    
    def calculate_health_fitness_score(self):
        """Calculate health & fitness section score"""
        try:
            health_check = self.inspection.health_fitness
            earned, max_score, _ = health_check.calculate_score()
            return earned, max_score
        except:
            return 0, sum(HEALTH_FITNESS_SCORES.values())
    
    def calculate_documentation_score(self):
        """Calculate documentation section score"""
        try:
            doc = self.inspection.documentation
            earned = 0
            
            if doc.certificate_of_fitness == 'valid':
                earned += DOCUMENTATION_SCORES['certificate_of_fitness']
            if doc.road_tax_valid:
                earned += DOCUMENTATION_SCORES['road_tax_valid']
            if doc.insurance_valid:
                earned += DOCUMENTATION_SCORES['insurance_valid']
            if doc.trip_authorization_signed:
                earned += DOCUMENTATION_SCORES['trip_authorization_signed']
            if doc.logbook_present:
                earned += DOCUMENTATION_SCORES['logbook_present']
            if doc.driver_handbook_present:
                earned += DOCUMENTATION_SCORES['driver_handbook_present']
            if doc.permits_valid:
                earned += DOCUMENTATION_SCORES['permits_valid']
            if doc.ppe_available:
                earned += DOCUMENTATION_SCORES['ppe_available']
            if doc.route_familiarity:
                earned += DOCUMENTATION_SCORES['route_familiarity']
            if doc.emergency_procedures_known:
                earned += DOCUMENTATION_SCORES['emergency_procedures_known']
            if doc.gps_activated:
                earned += DOCUMENTATION_SCORES['gps_activated']
            if doc.safety_briefing_provided:
                earned += DOCUMENTATION_SCORES['safety_briefing_provided']
            if doc.rtsa_clearance:
                earned += DOCUMENTATION_SCORES['rtsa_clearance']
            
            return earned, sum(DOCUMENTATION_SCORES.values())
        except:
            return 0, sum(DOCUMENTATION_SCORES.values())
    
    def calculate_vehicle_check_score(self, check_type):
        """Calculate score for a vehicle check section"""
        check_mapping = {
            'exterior': ('exterior_checks', ['tires', 'lights', 'mirrors', 'windshield', 'body_condition', 'loose_parts', 'leaks']),
            'engine': ('engine_fluid_checks', ['engine_oil', 'coolant', 'brake_fluid', 'transmission_fluid', 'power_steering_fluid', 'battery']),
            'interior': ('interior_cabin_checks', ['dashboard_indicators', 'seatbelts', 'horn', 'fire_extinguisher', 'first_aid_kit', 'safety_triangles']),
            'functional': ('functional_checks', ['brakes', 'steering', 'suspension', 'hvac']),
            'safety': ('safety_equipment_checks', ['fire_extinguisher', 'first_aid_kit', 'reflective_triangles', 'wheel_chocks', 'spare_tyre', 'torch', 'emergency_contacts', 'gps_tracker']),
        }
        
        try:
            related_name, items = check_mapping[check_type]
            checks = getattr(self.inspection, related_name).all()
            
            earned = 0
            max_score = sum(VEHICLE_CHECK_SCORES.get(item, 25) for item in items)
            
            for check in checks:
                if check.status == 'pass':
                    item_score = VEHICLE_CHECK_SCORES.get(check.check_item, 25)
                    earned += item_score
            
            return earned, max_score
        except:
            return 0, 100
    
    def check_critical_failures(self):
        """Check for any critical failures"""
        failures = []
        
        # Health & Fitness critical checks
        try:
            health = self.inspection.health_fitness
            if health.adequate_rest is False:
                failures.append('Inadequate Rest (less than 8 hours)')
            if health.alcohol_test_status == 'fail':
                failures.append('Failed Alcohol/Drug Test')
            if not health.fit_for_duty:
                failures.append('Driver Not Fit for Duty')
            if not health.no_health_impairment:
                failures.append('Health Impairment Present')
        except:
            pass
        
        # Critical vehicle checks
        critical_items = ['tires', 'lights', 'brakes', 'steering', 'seatbelts', 'engine_oil', 'brake_fluid']
        
        for check_type in ['exterior_checks', 'engine_fluid_checks', 'interior_cabin_checks', 'functional_checks']:
            try:
                checks = getattr(self.inspection, check_type).all()
                for check in checks:
                    if check.check_item in critical_items and check.status == 'fail':
                        failures.append(f'Failed Critical Check: {check.check_item.replace("_", " ").title()}')
            except:
                pass
        
        return failures
    
    def determine_score_level(self, percentage):
        """Determine score level based on percentage"""
        if percentage >= 90:
            return ScoreLevel.EXCELLENT
        elif percentage >= 75:
            return ScoreLevel.GOOD
        elif percentage >= 60:
            return ScoreLevel.FAIR
        else:
            return ScoreLevel.POOR
    
    def calculate_all_scores(self):
        """Calculate all section scores and totals"""
        # Health & Fitness
        self.health_fitness_score, self.health_fitness_max = self.calculate_health_fitness_score()
        
        # Documentation
        self.documentation_score, self.documentation_max = self.calculate_documentation_score()
        
        # Vehicle checks
        self.vehicle_exterior_score, self.vehicle_exterior_max = self.calculate_vehicle_check_score('exterior')
        self.engine_fluid_score, self.engine_fluid_max = self.calculate_vehicle_check_score('engine')
        self.interior_cabin_score, self.interior_cabin_max = self.calculate_vehicle_check_score('interior')
        self.functional_score, self.functional_max = self.calculate_vehicle_check_score('functional')
        self.safety_equipment_score, self.safety_equipment_max = self.calculate_vehicle_check_score('safety')
        
        # Totals
        self.total_score = (
            self.health_fitness_score +
            self.documentation_score +
            self.vehicle_exterior_score +
            self.engine_fluid_score +
            self.interior_cabin_score +
            self.functional_score +
            self.safety_equipment_score
        )
        
        self.max_possible_score = (
            self.health_fitness_max +
            self.documentation_max +
            self.vehicle_exterior_max +
            self.engine_fluid_max +
            self.interior_cabin_max +
            self.functional_max +
            self.safety_equipment_max
        )
        
        # Percentage and level
        if self.max_possible_score > 0:
            self.score_percentage = round((self.total_score / self.max_possible_score) * 100, 2)
        else:
            self.score_percentage = 0
        
        self.score_level = self.determine_score_level(float(self.score_percentage))
        
        # Critical failures
        self.critical_failures = self.check_critical_failures()
        self.has_critical_failures = len(self.critical_failures) > 0
        
        # Travel clearance
        self.is_cleared_for_travel = not self.has_critical_failures and self.score_percentage >= 60
        
        if self.has_critical_failures:
            self.clearance_notes = f"Travel not cleared due to critical failures: {', '.join(self.critical_failures)}"
        elif self.score_percentage < 60:
            self.clearance_notes = f"Travel not cleared due to low overall score ({self.score_percentage}%)"
        else:
            self.clearance_notes = "All checks passed. Vehicle and driver cleared for travel."
    
    def save(self, *args, **kwargs):
        """Calculate all scores before saving"""
        self.calculate_all_scores()
        super().save(*args, **kwargs)
    
    def get_section_summary(self):
        """Return a summary of all section scores"""
        return [
            {
                'section': 'Health & Fitness',
                'score': self.health_fitness_score,
                'max': self.health_fitness_max,
                'percentage': round((self.health_fitness_score / self.health_fitness_max * 100), 1) if self.health_fitness_max > 0 else 0
            },
            {
                'section': 'Documentation & Compliance',
                'score': self.documentation_score,
                'max': self.documentation_max,
                'percentage': round((self.documentation_score / self.documentation_max * 100), 1) if self.documentation_max > 0 else 0
            },
            {
                'section': 'Vehicle Exterior',
                'score': self.vehicle_exterior_score,
                'max': self.vehicle_exterior_max,
                'percentage': round((self.vehicle_exterior_score / self.vehicle_exterior_max * 100), 1) if self.vehicle_exterior_max > 0 else 0
            },
            {
                'section': 'Engine & Fluids',
                'score': self.engine_fluid_score,
                'max': self.engine_fluid_max,
                'percentage': round((self.engine_fluid_score / self.engine_fluid_max * 100), 1) if self.engine_fluid_max > 0 else 0
            },
            {
                'section': 'Interior & Cabin',
                'score': self.interior_cabin_score,
                'max': self.interior_cabin_max,
                'percentage': round((self.interior_cabin_score / self.interior_cabin_max * 100), 1) if self.interior_cabin_max > 0 else 0
            },
            {
                'section': 'Functional Checks',
                'score': self.functional_score,
                'max': self.functional_max,
                'percentage': round((self.functional_score / self.functional_max * 100), 1) if self.functional_max > 0 else 0
            },
            {
                'section': 'Safety Equipment',
                'score': self.safety_equipment_score,
                'max': self.safety_equipment_max,
                'percentage': round((self.safety_equipment_score / self.safety_equipment_max * 100), 1) if self.safety_equipment_max > 0 else 0
            },
        ]
