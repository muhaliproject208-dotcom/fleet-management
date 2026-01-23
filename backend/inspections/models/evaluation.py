from django.db import models
from django.core.exceptions import ValidationError
from .base import PreTripInspection


class PerformanceLevel(models.TextChoices):
    """Overall performance level choices"""
    EXCELLENT = 'excellent', 'Excellent'
    SATISFACTORY = 'satisfactory', 'Satisfactory'
    NEEDS_IMPROVEMENT = 'needs_improvement', 'Needs Improvement'
    NON_COMPLIANT = 'non_compliant', 'Non-Compliant'


class SupervisorRemarks(models.Model):
    """Supervisor remarks and recommendations"""
    
    inspection = models.OneToOneField(
        PreTripInspection,
        on_delete=models.CASCADE,
        related_name='supervisor_remarks',
        help_text="Associated pre-trip inspection"
    )
    supervisor_name = models.CharField(
        max_length=100,
        help_text="Name of the supervisor providing remarks"
    )
    remarks = models.TextField(
        help_text="Supervisor's remarks about the inspection"
    )
    recommendation = models.TextField(
        blank=True,
        help_text="Supervisor's recommendations"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Supervisor Remarks'
        verbose_name_plural = 'Supervisor Remarks'
    
    def __str__(self):
        return f"{self.inspection.inspection_id} - Remarks by {self.supervisor_name}"


class EvaluationSummary(models.Model):
    """Evaluation summary with scoring and performance assessment"""
    
    SCORE_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Below Average'),
        (3, '3 - Average'),
        (4, '4 - Good'),
        (5, '5 - Excellent'),
    ]
    
    inspection = models.OneToOneField(
        PreTripInspection,
        on_delete=models.CASCADE,
        related_name='evaluation',
        help_text="Associated pre-trip inspection"
    )
    pre_trip_inspection_score = models.IntegerField(
        choices=SCORE_CHOICES,
        help_text="Score for pre-trip inspection completion (1-5)"
    )
    driving_conduct_score = models.IntegerField(
        choices=SCORE_CHOICES,
        help_text="Score for driving conduct (1-5)"
    )
    incident_management_score = models.IntegerField(
        choices=SCORE_CHOICES,
        help_text="Score for incident management (1-5)"
    )
    post_trip_reporting_score = models.IntegerField(
        choices=SCORE_CHOICES,
        help_text="Score for post-trip reporting (1-5)"
    )
    compliance_documentation_score = models.IntegerField(
        choices=SCORE_CHOICES,
        help_text="Score for compliance and documentation (1-5)"
    )
    overall_performance = models.CharField(
        max_length=20,
        choices=PerformanceLevel.choices,
        help_text="Overall performance level (auto-calculated)"
    )
    comments = models.TextField(
        blank=True,
        help_text="Additional comments"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Evaluation Summary'
        verbose_name_plural = 'Evaluation Summaries'
    
    def __str__(self):
        return f"{self.inspection.inspection_id} - Overall: {self.overall_performance}"
    
    def calculate_average_score(self):
        """Calculate average of all scores"""
        total = (
            self.pre_trip_inspection_score +
            self.driving_conduct_score +
            self.incident_management_score +
            self.post_trip_reporting_score +
            self.compliance_documentation_score
        )
        return total / 5.0
    
    def determine_overall_performance(self):
        """
        Determine overall performance based on average score:
        4.5-5.0: excellent
        3.5-4.4: satisfactory
        2.0-3.4: needs_improvement
        <2.0: non_compliant
        """
        avg = self.calculate_average_score()
        
        if avg >= 4.5:
            return PerformanceLevel.EXCELLENT
        elif avg >= 3.5:
            return PerformanceLevel.SATISFACTORY
        elif avg >= 2.0:
            return PerformanceLevel.NEEDS_IMPROVEMENT
        else:
            return PerformanceLevel.NON_COMPLIANT
    
    def save(self, *args, **kwargs):
        """Auto-calculate overall performance before saving"""
        self.overall_performance = self.determine_overall_performance()
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validate model fields"""
        super().clean()
        
        # Validate all scores are between 1 and 5
        scores = [
            self.pre_trip_inspection_score,
            self.driving_conduct_score,
            self.incident_management_score,
            self.post_trip_reporting_score,
            self.compliance_documentation_score,
        ]
        
        for score in scores:
            if score and (score < 1 or score > 5):
                raise ValidationError('All scores must be between 1 and 5.')
