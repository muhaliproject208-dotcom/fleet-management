from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone
from datetime import date


class InspectionStatus(models.TextChoices):
    """Status choices for pre-trip inspections"""
    DRAFT = 'draft', 'Draft'
    SUBMITTED = 'submitted', 'Submitted'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'
    POST_TRIP_IN_PROGRESS = 'post_trip_in_progress', 'Post-Trip In Progress'
    POST_TRIP_COMPLETED = 'post_trip_completed', 'Post-Trip Completed'


class PreTripInspection(models.Model):
    """
    Pre-Trip Inspection model for fleet management system.
    Ties together drivers, vehicles, mechanics, and supervisors in the inspection workflow.
    """
    
    inspection_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        db_index=True,
        help_text="Auto-generated inspection ID in format INSP-XXXX"
    )
    driver = models.ForeignKey(
        'drivers.Driver',
        on_delete=models.PROTECT,
        related_name='inspections',
        help_text="Driver assigned to this inspection"
    )
    vehicle = models.ForeignKey(
        'vehicles.Vehicle',
        on_delete=models.PROTECT,
        related_name='inspections',
        help_text="Vehicle being inspected"
    )
    supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='supervised_inspections',
        help_text="Transport Supervisor who created this inspection"
    )
    mechanic = models.ForeignKey(
        'mechanics.Mechanic',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inspections',
        help_text="Mechanic assigned to this inspection (optional)"
    )
    inspection_date = models.DateField(
        help_text="Date of the inspection"
    )
    route = models.CharField(
        max_length=200,
        help_text="Route for the trip (e.g., Lusaka - Ndola)"
    )
    approved_driving_hours = models.CharField(
        max_length=20,
        help_text="Approved driving hours (e.g., 6 hrs 50 mins)"
    )
    approved_rest_stops = models.IntegerField(
        default=0,
        help_text="Number of approved rest stops"
    )
    status = models.CharField(
        max_length=25,
        choices=InspectionStatus.choices,
        default=InspectionStatus.DRAFT,
        db_index=True,
        help_text="Current status of the inspection"
    )
    approval_status_updated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when approval status was last updated"
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_inspections',
        help_text="Fleet Manager who approved/rejected this inspection"
    )
    rejection_reason = models.TextField(
        blank=True,
        help_text="Reason for rejection (if applicable)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-inspection_date', '-created_at']
        indexes = [
            models.Index(fields=['inspection_id'], name='inspections_inspection_id_idx'),
            models.Index(fields=['status'], name='inspections_status_30a247_idx'),
            models.Index(fields=['inspection_date'], name='inspections_date_idx'),
        ]
        verbose_name = 'Pre-Trip Inspection'
        verbose_name_plural = 'Pre-Trip Inspections'
    
    def __str__(self):
        return f"{self.inspection_id} - {self.driver.full_name} - {self.vehicle.registration_number}"
    
    def save(self, *args, **kwargs):
        """Override save to auto-generate inspection_id if not exists"""
        if not self.inspection_id:
            self.inspection_id = self._generate_inspection_id()
        super().save(*args, **kwargs)
    
    def _generate_inspection_id(self):
        """Generate inspection ID in format INSP-XXXX (4-digit sequential)"""
        last_inspection = PreTripInspection.objects.all().order_by('-inspection_id').first()
        
        if last_inspection and last_inspection.inspection_id:
            try:
                # Extract the numeric part from the last inspection_id
                last_number = int(last_inspection.inspection_id.split('-')[1])
                new_number = last_number + 1
            except (IndexError, ValueError):
                new_number = 1
        else:
            new_number = 1
        
        return f"INSP-{new_number:04d}"
    
    def clean(self):
        """Validate model fields"""
        super().clean()
        
        # Validate inspection date cannot be in the future
        if self.inspection_date and self.inspection_date > date.today():
            raise ValidationError({
                'inspection_date': 'Inspection date cannot be in the future.'
            })
        
        # Validate driver is active
        if self.driver and not self.driver.is_active:
            raise ValidationError({
                'driver': 'Selected driver is not active.'
            })
        
        # Validate vehicle is active
        if self.vehicle and not self.vehicle.is_active:
            raise ValidationError({
                'vehicle': 'Selected vehicle is not active.'
            })
        
        # Validate mechanic is active (if assigned)
        if self.mechanic and not self.mechanic.is_active:
            raise ValidationError({
                'mechanic': 'Selected mechanic is not active.'
            })
    
    def can_edit(self):
        """Return True only if status is 'draft' or 'rejected'"""
        return self.status in [InspectionStatus.DRAFT, InspectionStatus.REJECTED]
    
    def get_completion_status(self):
        """
        Calculate completion status for draft inspections.
        Returns: {
            'completed_steps': [1, 2, 3, ...],
            'next_step': 4,
            'completion_percentage': 33.33,
            'total_steps': 9
        }
        """
        completed_steps = [1]  # Step 1 is always complete (basic info)
        
        # Step 2: Health & Fitness Check
        try:
            self.health_fitness
            completed_steps.append(2)
        except Exception:
            pass
        
        # Step 3: Documentation & Compliance
        try:
            self.documentation
            completed_steps.append(3)
        except Exception:
            pass
        
        # Step 4: Exterior Checks
        try:
            if self.exterior_checks.exists():
                completed_steps.append(4)
        except Exception:
            pass
        
        # Step 5: Engine Checks
        try:
            if self.engine_fluid_checks.exists():
                completed_steps.append(5)
        except Exception:
            pass
        
        # Step 6: Interior Checks
        try:
            if self.interior_cabin_checks.exists():
                completed_steps.append(6)
        except Exception:
            pass
        
        # Step 7: Functional Checks
        try:
            if self.functional_checks.exists():
                completed_steps.append(7)
        except Exception:
            pass
        
        # Step 8: Safety Equipment Checks
        try:
            if self.safety_equipment_checks.exists():
                completed_steps.append(8)
        except Exception:
            pass
        
        # Step 9: Final Verification (supervisor remarks)
        try:
            self.supervisor_remarks
            completed_steps.append(9)
        except Exception:
            pass
        
        total_steps = 9
        next_step = max(completed_steps) + 1 if max(completed_steps) < total_steps else total_steps
        completion_percentage = round((len(completed_steps) / total_steps) * 100, 2)
        
        return {
            'completed_steps': completed_steps,
            'next_step': next_step if next_step <= total_steps else None,
            'completion_percentage': completion_percentage,
            'total_steps': total_steps
        }
    
    def get_post_trip_completion_status(self):
        """
        Calculate completion status for post-trip inspections.
        Returns: {
            'completed_steps': [1, 2, 3, ...],
            'next_step': 4,
            'completion_percentage': 33.33,
            'total_steps': 8
        }
        """
        completed_steps = []
        
        # Step 1: Trip Behavior Monitoring
        try:
            if self.trip_behaviors.exists():
                completed_steps.append(1)
        except Exception:
            pass
        
        # Step 2: Driving Behavior Check
        try:
            if self.driving_behaviors.exists():
                completed_steps.append(2)
        except Exception:
            pass
        
        # Step 3: Post-Trip Report
        try:
            self.post_trip
            completed_steps.append(3)
        except Exception:
            pass
        
        # Step 4: Risk Score Summary
        try:
            self.risk_score
            completed_steps.append(4)
        except Exception:
            pass
        
        # Step 5: Corrective Measures (optional - always count as complete if we pass step 4)
        if 4 in completed_steps:
            completed_steps.append(5)
        
        # Step 6: Enforcement Actions (optional - always count as complete if we pass step 5)
        if 5 in completed_steps:
            completed_steps.append(6)
        
        # Step 7: Evaluation Summary
        try:
            self.evaluation
            completed_steps.append(7)
        except Exception:
            pass
        
        # Step 8: Driver Sign-Off
        try:
            if self.sign_offs.filter(role='driver').exists():
                completed_steps.append(8)
        except Exception:
            pass
        
        total_steps = 8
        next_step = min([s for s in range(1, total_steps + 1) if s not in completed_steps], default=total_steps + 1)
        completion_percentage = round((len(completed_steps) / total_steps) * 100, 2)
        
        return {
            'completed_steps': sorted(completed_steps),
            'next_step': next_step if next_step <= total_steps else None,
            'completion_percentage': completion_percentage,
            'total_steps': total_steps,
            'is_complete': len(completed_steps) == total_steps
        }
    
    def submit_for_approval(self):
        """
        Change status to 'submitted'.
        Validate that all required sections are complete before submission.
        Check for critical failures in vehicle checks.
        """
        if self.status != InspectionStatus.DRAFT:
            raise ValidationError(
                f"Can only submit inspections with 'draft' status. Current status: {self.status}"
            )
        
        # Validate all required fields are present
        if not all([self.driver, self.vehicle, self.supervisor, self.route, self.approved_driving_hours]):
            raise ValidationError(
                "Cannot submit incomplete inspection. All required fields must be filled."
            )
        
        self.status = InspectionStatus.SUBMITTED
        self.save()
    
    def approve(self, approved_by_user):
        """
        Change status to 'approved'.
        Only Fleet Managers can approve inspections.
        """
        if self.status != InspectionStatus.SUBMITTED:
            raise ValidationError(
                f"Can only approve inspections with 'submitted' status. Current status: {self.status}"
            )
        
        # Validate user has Fleet Manager role
        if not (approved_by_user.is_fleet_manager_role or approved_by_user.is_superuser_role):
            raise ValidationError(
                "Only Fleet Managers can approve inspections."
            )
        
        self.status = InspectionStatus.APPROVED
        self.approved_by = approved_by_user
        self.approval_status_updated_at = timezone.now()
        self.rejection_reason = ''  # Clear any previous rejection reason
        self.save()
    
    def reject(self, approved_by_user, reason):
        """
        Change status to 'rejected'.
        Only Fleet Managers can reject inspections.
        Requires a rejection reason.
        """
        if self.status != InspectionStatus.SUBMITTED:
            raise ValidationError(
                f"Can only reject inspections with 'submitted' status. Current status: {self.status}"
            )
        
        # Validate user has Fleet Manager role
        if not (approved_by_user.is_fleet_manager_role or approved_by_user.is_superuser_role):
            raise ValidationError(
                "Only Fleet Managers can reject inspections."
            )
        
        if not reason or not reason.strip():
            raise ValidationError(
                "Rejection reason is required."
            )
        
        self.status = InspectionStatus.REJECTED
        self.approved_by = approved_by_user
        self.approval_status_updated_at = timezone.now()
        self.rejection_reason = reason
        self.save()
    
    def check_and_update_post_trip_status(self):
        """
        Check if post-trip inspection is complete and update status accordingly.
        Call this after saving any post-trip related data.
        """
        if self.status != InspectionStatus.POST_TRIP_IN_PROGRESS:
            return False
        
        completion_info = self.get_post_trip_completion_status()
        
        if completion_info.get('is_complete', False):
            self.status = InspectionStatus.POST_TRIP_COMPLETED
            self.save(update_fields=['status'])
            return True
        
        return False
