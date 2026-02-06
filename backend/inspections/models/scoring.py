"""
Pre-Trip Score Summary Model
Calculates and stores overall pre-trip checklist scores.
Each question in the pre-checklist carries a score of 1 point.
Total percentage = (earned points / total questions across all 8 forms) * 100
"""

from django.db import models
from decimal import Decimal
from .base import PreTripInspection
from .health_fitness import HEALTH_FITNESS_SCORES


# Standard score per question in pre-trip checklist
SCORE_PER_QUESTION = Decimal('1')

# Total questions across all 8 pre-checklist forms
# Health & Fitness: 7, Documentation: 17, Exterior: 7, Engine: 6,
# Interior: 6, Functional: 4, Safety Equipment: 8, Brakes & Steering: 9
TOTAL_PRECHECKLIST_QUESTIONS = 64

# Section question counts (for calculating section weight)
SECTION_QUESTIONS = {
    'health_fitness': 7,
    'documentation': 17,
    'vehicle_exterior': 7,
    'engine_fluid': 6,
    'interior_cabin': 6,
    'functional': 4,
    'safety_equipment': 8,
    'brakes_steering': 9,
}

# Section weights as percentage of total (calculated from question counts)
SECTION_WEIGHTS = {
    key: round((count / TOTAL_PRECHECKLIST_QUESTIONS) * 100, 2)
    for key, count in SECTION_QUESTIONS.items()
}


class SectionRiskLevel(models.TextChoices):
    """Risk level choices for individual sections"""
    NO_RISK = 'no_risk', 'No Risk'
    VERY_LOW_RISK = 'very_low_risk', 'Very Low Risk'
    LOW_RISK = 'low_risk', 'Low Risk'
    HIGH_RISK = 'high_risk', 'High Risk'


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
    """Risk status choices based on overall score"""
    NO_RISK = 'no_risk', 'No Risk'
    VERY_LOW_RISK = 'very_low_risk', 'Very Low Risk'
    LOW_RISK = 'low_risk', 'Low Risk'
    HIGH_RISK = 'high_risk', 'High Risk'


def get_section_risk_level(percentage: float) -> str:
    """Determine risk level for a section based on its percentage score"""
    if percentage >= 100:
        return SectionRiskLevel.NO_RISK
    elif percentage >= 85:
        return SectionRiskLevel.VERY_LOW_RISK
    elif percentage >= 70:
        return SectionRiskLevel.LOW_RISK
    else:
        return SectionRiskLevel.HIGH_RISK


