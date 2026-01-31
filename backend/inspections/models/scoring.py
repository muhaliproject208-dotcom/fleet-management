"""
Pre-Trip Score Summary Model
Calculates and stores overall pre-trip checklist scores.
Each question in the pre-checklist carries a score of 1.5 points.
"""

from django.db import models
from decimal import Decimal
from .base import PreTripInspection
from .health_fitness import HEALTH_FITNESS_SCORES


# Standard score per question in pre-trip checklist
SCORE_PER_QUESTION = Decimal('1.5')


# Scoring weights for documentation items (legacy - kept for reference)
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
    # New fields
    'certificate_of_fitness_valid': 50,
    'time_briefing_conducted': 30,
    'emergency_contact_employer': 25,
    'emergency_contact_government': 25,
}

# Scoring weights for vehicle checks (per item) - legacy
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
    
    # Brakes and Steering checks (new dedicated section)
    'brakes_condition': 60,
    'brake_pads': 50,
    'brake_fluid_level': 50,
    'brake_lines': 45,
    'handbrake': 40,
    'steering_wheel': 55,
    'steering_response': 55,
    'power_steering': 40,
    'steering_fluid': 35,
}


class RiskStatus(models.TextChoices):
    """Risk status choices based on score"""
    LOW_RISK = 'low_risk', 'Low Risk'
    MODERATE_RISK = 'moderate_risk', 'Moderate Risk'
    HIGH_RISK = 'high_risk', 'High Risk'
    CRITICAL_RISK = 'critical_risk', 'Critical Risk'


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
    Each question carries 1.5 points for the new scoring system.
    """
    
    inspection = models.OneToOneField(
        PreTripInspection,
        on_delete=models.CASCADE,
        related_name='pre_trip_score',
        help_text="Associated pre-trip inspection"
    )
    
    # Section scores (using Decimal for 1.5 point system)
    health_fitness_score = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Health & Fitness section score"
    )
    health_fitness_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Max possible Health & Fitness score"
    )
    health_fitness_questions = models.IntegerField(
        default=0,
        help_text="Number of questions in Health & Fitness section"
    )
    
    documentation_score = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Documentation section score"
    )
    documentation_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Max possible Documentation score"
    )
    documentation_questions = models.IntegerField(
        default=0,
        help_text="Number of questions in Documentation section"
    )
    
    vehicle_exterior_score = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Vehicle Exterior checks score"
    )
    vehicle_exterior_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Max possible Exterior score"
    )
    vehicle_exterior_questions = models.IntegerField(
        default=0,
        help_text="Number of questions in Exterior section"
    )
    
    engine_fluid_score = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Engine & Fluid checks score"
    )
    engine_fluid_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Max possible Engine/Fluid score"
    )
    engine_fluid_questions = models.IntegerField(
        default=0,
        help_text="Number of questions in Engine/Fluid section"
    )
    
    interior_cabin_score = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Interior & Cabin checks score"
    )
    interior_cabin_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Max possible Interior score"
    )
    interior_cabin_questions = models.IntegerField(
        default=0,
        help_text="Number of questions in Interior section"
    )
    
    functional_score = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Functional checks score"
    )
    functional_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Max possible Functional score"
    )
    functional_questions = models.IntegerField(
        default=0,
        help_text="Number of questions in Functional section"
    )
    
    safety_equipment_score = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Safety Equipment checks score"
    )
    safety_equipment_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Max possible Safety score"
    )
    safety_equipment_questions = models.IntegerField(
        default=0,
        help_text="Number of questions in Safety Equipment section"
    )
    
    # Brakes and Steering section (new)
    brakes_steering_score = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Brakes & Steering checks score"
    )
    brakes_steering_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Max possible Brakes & Steering score"
    )
    brakes_steering_questions = models.IntegerField(
        default=0,
        help_text="Number of questions in Brakes & Steering section"
    )
    
    # Overall scores
    total_score = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Total pre-trip checklist score"
    )
    max_possible_score = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Maximum possible total score"
    )
    total_questions = models.IntegerField(
        default=0,
        help_text="Total number of questions across all sections"
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
    
    # Risk Status (new field)
    risk_status = models.CharField(
        max_length=20,
        choices=RiskStatus.choices,
        default=RiskStatus.HIGH_RISK,
        help_text="Risk status based on overall score"
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
        return f"{self.inspection.inspection_id} - Score: {self.score_percentage}% ({self.score_level}) - {self.risk_status}"
    
    def determine_risk_status(self, percentage):
        """Determine risk status based on percentage"""
        if percentage >= 90:
            return RiskStatus.LOW_RISK
        elif percentage >= 75:
            return RiskStatus.MODERATE_RISK
        elif percentage >= 60:
            return RiskStatus.HIGH_RISK
        else:
            return RiskStatus.CRITICAL_RISK
    
    def calculate_health_fitness_score_new(self):
        """
        Calculate health & fitness section score using 1.5 points per question.
        Returns tuple of (earned_score, max_score, num_questions)
        """
        try:
            health_check = self.inspection.health_fitness
            # Count questions answered
            questions = 0
            passed = 0
            
            # Adequate Rest
            if health_check.adequate_rest is not None:
                questions += 1
                if health_check.adequate_rest:
                    passed += 1
            
            # Alcohol Test
            if health_check.alcohol_test_status:
                questions += 1
                if health_check.alcohol_test_status == 'pass':
                    passed += 1
            
            # Temperature Check
            if health_check.temperature_check_status:
                questions += 1
                if health_check.temperature_check_status == 'pass':
                    passed += 1
            
            # Fit for Duty
            questions += 1
            if health_check.fit_for_duty:
                passed += 1
            
            # No Health Impairment
            questions += 1
            if health_check.no_health_impairment:
                passed += 1
            
            # Fatigue Checklist
            questions += 1
            if health_check.fatigue_checklist_completed:
                passed += 1
            
            # Medication Status (informational, still a question)
            questions += 1
            if not health_check.medication_status:  # No medication is positive
                passed += 1
            
            earned = Decimal(passed) * SCORE_PER_QUESTION
            max_score = Decimal(questions) * SCORE_PER_QUESTION
            
            return earned, max_score, questions
        except Exception:
            return Decimal('0'), Decimal('10.5'), 7  # 7 questions * 1.5
    
    def calculate_documentation_score_new(self):
        """
        Calculate documentation section score using 1.5 points per question.
        Returns tuple of (earned_score, max_score, num_questions)
        """
        try:
            doc = self.inspection.documentation
            questions = 0
            passed = 0
            
            # Certificate of Fitness Valid
            questions += 1
            if doc.certificate_of_fitness_valid == 'yes' or doc.certificate_of_fitness == 'valid':
                passed += 1
            
            # Road Tax Valid
            questions += 1
            if doc.road_tax_valid:
                passed += 1
            
            # Insurance Valid
            questions += 1
            if doc.insurance_valid:
                passed += 1
            
            # Trip Authorization Signed
            questions += 1
            if doc.trip_authorization_signed:
                passed += 1
            
            # Logbook Present
            questions += 1
            if doc.logbook_present:
                passed += 1
            
            # Driver Handbook Present
            questions += 1
            if doc.driver_handbook_present:
                passed += 1
            
            # Permits Valid
            questions += 1
            if doc.permits_valid:
                passed += 1
            
            # PPE Available
            questions += 1
            if doc.ppe_available:
                passed += 1
            
            # Route Familiarity
            questions += 1
            if doc.route_familiarity:
                passed += 1
            
            # Emergency Procedures Known
            questions += 1
            if doc.emergency_procedures_known:
                passed += 1
            
            # GPS Activated
            questions += 1
            if doc.gps_activated:
                passed += 1
            
            # Safety Briefing Provided
            questions += 1
            safety_ok = doc.safety_briefing_provided == 'yes' if isinstance(doc.safety_briefing_provided, str) else doc.safety_briefing_provided
            if safety_ok:
                passed += 1
            
            # RTSA Clearance
            questions += 1
            rtsa_ok = doc.rtsa_clearance == 'yes' if isinstance(doc.rtsa_clearance, str) else doc.rtsa_clearance
            if rtsa_ok:
                passed += 1
            
            # Time Briefing Conducted
            questions += 1
            if doc.time_briefing_conducted:
                passed += 1
            
            # Emergency Contact Employer
            questions += 1
            if doc.emergency_contact_employer:
                passed += 1
            
            # Emergency Contact Government
            questions += 1
            if doc.emergency_contact_government:
                passed += 1
            
            earned = Decimal(passed) * SCORE_PER_QUESTION
            max_score = Decimal(questions) * SCORE_PER_QUESTION
            
            return earned, max_score, questions
        except Exception:
            return Decimal('0'), Decimal('25.5'), 17  # 17 questions * 1.5
    
    def calculate_vehicle_check_score_new(self, check_type):
        """
        Calculate score for a vehicle check section using 1.5 points per question.
        Returns tuple of (earned_score, max_score, num_questions)
        """
        check_mapping = {
            'exterior': 'exterior_checks',
            'engine': 'engine_fluid_checks',
            'interior': 'interior_cabin_checks',
            'functional': 'functional_checks',
            'safety': 'safety_equipment_checks',
            'brakes_steering': 'brakes_steering_checks',
        }
        
        try:
            related_name = check_mapping[check_type]
            checks = getattr(self.inspection, related_name).all()
            
            questions = checks.count()
            passed = checks.filter(status='pass').count()
            
            earned = Decimal(passed) * SCORE_PER_QUESTION
            max_score = Decimal(questions) * SCORE_PER_QUESTION if questions > 0 else Decimal('0')
            
            return earned, max_score, questions
        except Exception:
            return Decimal('0'), Decimal('0'), 0
    
    def calculate_health_fitness_score(self):
        """Calculate health & fitness section score - backward compatible"""
        earned, max_score, _ = self.calculate_health_fitness_score_new()
        return float(earned), float(max_score)
    
    def calculate_documentation_score(self):
        """Calculate documentation section score - backward compatible"""
        earned, max_score, _ = self.calculate_documentation_score_new()
        return float(earned), float(max_score)
    
    def calculate_vehicle_check_score(self, check_type):
        """Calculate score for a vehicle check section - backward compatible"""
        earned, max_score, _ = self.calculate_vehicle_check_score_new(check_type)
        return float(earned), float(max_score)
    
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
        """Calculate all section scores and totals using the 1.5 points per question system"""
        # Health & Fitness
        self.health_fitness_score, self.health_fitness_max, self.health_fitness_questions = \
            self.calculate_health_fitness_score_new()
        
        # Documentation
        self.documentation_score, self.documentation_max, self.documentation_questions = \
            self.calculate_documentation_score_new()
        
        # Vehicle checks
        self.vehicle_exterior_score, self.vehicle_exterior_max, self.vehicle_exterior_questions = \
            self.calculate_vehicle_check_score_new('exterior')
        self.engine_fluid_score, self.engine_fluid_max, self.engine_fluid_questions = \
            self.calculate_vehicle_check_score_new('engine')
        self.interior_cabin_score, self.interior_cabin_max, self.interior_cabin_questions = \
            self.calculate_vehicle_check_score_new('interior')
        self.functional_score, self.functional_max, self.functional_questions = \
            self.calculate_vehicle_check_score_new('functional')
        self.safety_equipment_score, self.safety_equipment_max, self.safety_equipment_questions = \
            self.calculate_vehicle_check_score_new('safety')
        
        # Brakes and Steering (new section)
        self.brakes_steering_score, self.brakes_steering_max, self.brakes_steering_questions = \
            self.calculate_vehicle_check_score_new('brakes_steering')
        
        # Totals
        self.total_score = (
            self.health_fitness_score +
            self.documentation_score +
            self.vehicle_exterior_score +
            self.engine_fluid_score +
            self.interior_cabin_score +
            self.functional_score +
            self.safety_equipment_score +
            self.brakes_steering_score
        )
        
        self.max_possible_score = (
            self.health_fitness_max +
            self.documentation_max +
            self.vehicle_exterior_max +
            self.engine_fluid_max +
            self.interior_cabin_max +
            self.functional_max +
            self.safety_equipment_max +
            self.brakes_steering_max
        )
        
        self.total_questions = (
            self.health_fitness_questions +
            self.documentation_questions +
            self.vehicle_exterior_questions +
            self.engine_fluid_questions +
            self.interior_cabin_questions +
            self.functional_questions +
            self.safety_equipment_questions +
            self.brakes_steering_questions
        )
        
        # Percentage and level
        if self.max_possible_score > 0:
            self.score_percentage = round((float(self.total_score) / float(self.max_possible_score)) * 100, 2)
        else:
            self.score_percentage = 0
        
        self.score_level = self.determine_score_level(float(self.score_percentage))
        self.risk_status = self.determine_risk_status(float(self.score_percentage))
        
        # Critical failures
        self.critical_failures = self.check_critical_failures()
        self.has_critical_failures = len(self.critical_failures) > 0
        
        # Travel clearance
        self.is_cleared_for_travel = not self.has_critical_failures and float(self.score_percentage) >= 60
        
        if self.has_critical_failures:
            self.clearance_notes = f"Travel not cleared due to critical failures: {', '.join(self.critical_failures)}"
        elif float(self.score_percentage) < 60:
            self.clearance_notes = f"Travel not cleared due to low overall score ({self.score_percentage}%)"
        else:
            self.clearance_notes = "All checks passed. Vehicle and driver cleared for travel."
    
    def save(self, *args, **kwargs):
        """Calculate all scores before saving"""
        self.calculate_all_scores()
        super().save(*args, **kwargs)
    
    def get_section_summary(self):
        """Return a summary of all section scores with subtotals"""
        sections = [
            {
                'section': 'Health & Fitness',
                'score': float(self.health_fitness_score),
                'max': float(self.health_fitness_max),
                'questions': self.health_fitness_questions,
                'percentage': round((float(self.health_fitness_score) / float(self.health_fitness_max) * 100), 1) if self.health_fitness_max > 0 else 0,
                'subtotal': f"{float(self.health_fitness_score)}/{float(self.health_fitness_max)}"
            },
            {
                'section': 'Documentation & Compliance',
                'score': float(self.documentation_score),
                'max': float(self.documentation_max),
                'questions': self.documentation_questions,
                'percentage': round((float(self.documentation_score) / float(self.documentation_max) * 100), 1) if self.documentation_max > 0 else 0,
                'subtotal': f"{float(self.documentation_score)}/{float(self.documentation_max)}"
            },
            {
                'section': 'Vehicle Exterior',
                'score': float(self.vehicle_exterior_score),
                'max': float(self.vehicle_exterior_max),
                'questions': self.vehicle_exterior_questions,
                'percentage': round((float(self.vehicle_exterior_score) / float(self.vehicle_exterior_max) * 100), 1) if self.vehicle_exterior_max > 0 else 0,
                'subtotal': f"{float(self.vehicle_exterior_score)}/{float(self.vehicle_exterior_max)}"
            },
            {
                'section': 'Engine & Fluids',
                'score': float(self.engine_fluid_score),
                'max': float(self.engine_fluid_max),
                'questions': self.engine_fluid_questions,
                'percentage': round((float(self.engine_fluid_score) / float(self.engine_fluid_max) * 100), 1) if self.engine_fluid_max > 0 else 0,
                'subtotal': f"{float(self.engine_fluid_score)}/{float(self.engine_fluid_max)}"
            },
            {
                'section': 'Interior & Cabin',
                'score': float(self.interior_cabin_score),
                'max': float(self.interior_cabin_max),
                'questions': self.interior_cabin_questions,
                'percentage': round((float(self.interior_cabin_score) / float(self.interior_cabin_max) * 100), 1) if self.interior_cabin_max > 0 else 0,
                'subtotal': f"{float(self.interior_cabin_score)}/{float(self.interior_cabin_max)}"
            },
            {
                'section': 'Functional Checks',
                'score': float(self.functional_score),
                'max': float(self.functional_max),
                'questions': self.functional_questions,
                'percentage': round((float(self.functional_score) / float(self.functional_max) * 100), 1) if self.functional_max > 0 else 0,
                'subtotal': f"{float(self.functional_score)}/{float(self.functional_max)}"
            },
            {
                'section': 'Safety Equipment',
                'score': float(self.safety_equipment_score),
                'max': float(self.safety_equipment_max),
                'questions': self.safety_equipment_questions,
                'percentage': round((float(self.safety_equipment_score) / float(self.safety_equipment_max) * 100), 1) if self.safety_equipment_max > 0 else 0,
                'subtotal': f"{float(self.safety_equipment_score)}/{float(self.safety_equipment_max)}"
            },
            {
                'section': 'Brakes & Steering',
                'score': float(self.brakes_steering_score),
                'max': float(self.brakes_steering_max),
                'questions': self.brakes_steering_questions,
                'percentage': round((float(self.brakes_steering_score) / float(self.brakes_steering_max) * 100), 1) if self.brakes_steering_max > 0 else 0,
                'subtotal': f"{float(self.brakes_steering_score)}/{float(self.brakes_steering_max)}"
            },
        ]
        return sections
    
    def get_total_summary(self):
        """Return overall total summary with risk status"""
        return {
            'total_score': float(self.total_score),
            'max_possible_score': float(self.max_possible_score),
            'total_questions': self.total_questions,
            'score_percentage': float(self.score_percentage),
            'score_level': self.score_level,
            'score_level_display': self.get_score_level_display(),
            'risk_status': self.risk_status,
            'risk_status_display': self.get_risk_status_display(),
            'is_cleared_for_travel': self.is_cleared_for_travel,
            'has_critical_failures': self.has_critical_failures,
            'critical_failures': self.critical_failures,
            'clearance_notes': self.clearance_notes,
        }
