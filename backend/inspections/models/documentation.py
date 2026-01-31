from django.db import models
from django.core.exceptions import ValidationError
from .base import PreTripInspection


class DocumentStatus(models.TextChoices):
    """Status choices for document validity"""
    VALID = 'valid', 'Valid'
    INVALID = 'invalid', 'Invalid'


class YesNoChoice(models.TextChoices):
    """Yes/No choices for boolean-like fields"""
    YES = 'yes', 'Yes'
    NO = 'no', 'No'


class DocumentationCompliance(models.Model):
    """
    Documentation and Compliance Check model for pre-trip inspections.
    OneToOne relationship with PreTripInspection.
    """
    
    inspection = models.OneToOneField(
        PreTripInspection,
        on_delete=models.CASCADE,
        related_name='documentation',
        help_text="Associated pre-trip inspection"
    )
    
    # Certificate of Fitness Valid (Yes or No)
    certificate_of_fitness_valid = models.CharField(
        max_length=10,
        choices=YesNoChoice.choices,
        default=YesNoChoice.NO,
        help_text="Is Certificate of Fitness valid? (Yes or No)"
    )
    
    # Legacy field for backwards compatibility
    certificate_of_fitness = models.CharField(
        max_length=10,
        choices=DocumentStatus.choices,
        help_text="Certificate of fitness status (legacy)"
    )
    
    # Safety Briefing Provided (Yes or No)
    safety_briefing_provided = models.CharField(
        max_length=10,
        choices=YesNoChoice.choices,
        default=YesNoChoice.NO,
        help_text="Was safety briefing provided? (Yes or No)"
    )
    
    # Time Briefing Conducted
    time_briefing_conducted = models.TimeField(
        null=True,
        blank=True,
        help_text="Time when briefing was conducted"
    )
    
    # RTSA Clearance (If Applicable) (Yes or No)
    rtsa_clearance = models.CharField(
        max_length=10,
        choices=YesNoChoice.choices,
        default=YesNoChoice.NO,
        help_text="RTSA Clearance obtained (If Applicable)? (Yes or No)"
    )
    
    # Emergency Contact - Employer
    emergency_contact_employer = models.CharField(
        max_length=100,
        blank=True,
        help_text="Emergency contact - Employer (name and phone number)"
    )
    
    # Emergency Contact - Government
    emergency_contact_government = models.CharField(
        max_length=100,
        blank=True,
        help_text="Emergency contact - Government (name and phone number)"
    )
    
    # Legacy emergency contact field
    emergency_contact = models.CharField(
        max_length=100,
        blank=True,
        help_text="Emergency contact information (legacy)"
    )
    
    road_tax_valid = models.BooleanField(
        default=False,
        help_text="Road tax is valid"
    )
    insurance_valid = models.BooleanField(
        default=False,
        help_text="Insurance is valid"
    )
    trip_authorization_signed = models.BooleanField(
        default=False,
        help_text="Trip authorization has been signed"
    )
    logbook_present = models.BooleanField(
        default=False,
        help_text="Vehicle logbook is present"
    )
    driver_handbook_present = models.BooleanField(
        default=False,
        help_text="Driver handbook is present"
    )
    permits_valid = models.BooleanField(
        default=False,
        help_text="All permits are valid"
    )
    ppe_available = models.BooleanField(
        default=False,
        help_text="Personal protective equipment is available"
    )
    route_familiarity = models.BooleanField(
        default=False,
        help_text="Driver is familiar with the route"
    )
    emergency_procedures_known = models.BooleanField(
        default=False,
        help_text="Driver knows emergency procedures"
    )
    gps_activated = models.BooleanField(
        default=False,
        help_text="GPS tracking is activated"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Documentation & Compliance Check'
        verbose_name_plural = 'Documentation & Compliance Checks'
    
    def __str__(self):
        status = "Compliant" if self.is_compliant() else "Non-Compliant"
        return f"{self.inspection.inspection_id} - Documentation: {status}"
    
    def is_compliant(self):
        """
        Return True if all required documents are valid.
        Required: certificate of fitness (valid), road tax, insurance, 
        trip authorization, logbook
        """
        cert_fitness_valid = (
            self.certificate_of_fitness_valid == YesNoChoice.YES or 
            self.certificate_of_fitness == DocumentStatus.VALID
        )
        return (
            cert_fitness_valid and
            self.road_tax_valid and
            self.insurance_valid and
            self.trip_authorization_signed and
            self.logbook_present
        )
    
    def get_missing_documents(self):
        """Return list of missing or invalid documents"""
        missing = []
        
        cert_fitness_valid = (
            self.certificate_of_fitness_valid == YesNoChoice.YES or 
            self.certificate_of_fitness == DocumentStatus.VALID
        )
        if not cert_fitness_valid:
            missing.append('Certificate of Fitness')
        if not self.road_tax_valid:
            missing.append('Road Tax')
        if not self.insurance_valid:
            missing.append('Insurance')
        if not self.trip_authorization_signed:
            missing.append('Trip Authorization')
        if not self.logbook_present:
            missing.append('Logbook')
        if not self.driver_handbook_present:
            missing.append('Driver Handbook')
        if not self.permits_valid:
            missing.append('Permits')
        if not self.ppe_available:
            missing.append('PPE')
        if not self.route_familiarity:
            missing.append('Route Familiarity')
        if not self.emergency_procedures_known:
            missing.append('Emergency Procedures Knowledge')
        if not self.gps_activated:
            missing.append('GPS Activation')
        
        # Check safety briefing
        safety_briefing_ok = (
            self.safety_briefing_provided == YesNoChoice.YES if isinstance(self.safety_briefing_provided, str) 
            else self.safety_briefing_provided
        )
        if not safety_briefing_ok:
            missing.append('Safety Briefing')
        
        # Check RTSA clearance
        rtsa_ok = (
            self.rtsa_clearance == YesNoChoice.YES if isinstance(self.rtsa_clearance, str)
            else self.rtsa_clearance
        )
        if not rtsa_ok:
            missing.append('RTSA Clearance')
        
        return missing
    
    def clean(self):
        """Validate model fields"""
        super().clean()
        
        # Validate required documents for compliance
        if not self.is_compliant():
            missing = self.get_missing_documents()
            raise ValidationError(
                f"Cannot proceed with inspection. Missing/invalid documents: {', '.join(missing[:5])}"
            )