def get_section_risk_display(risk_level: str) -> str:
    """Get display name for section risk level"""
    displays = {
        SectionRiskLevel.NO_RISK: 'No Risk',
        SectionRiskLevel.VERY_LOW_RISK: 'Very Low Risk',
        SectionRiskLevel.LOW_RISK: 'Low Risk',
        SectionRiskLevel.HIGH_RISK: 'High Risk',
    }
    return displays.get(risk_level, 'Unknown')


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
    Each question carries 1 point. Total percentage = (earned / 64) * 100.
    """
    
    inspection = models.OneToOneField(
        PreTripInspection,
        on_delete=models.CASCADE,
        related_name='pre_trip_score',
        help_text="Associated pre-trip inspection"
    )
    
    # Section scores (1 point per question)
    health_fitness_score = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Health & Fitness section score (points earned)"
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
    health_fitness_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Health & Fitness percentage of total (out of 100%)"
    )
    health_fitness_risk = models.CharField(
        max_length=20,
        choices=SectionRiskLevel.choices,
        default=SectionRiskLevel.HIGH_RISK,
        help_text="Risk level for Health & Fitness section"
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
    documentation_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Documentation percentage of total (out of 100%)"
    )
    documentation_risk = models.CharField(
        max_length=20,
        choices=SectionRiskLevel.choices,
        default=SectionRiskLevel.HIGH_RISK,
        help_text="Risk level for Documentation section"
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
    vehicle_exterior_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Vehicle Exterior percentage of total (out of 100%)"
    )
    vehicle_exterior_risk = models.CharField(
        max_length=20,
        choices=SectionRiskLevel.choices,
        default=SectionRiskLevel.HIGH_RISK,
        help_text="Risk level for Vehicle Exterior section"
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
    engine_fluid_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Engine & Fluid percentage of total (out of 100%)"
    )
    engine_fluid_risk = models.CharField(
        max_length=20,
        choices=SectionRiskLevel.choices,
        default=SectionRiskLevel.HIGH_RISK,
        help_text="Risk level for Engine & Fluid section"
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
    interior_cabin_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Interior & Cabin percentage of total (out of 100%)"
    )
    interior_cabin_risk = models.CharField(
        max_length=20,
        choices=SectionRiskLevel.choices,
        default=SectionRiskLevel.HIGH_RISK,
        help_text="Risk level for Interior & Cabin section"
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
    functional_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Functional percentage of total (out of 100%)"
    )
    functional_risk = models.CharField(
        max_length=20,
        choices=SectionRiskLevel.choices,
        default=SectionRiskLevel.HIGH_RISK,
        help_text="Risk level for Functional section"
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
    safety_equipment_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Safety Equipment percentage of total (out of 100%)"
    )
    safety_equipment_risk = models.CharField(
        max_length=20,
        choices=SectionRiskLevel.choices,
        default=SectionRiskLevel.HIGH_RISK,
        help_text="Risk level for Safety Equipment section"
    )
    
    # Brakes and Steering section
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
    brakes_steering_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Brakes & Steering percentage of total (out of 100%)"
    )
    brakes_steering_risk = models.CharField(
        max_length=20,
        choices=SectionRiskLevel.choices,
        default=SectionRiskLevel.HIGH_RISK,
        help_text="Risk level for Brakes & Steering section"
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
        """Determine overall risk status based on percentage"""
        if percentage >= 100:
            return RiskStatus.NO_RISK
        elif percentage >= 85:
            return RiskStatus.VERY_LOW_RISK
        elif percentage >= 70:
            return RiskStatus.LOW_RISK
        else:
            return RiskStatus.HIGH_RISK
    
    def calculate_health_fitness_score_new(self):
        """
        Calculate health & fitness section score using 1 point per question.
        Returns tuple of (earned_score, max_score, num_questions, percentage_of_total)
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
            # Calculate percentage of total prechecklist (out of 100%)
            percentage_of_total = round((float(earned) / TOTAL_PRECHECKLIST_QUESTIONS) * 100, 2)
            
            return earned, max_score, questions, percentage_of_total
        except Exception:
            return Decimal('0'), Decimal('7'), 7, 0.0  # 7 questions * 1 point
    
    def calculate_documentation_score_new(self):
        """
        Calculate documentation section score using 1 point per question.
        Returns tuple of (earned_score, max_score, num_questions, percentage_of_total)
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
            # Calculate percentage of total prechecklist (out of 100%)
            percentage_of_total = round((float(earned) / TOTAL_PRECHECKLIST_QUESTIONS) * 100, 2)
            
            return earned, max_score, questions, percentage_of_total
        except Exception:
            return Decimal('0'), Decimal('17'), 17, 0.0  # 17 questions * 1 point
    
    def calculate_vehicle_check_score_new(self, check_type):
        """
        Calculate score for a vehicle check section using 1 point per question.
        Returns tuple of (earned_score, max_score, num_questions, percentage_of_total)
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
            # Calculate percentage of total prechecklist (out of 100%)
            percentage_of_total = round((float(earned) / TOTAL_PRECHECKLIST_QUESTIONS) * 100, 2) if TOTAL_PRECHECKLIST_QUESTIONS > 0 else 0.0
            
            return earned, max_score, questions, percentage_of_total
        except Exception:
            return Decimal('0'), Decimal('0'), 0, 0.0
    
    def calculate_health_fitness_score(self):
        """Calculate health & fitness section score - backward compatible"""
        earned, max_score, _, _ = self.calculate_health_fitness_score_new()
        return float(earned), float(max_score)
    
    def calculate_documentation_score(self):
        """Calculate documentation section score - backward compatible"""
        earned, max_score, _, _ = self.calculate_documentation_score_new()
        return float(earned), float(max_score)
    
    def calculate_vehicle_check_score(self, check_type):
        """Calculate score for a vehicle check section - backward compatible"""
        earned, max_score, _, _ = self.calculate_vehicle_check_score_new(check_type)
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
        """Calculate all section scores and totals using 1 point per question system"""
        # Health & Fitness
        self.health_fitness_score, self.health_fitness_max, self.health_fitness_questions, self.health_fitness_percentage = \
            self.calculate_health_fitness_score_new()
        # Calculate section-specific risk based on section percentage (score/max * 100)
        section_pct = round((float(self.health_fitness_score) / float(self.health_fitness_max) * 100), 2) if self.health_fitness_max > 0 else 0
        self.health_fitness_risk = get_section_risk_level(section_pct)
        
        # Documentation
        self.documentation_score, self.documentation_max, self.documentation_questions, self.documentation_percentage = \
            self.calculate_documentation_score_new()
        section_pct = round((float(self.documentation_score) / float(self.documentation_max) * 100), 2) if self.documentation_max > 0 else 0
        self.documentation_risk = get_section_risk_level(section_pct)
        
        # Vehicle checks
        self.vehicle_exterior_score, self.vehicle_exterior_max, self.vehicle_exterior_questions, self.vehicle_exterior_percentage = \
            self.calculate_vehicle_check_score_new('exterior')
        section_pct = round((float(self.vehicle_exterior_score) / float(self.vehicle_exterior_max) * 100), 2) if self.vehicle_exterior_max > 0 else 0
        self.vehicle_exterior_risk = get_section_risk_level(section_pct)
        
        self.engine_fluid_score, self.engine_fluid_max, self.engine_fluid_questions, self.engine_fluid_percentage = \
            self.calculate_vehicle_check_score_new('engine')
        section_pct = round((float(self.engine_fluid_score) / float(self.engine_fluid_max) * 100), 2) if self.engine_fluid_max > 0 else 0
        self.engine_fluid_risk = get_section_risk_level(section_pct)
        
        self.interior_cabin_score, self.interior_cabin_max, self.interior_cabin_questions, self.interior_cabin_percentage = \
            self.calculate_vehicle_check_score_new('interior')
        section_pct = round((float(self.interior_cabin_score) / float(self.interior_cabin_max) * 100), 2) if self.interior_cabin_max > 0 else 0
        self.interior_cabin_risk = get_section_risk_level(section_pct)
        
        self.functional_score, self.functional_max, self.functional_questions, self.functional_percentage = \
            self.calculate_vehicle_check_score_new('functional')
        section_pct = round((float(self.functional_score) / float(self.functional_max) * 100), 2) if self.functional_max > 0 else 0
        self.functional_risk = get_section_risk_level(section_pct)
        
        self.safety_equipment_score, self.safety_equipment_max, self.safety_equipment_questions, self.safety_equipment_percentage = \
            self.calculate_vehicle_check_score_new('safety')
        section_pct = round((float(self.safety_equipment_score) / float(self.safety_equipment_max) * 100), 2) if self.safety_equipment_max > 0 else 0
        self.safety_equipment_risk = get_section_risk_level(section_pct)
        
        # Brakes and Steering
        self.brakes_steering_score, self.brakes_steering_max, self.brakes_steering_questions, self.brakes_steering_percentage = \
            self.calculate_vehicle_check_score_new('brakes_steering')
        section_pct = round((float(self.brakes_steering_score) / float(self.brakes_steering_max) * 100), 2) if self.brakes_steering_max > 0 else 0
        self.brakes_steering_risk = get_section_risk_level(section_pct)
        
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
                'section_percentage': round((float(self.health_fitness_score) / float(self.health_fitness_max) * 100), 1) if self.health_fitness_max > 0 else 0,
                'total_percentage': float(self.health_fitness_percentage),
                'max_weight': SECTION_WEIGHTS.get('health_fitness', 0),
                'risk_level': self.health_fitness_risk,
                'risk_display': get_section_risk_display(self.health_fitness_risk),
                'subtotal': f"{int(self.health_fitness_score)}/{int(self.health_fitness_max)}"
            },
            {
                'section': 'Documentation & Compliance',
                'score': float(self.documentation_score),
                'max': float(self.documentation_max),
                'questions': self.documentation_questions,
                'percentage': round((float(self.documentation_score) / float(self.documentation_max) * 100), 1) if self.documentation_max > 0 else 0,
                'section_percentage': round((float(self.documentation_score) / float(self.documentation_max) * 100), 1) if self.documentation_max > 0 else 0,
                'total_percentage': float(self.documentation_percentage),
                'max_weight': SECTION_WEIGHTS.get('documentation', 0),
                'risk_level': self.documentation_risk,
                'risk_display': get_section_risk_display(self.documentation_risk),
                'subtotal': f"{int(self.documentation_score)}/{int(self.documentation_max)}"
            },
            {
                'section': 'Vehicle Exterior',
                'score': float(self.vehicle_exterior_score),
                'max': float(self.vehicle_exterior_max),
                'questions': self.vehicle_exterior_questions,
                'percentage': round((float(self.vehicle_exterior_score) / float(self.vehicle_exterior_max) * 100), 1) if self.vehicle_exterior_max > 0 else 0,
                'section_percentage': round((float(self.vehicle_exterior_score) / float(self.vehicle_exterior_max) * 100), 1) if self.vehicle_exterior_max > 0 else 0,
                'total_percentage': float(self.vehicle_exterior_percentage),
                'max_weight': SECTION_WEIGHTS.get('vehicle_exterior', 0),
                'risk_level': self.vehicle_exterior_risk,
                'risk_display': get_section_risk_display(self.vehicle_exterior_risk),
                'subtotal': f"{int(self.vehicle_exterior_score)}/{int(self.vehicle_exterior_max)}"
            },
            {
                'section': 'Engine & Fluids',
                'score': float(self.engine_fluid_score),
                'max': float(self.engine_fluid_max),
                'questions': self.engine_fluid_questions,
                'percentage': round((float(self.engine_fluid_score) / float(self.engine_fluid_max) * 100), 1) if self.engine_fluid_max > 0 else 0,
                'section_percentage': round((float(self.engine_fluid_score) / float(self.engine_fluid_max) * 100), 1) if self.engine_fluid_max > 0 else 0,
                'total_percentage': float(self.engine_fluid_percentage),
                'max_weight': SECTION_WEIGHTS.get('engine_fluid', 0),
                'risk_level': self.engine_fluid_risk,
                'risk_display': get_section_risk_display(self.engine_fluid_risk),
                'subtotal': f"{int(self.engine_fluid_score)}/{int(self.engine_fluid_max)}"
            },
            {
                'section': 'Interior & Cabin',
                'score': float(self.interior_cabin_score),
                'max': float(self.interior_cabin_max),
                'questions': self.interior_cabin_questions,
                'percentage': round((float(self.interior_cabin_score) / float(self.interior_cabin_max) * 100), 1) if self.interior_cabin_max > 0 else 0,
                'section_percentage': round((float(self.interior_cabin_score) / float(self.interior_cabin_max) * 100), 1) if self.interior_cabin_max > 0 else 0,
                'total_percentage': float(self.interior_cabin_percentage),
                'max_weight': SECTION_WEIGHTS.get('interior_cabin', 0),
                'risk_level': self.interior_cabin_risk,
                'risk_display': get_section_risk_display(self.interior_cabin_risk),
                'subtotal': f"{int(self.interior_cabin_score)}/{int(self.interior_cabin_max)}"
            },
            {
                'section': 'Functional Checks',
                'score': float(self.functional_score),
                'max': float(self.functional_max),
                'questions': self.functional_questions,
                'percentage': round((float(self.functional_score) / float(self.functional_max) * 100), 1) if self.functional_max > 0 else 0,
                'section_percentage': round((float(self.functional_score) / float(self.functional_max) * 100), 1) if self.functional_max > 0 else 0,
                'total_percentage': float(self.functional_percentage),
                'max_weight': SECTION_WEIGHTS.get('functional', 0),
                'risk_level': self.functional_risk,
                'risk_display': get_section_risk_display(self.functional_risk),
                'subtotal': f"{int(self.functional_score)}/{int(self.functional_max)}"
            },
            {
                'section': 'Safety Equipment',
                'score': float(self.safety_equipment_score),
                'max': float(self.safety_equipment_max),
                'questions': self.safety_equipment_questions,
                'percentage': round((float(self.safety_equipment_score) / float(self.safety_equipment_max) * 100), 1) if self.safety_equipment_max > 0 else 0,
                'section_percentage': round((float(self.safety_equipment_score) / float(self.safety_equipment_max) * 100), 1) if self.safety_equipment_max > 0 else 0,
                'total_percentage': float(self.safety_equipment_percentage),
                'max_weight': SECTION_WEIGHTS.get('safety_equipment', 0),
                'risk_level': self.safety_equipment_risk,
                'risk_display': get_section_risk_display(self.safety_equipment_risk),
                'subtotal': f"{int(self.safety_equipment_score)}/{int(self.safety_equipment_max)}"
            },
            {
                'section': 'Brakes & Steering',
                'score': float(self.brakes_steering_score),
                'max': float(self.brakes_steering_max),
                'questions': self.brakes_steering_questions,
                'percentage': round((float(self.brakes_steering_score) / float(self.brakes_steering_max) * 100), 1) if self.brakes_steering_max > 0 else 0,
                'section_percentage': round((float(self.brakes_steering_score) / float(self.brakes_steering_max) * 100), 1) if self.brakes_steering_max > 0 else 0,
                'total_percentage': float(self.brakes_steering_percentage),
                'max_weight': SECTION_WEIGHTS.get('brakes_steering', 0),
                'risk_level': self.brakes_steering_risk,
                'risk_display': get_section_risk_display(self.brakes_steering_risk),
                'subtotal': f"{int(self.brakes_steering_score)}/{int(self.brakes_steering_max)}"
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


# Post-Checklist question counts
# Trip Behavior Monitoring: 12, Driving Behavior Check: 11, Post-Trip Report: 5
TOTAL_POSTCHECKLIST_QUESTIONS = 28

POST_SECTION_QUESTIONS = {
    'trip_behavior': 12,
    'driving_behavior': 11,
    'post_trip_report': 5,
}


class FinalRiskLevel(models.TextChoices):
    """Final risk level choices"""
    NO_RISK = 'no_risk', 'No Risk'
    VERY_LOW_RISK = 'very_low_risk', 'Very Low Risk'
    LOW_RISK = 'low_risk', 'Low Risk'
    HIGH_RISK = 'high_risk', 'High Risk'


class FinalStatus(models.TextChoices):
    """Final status choices"""
    PASSED = 'passed', 'Passed'
    FAILED = 'failed', 'Failed'
    NEEDS_REVIEW = 'needs_review', 'Needs Review'


def get_final_risk_level(percentage):
    """Determine final risk level based on percentage"""
    if percentage >= 100:
        return FinalRiskLevel.NO_RISK
    elif percentage >= 85:
        return FinalRiskLevel.VERY_LOW_RISK
    elif percentage >= 70:
        return FinalRiskLevel.LOW_RISK
    else:
        return FinalRiskLevel.HIGH_RISK


def get_final_risk_display(risk_level):
    """Get human-readable display for final risk level"""
    display_map = {
        FinalRiskLevel.NO_RISK: 'No Risk',
        FinalRiskLevel.VERY_LOW_RISK: 'Very Low Risk',
        FinalRiskLevel.LOW_RISK: 'Low Risk',
        FinalRiskLevel.HIGH_RISK: 'High Risk',
    }
    return display_map.get(risk_level, 'Unknown')


class PostChecklistScoreSummary(models.Model):
    """Post-Checklist Score Summary - calculates scores for post-trip forms"""
    
    inspection = models.OneToOneField(
        PreTripInspection,
        on_delete=models.CASCADE,
        related_name='post_checklist_score',
        help_text="Associated inspection"
    )
    
    # Trip Behavior Monitoring (12 questions)
    trip_behavior_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0'),
        help_text="Score for trip behavior monitoring"
    )
    trip_behavior_max = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('12'),
        help_text="Max score for trip behavior"
    )
    trip_behavior_questions = models.IntegerField(default=12)
    trip_behavior_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0')
    )
    trip_behavior_risk = models.CharField(
        max_length=20,
        choices=SectionRiskLevel.choices,
        default=SectionRiskLevel.HIGH_RISK
    )
    
    # Driving Behavior Check (11 questions)
    driving_behavior_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0'),
        help_text="Score for driving behavior check"
    )
    driving_behavior_max = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('11'),
        help_text="Max score for driving behavior"
    )
    driving_behavior_questions = models.IntegerField(default=11)
    driving_behavior_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0')
    )
    driving_behavior_risk = models.CharField(
        max_length=20,
        choices=SectionRiskLevel.choices,
        default=SectionRiskLevel.HIGH_RISK
    )
    
    # Post-Trip Report (5 scorable questions)
    post_trip_report_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0'),
        help_text="Score for post-trip report"
    )
    post_trip_report_max = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('5'),
        help_text="Max score for post-trip report"
    )
    post_trip_report_questions = models.IntegerField(default=5)
    post_trip_report_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0')
    )
    post_trip_report_risk = models.CharField(
        max_length=20,
        choices=SectionRiskLevel.choices,
        default=SectionRiskLevel.HIGH_RISK
    )
    
    # Overall post-checklist totals
    total_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0'),
        help_text="Total post-checklist score"
    )
    max_possible_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('28'),
        help_text="Maximum possible post-checklist score"
    )
    total_questions = models.IntegerField(default=28)
    score_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0'),
        help_text="Overall post-checklist percentage"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Post-Checklist Score Summary'
        verbose_name_plural = 'Post-Checklist Score Summaries'
    
    def __str__(self):
        return f"{self.inspection.inspection_id} - Post-Checklist: {self.score_percentage}%"
    
    def calculate_trip_behavior_score(self):
        """Calculate score from trip behavior monitoring"""
        try:
            behaviors = self.inspection.trip_behaviors.all()
            total = 0
            for behavior in behaviors:
                # Compliant = 1 point, Violation = 0 points
                if behavior.status == 'compliant':
                    total += 1
            return Decimal(str(total))
        except Exception:
            return Decimal('0')
    
    def calculate_driving_behavior_score(self):
        """Calculate score from driving behavior check"""
        try:
            behaviors = self.inspection.driving_behaviors.all()
            total = 0
            for behavior in behaviors:
                # True (compliant) = 1 point
                if behavior.status:
                    total += 1
            return Decimal(str(total))
        except Exception:
            return Decimal('0')
    
    def calculate_post_trip_report_score(self):
        """Calculate score from post-trip report"""
        try:
            post_trip = self.inspection.post_trip
            total = 0
            
            # No vehicle fault = 1 point (good)
            if not post_trip.vehicle_fault_submitted:
                total += 1
            
            # Final inspection signed = 1 point
            if post_trip.final_inspection_signed:
                total += 1
            
            # Compliance with policy = 1 point
            if post_trip.compliance_with_policy:
                total += 1
            
            # Good attitude = 1 point
            if post_trip.attitude_cooperation:
                total += 1
            
            # No incidents = 1 point (good)
            if not post_trip.incidents_recorded:
                total += 1
            
            return Decimal(str(total))
        except Exception:
            return Decimal('0')
    
    def calculate_all_scores(self):
        """Calculate all post-checklist scores"""
        # Trip Behavior
        self.trip_behavior_score = self.calculate_trip_behavior_score()
        self.trip_behavior_max = Decimal('12')
        self.trip_behavior_questions = 12
        if self.trip_behavior_max > 0:
            pct = (self.trip_behavior_score / self.trip_behavior_max) * 100
            self.trip_behavior_percentage = round(pct, 2)
            self.trip_behavior_risk = get_section_risk_level(float(pct))
        
        # Driving Behavior
        self.driving_behavior_score = self.calculate_driving_behavior_score()
        self.driving_behavior_max = Decimal('11')
        self.driving_behavior_questions = 11
        if self.driving_behavior_max > 0:
            pct = (self.driving_behavior_score / self.driving_behavior_max) * 100
            self.driving_behavior_percentage = round(pct, 2)
            self.driving_behavior_risk = get_section_risk_level(float(pct))
        
        # Post-Trip Report
        self.post_trip_report_score = self.calculate_post_trip_report_score()
        self.post_trip_report_max = Decimal('5')
        self.post_trip_report_questions = 5
        if self.post_trip_report_max > 0:
            pct = (self.post_trip_report_score / self.post_trip_report_max) * 100
            self.post_trip_report_percentage = round(pct, 2)
            self.post_trip_report_risk = get_section_risk_level(float(pct))
        
        # Overall totals
        self.total_score = (
            self.trip_behavior_score +
            self.driving_behavior_score +
            self.post_trip_report_score
        )
        self.max_possible_score = Decimal('28')
        self.total_questions = 28
        
        if self.max_possible_score > 0:
            self.score_percentage = round(
                (self.total_score / self.max_possible_score) * 100, 2
            )
    
    def save(self, *args, **kwargs):
        """Auto-calculate scores before saving"""
        self.calculate_all_scores()
        super().save(*args, **kwargs)
    
    def get_section_summary(self):
        """Return summary of all post-checklist sections"""
        return [
            {
                'section': 'Trip Behavior Monitoring',
                'score': float(self.trip_behavior_score),
                'max': float(self.trip_behavior_max),
                'questions': self.trip_behavior_questions,
                'percentage': float(self.trip_behavior_percentage),
                'risk_level': self.trip_behavior_risk,
                'risk_display': get_section_risk_display(self.trip_behavior_risk),
            },
            {
                'section': 'Driving Behavior Check',
                'score': float(self.driving_behavior_score),
                'max': float(self.driving_behavior_max),
                'questions': self.driving_behavior_questions,
                'percentage': float(self.driving_behavior_percentage),
                'risk_level': self.driving_behavior_risk,
                'risk_display': get_section_risk_display(self.driving_behavior_risk),
            },
            {
                'section': 'Post-Trip Report',
                'score': float(self.post_trip_report_score),
                'max': float(self.post_trip_report_max),
                'questions': self.post_trip_report_questions,
                'percentage': float(self.post_trip_report_percentage),
                'risk_level': self.post_trip_report_risk,
                'risk_display': get_section_risk_display(self.post_trip_report_risk),
            },
        ]


class FinalScoreSummary(models.Model):
    """
    Final Score Summary - combines Pre-Checklist (50%) and Post-Checklist (50%)
    to determine final driver risk level and status.
    """
    
    inspection = models.OneToOneField(
        PreTripInspection,
        on_delete=models.CASCADE,
        related_name='final_score',
        help_text="Associated inspection"
    )
    
    # Pre-Checklist component (50%)
    pre_checklist_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0'),
        help_text="Pre-checklist total score"
    )
    pre_checklist_max = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('64'),
        help_text="Pre-checklist max score"
    )
    pre_checklist_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0'),
        help_text="Pre-checklist percentage (0-100)"
    )
    pre_checklist_weighted = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0'),
        help_text="Pre-checklist weighted contribution (out of 50)"
    )
    
    # Post-Checklist component (50%)
    post_checklist_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0'),
        help_text="Post-checklist total score"
    )
    post_checklist_max = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('28'),
        help_text="Post-checklist max score"
    )
    post_checklist_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0'),
        help_text="Post-checklist percentage (0-100)"
    )
    post_checklist_weighted = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0'),
        help_text="Post-checklist weighted contribution (out of 50)"
    )
    
    # Final combined results
    final_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0'),
        help_text="Final combined percentage (0-100)"
    )
    final_risk_level = models.CharField(
        max_length=20,
        choices=FinalRiskLevel.choices,
        default=FinalRiskLevel.HIGH_RISK,
        help_text="Final risk level"
    )
    final_status = models.CharField(
        max_length=20,
        choices=FinalStatus.choices,
        default=FinalStatus.NEEDS_REVIEW,
        help_text="Final status (Passed/Failed/Needs Review)"
    )
    final_comment = models.TextField(
        blank=True,
        help_text="Final comment based on results"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Final Score Summary'
        verbose_name_plural = 'Final Score Summaries'
    
    def __str__(self):
        return f"{self.inspection.inspection_id} - Final: {self.final_percentage}% ({self.final_status})"
    
    def calculate_final_score(self):
        """Calculate final combined score from pre and post checklists"""
        # Get pre-checklist score
        try:
            pre_score = self.inspection.pre_trip_score
            self.pre_checklist_score = pre_score.total_score
            self.pre_checklist_max = pre_score.max_possible_score
            self.pre_checklist_percentage = pre_score.score_percentage
            # Pre-checklist contributes 50% of final score
            self.pre_checklist_weighted = round(
                (float(pre_score.score_percentage) / 100) * 50, 2
            )
        except Exception:
            self.pre_checklist_score = Decimal('0')
            self.pre_checklist_max = Decimal('64')
            self.pre_checklist_percentage = Decimal('0')
            self.pre_checklist_weighted = Decimal('0')
        
        # Get post-checklist score
        try:
            post_score = self.inspection.post_checklist_score
            self.post_checklist_score = post_score.total_score
            self.post_checklist_max = post_score.max_possible_score
            self.post_checklist_percentage = post_score.score_percentage
            # Post-checklist contributes 50% of final score
            self.post_checklist_weighted = round(
                (float(post_score.score_percentage) / 100) * 50, 2
            )
        except Exception:
            self.post_checklist_score = Decimal('0')
            self.post_checklist_max = Decimal('28')
            self.post_checklist_percentage = Decimal('0')
            self.post_checklist_weighted = Decimal('0')
        
        # Calculate final percentage
        self.final_percentage = Decimal(str(
            float(self.pre_checklist_weighted) + float(self.post_checklist_weighted)
        ))
        
        # Determine final risk level
        self.final_risk_level = get_final_risk_level(float(self.final_percentage))
        
        # Determine final status
        if float(self.final_percentage) >= 70:
            self.final_status = FinalStatus.PASSED
        elif float(self.final_percentage) >= 50:
            self.final_status = FinalStatus.NEEDS_REVIEW
        else:
            self.final_status = FinalStatus.FAILED
        
        # Generate final comment
        self.final_comment = self.generate_final_comment()
    
    def generate_final_comment(self):
        """Generate descriptive comment based on scores"""
        pre_pct = float(self.pre_checklist_percentage)
        post_pct = float(self.post_checklist_percentage)
        final_pct = float(self.final_percentage)
        
        comments = []
        
        # Pre-checklist assessment
        if pre_pct >= 85:
            comments.append("Pre-trip inspection: Excellent compliance.")
        elif pre_pct >= 70:
            comments.append("Pre-trip inspection: Acceptable with minor issues.")
        else:
            comments.append("Pre-trip inspection: Significant deficiencies identified.")
        
        # Post-checklist assessment
        if post_pct >= 85:
            comments.append("Post-trip performance: Outstanding conduct and reporting.")
        elif post_pct >= 70:
            comments.append("Post-trip performance: Satisfactory with room for improvement.")
        else:
            comments.append("Post-trip performance: Major concerns regarding conduct or reporting.")
        
        # Final assessment
        if final_pct >= 85:
            comments.append(f"Overall Assessment: {self.get_final_status_display()} - Driver demonstrated excellent performance.")
        elif final_pct >= 70:
            comments.append(f"Overall Assessment: {self.get_final_status_display()} - Driver meets minimum requirements.")
        elif final_pct >= 50:
            comments.append(f"Overall Assessment: {self.get_final_status_display()} - Driver requires additional training or supervision.")
        else:
            comments.append(f"Overall Assessment: {self.get_final_status_display()} - Driver does not meet safety standards. Immediate action required.")
        
        return " ".join(comments)
    
    def save(self, *args, **kwargs):
        """Auto-calculate final score before saving"""
        self.calculate_final_score()
        super().save(*args, **kwargs)
    
    def get_breakdown(self):
        """Get detailed breakdown of how final score was calculated"""
        breakdown = {
            'pre_checklist': {
                'name': 'Pre-Trip Checklist',
                'weight': 50,
                'score': float(self.pre_checklist_score),
                'max': float(self.pre_checklist_max),
                'percentage': float(self.pre_checklist_percentage),
                'weighted_contribution': float(self.pre_checklist_weighted),
                'sections': [],
            },
            'post_checklist': {
                'name': 'Post-Trip Checklist',
                'weight': 50,
                'score': float(self.post_checklist_score),
                'max': float(self.post_checklist_max),
                'percentage': float(self.post_checklist_percentage),
                'weighted_contribution': float(self.post_checklist_weighted),
                'sections': [],
            },
            'final': {
                'percentage': float(self.final_percentage),
                'risk_level': self.final_risk_level,
                'risk_display': get_final_risk_display(self.final_risk_level),
                'status': self.final_status,
                'status_display': self.get_final_status_display(),
                'comment': self.final_comment,
            }
        }
        
        # Add pre-checklist section details
        try:
            pre_score = self.inspection.pre_trip_score
            breakdown['pre_checklist']['sections'] = pre_score.get_section_summary()
        except Exception:
            pass
        
        # Add post-checklist section details
        try:
            post_score = self.inspection.post_checklist_score
            breakdown['post_checklist']['sections'] = post_score.get_section_summary()
        except Exception:
            pass
        
        return breakdown
