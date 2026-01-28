from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.http import HttpResponse
from django.utils import timezone

from ..models import PreTripInspection, InspectionStatus
from ..serializers import (
    InspectionListSerializer,
    InspectionDetailSerializer,
    InspectionCreateUpdateSerializer,
    PreTripInspectionFullSerializer,
)
from ..pdf_generator import InspectionPDFGenerator
from ..filters import PreTripInspectionFilter
from authentication.permissions import IsTransportSupervisor, IsFleetManager


class InspectionPermission(IsAuthenticated):
    """
    Custom permission for inspections:
    - Transport Supervisors: can create and update their own inspections
    - Fleet Managers: can view all, approve, and reject
    - Admins: full access
    """
    def has_permission(self, request, view):
        # Must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Create permission: Transport Supervisor or higher
        if view.action == 'create':
            return (
                request.user.is_transport_supervisor_role or
                request.user.is_fleet_manager_role or
                request.user.is_superuser_role
            )
        
        # All authenticated users can list and retrieve (with filtering)
        return True
    
    def has_object_permission(self, request, view, obj):
        """Object-level permissions"""
        # Admins have full access
        if request.user.is_superuser_role:
            return True
        
        # Fleet Managers can view all and approve/reject
        if request.user.is_fleet_manager_role:
            return True
        
        # Transport Supervisors can only access their own inspections
        if request.user.is_transport_supervisor_role:
            return obj.supervisor == request.user
        
        return False


class PreTripInspectionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing pre-trip inspections.
    
    Provides CRUD operations with workflow management:
    - Create: Transport Supervisor only
    - Update: Transport Supervisor only (draft/rejected status only)
    - Delete: Not allowed
    - Submit: Transport Supervisor (changes status to submitted)
    - Approve: Fleet Manager (changes status to approved)
    - Reject: Fleet Manager (changes status to rejected, requires reason)
    
    Role-based filtering:
    - Transport Supervisor: only their own inspections
    - Fleet Manager: all inspections
    - Admin: all inspections
    
    Features:
    - Pagination: 25 items per page
    - Search: by inspection_id, driver name, vehicle registration
    - Filters: status, inspection_date range, driver, vehicle
    - Ordering: by inspection_date (newest first)
    """
    
    permission_classes = [InspectionPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PreTripInspectionFilter
    search_fields = ['inspection_id', 'driver__full_name', 'vehicle__registration_number', 'route']
    ordering_fields = ['inspection_date', 'created_at', 'updated_at']
    ordering = ['-inspection_date', '-created_at']
    http_method_names = ['get', 'post', 'patch', 'head', 'options']  # Disable DELETE
    
    def get_queryset(self):
        """
        Get queryset with optimizations and role-based filtering.
        """
        queryset = PreTripInspection.objects.select_related(
            'driver',
            'vehicle',
            'supervisor',
            'mechanic',
            'approved_by'
        )
        
        user = self.request.user
        
        # Role-based filtering
        if user.is_superuser_role or user.is_fleet_manager_role:
            # Admins and Fleet Managers see all inspections
            pass
        elif user.is_transport_supervisor_role:
            # Supervisors only see their own inspections
            queryset = queryset.filter(supervisor=user)
        else:
            # Other users see no inspections (shouldn't happen due to permissions)
            queryset = queryset.none()
        
        return queryset
    
    def get_serializer_class(self):
        """Use different serializers based on action"""
        if self.action == 'list':
            return InspectionListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return InspectionCreateUpdateSerializer
        elif self.action == 'retrieve':
            # Use full serializer for detailed view with all nested data
            return PreTripInspectionFullSerializer
        else:
            return InspectionDetailSerializer
    
    def perform_create(self, serializer):
        """Set the supervisor to the current user when creating an inspection"""
        # Validate user has Transport Supervisor role
        if not (
            self.request.user.is_transport_supervisor_role or
            self.request.user.is_fleet_manager_role or
            self.request.user.is_superuser_role
        ):
            raise DjangoValidationError(
                "Only Transport Supervisors can create inspections."
            )
        
        serializer.save(supervisor=self.request.user)
    
    def perform_update(self, serializer):
        """Validate that only drafts or rejected inspections can be updated"""
        instance = serializer.instance

        # Allow limited status transitions for post-trip workflow
        new_status = serializer.validated_data.get('status')
        if not instance.can_edit():
            post_trip_allowed = {
                InspectionStatus.APPROVED,
                InspectionStatus.POST_TRIP_IN_PROGRESS,
            }
            if new_status and instance.status in post_trip_allowed:
                serializer.save()
                return
            raise DjangoValidationError(
                f"Cannot edit inspection after submission. Current status: {instance.status}"
            )

        serializer.save()
    
    @action(detail=True, methods=['post'], permission_classes=[IsTransportSupervisor])
    def start_post_trip(self, request, pk=None):
        """
        Start post-trip inspection.
        Changes status from 'approved' to 'post_trip_in_progress'.
        
        POST /api/v1/inspections/{id}/start_post_trip/
        """
        inspection = self.get_object()
        
        if inspection.status not in [InspectionStatus.APPROVED, InspectionStatus.POST_TRIP_IN_PROGRESS]:
            return Response(
                {'error': f'Can only start post-trip for approved inspections. Current status: {inspection.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update status if not already in progress
        if inspection.status == InspectionStatus.APPROVED:
            inspection.status = InspectionStatus.POST_TRIP_IN_PROGRESS
            inspection.save()
        
        return Response(
            {
                'message': 'Post-trip inspection started',
                'inspection_id': inspection.inspection_id,
                'status': inspection.status,
                'post_trip_completion_info': inspection.get_post_trip_completion_status()
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsTransportSupervisor])
    def submit(self, request, pk=None):
        """
        Submit inspection for approval.
        Changes status from 'draft' to 'submitted'.
        Only Transport Supervisor who created it can submit.
        
        POST /api/v1/inspections/{id}/submit/
        """
        inspection = self.get_object()
        
        # Verify supervisor owns this inspection
        if inspection.supervisor != request.user and not request.user.is_superuser_role:
            return Response(
                {'error': 'You can only submit your own inspections.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            with transaction.atomic():
                inspection.submit_for_approval()
            
            return Response(
                {
                    'message': 'Inspection submitted for approval successfully',
                    'inspection_id': inspection.inspection_id,
                    'status': inspection.status
                },
                status=status.HTTP_200_OK
            )
        except DjangoValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsFleetManager])
    def approve(self, request, pk=None):
        """
        Approve inspection.
        Changes status from 'submitted' to 'approved'.
        Only Fleet Managers can approve.
        
        POST /api/v1/inspections/{id}/approve/
        """
        inspection = self.get_object()
        
        try:
            with transaction.atomic():
                inspection.approve(request.user)
            
            return Response(
                {
                    'message': 'Inspection approved successfully',
                    'inspection_id': inspection.inspection_id,
                    'status': inspection.status,
                    'approved_by': request.user.get_full_name(),
                    'approved_at': inspection.approval_status_updated_at
                },
                status=status.HTTP_200_OK
            )
        except DjangoValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsFleetManager])
    def reject(self, request, pk=None):
        """
        Reject inspection.
        Changes status from 'submitted' to 'rejected'.
        Only Fleet Managers can reject.
        Requires 'reason' in request body.
        
        POST /api/v1/inspections/{id}/reject/
        Body: {"reason": "Incomplete vehicle exterior checks"}
        """
        inspection = self.get_object()
        reason = request.data.get('reason', '').strip()
        
        if not reason:
            return Response(
                {'error': 'Rejection reason is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                inspection.reject(request.user, reason)
            
            return Response(
                {
                    'message': 'Inspection rejected',
                    'inspection_id': inspection.inspection_id,
                    'status': inspection.status,
                    'rejected_by': request.user.get_full_name(),
                    'rejection_reason': inspection.rejection_reason
                },
                status=status.HTTP_200_OK
            )
        except DjangoValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def download_pdf(self, request, pk=None):
        """
        Download PDF report for an inspection.
        Only approved or completed inspections can be downloaded by regular users.
        Fleet managers and admins can download any inspection.
        
        GET /api/v1/inspections/{id}/download_pdf/
        GET /api/v1/inspections/{id}/download_pdf/?approve=true (fleet managers only)
        """
        inspection = self.get_object()
        user = request.user
        
        # Check if fleet manager wants to approve first
        approve_param = request.query_params.get('approve', 'false').lower() == 'true'
        
        if approve_param:
            # Only fleet managers or superusers can approve
            if not (user.is_superuser_role or user.is_fleet_manager_role):
                return Response(
                    {"error": "Only fleet managers can approve inspections"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Only submitted inspections can be approved
            if inspection.status == InspectionStatus.SUBMITTED:
                inspection.status = InspectionStatus.APPROVED
                inspection.approved_by = user
                inspection.approval_status_updated_at = timezone.now()
                inspection.save(update_fields=['status', 'approved_by', 'approval_status_updated_at', 'updated_at'])
        
        # Permission check: only approved/completed inspections or fleet manager/admin
        allowed_statuses = [InspectionStatus.APPROVED, InspectionStatus.POST_TRIP_COMPLETED]
        if inspection.status not in allowed_statuses:
            if not (user.is_superuser_role or user.is_fleet_manager_role):
                return Response(
                    {
                        "error": "PDF can only be generated for approved inspections",
                        "requires_approval": True,
                        "can_approve": False,
                        "message": "Please contact the fleet manager to approve this inspection before downloading the PDF."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
        
        try:
            # Generate PDF
            pdf_generator = InspectionPDFGenerator()
            pdf_file = pdf_generator.generate_full_report(inspection.id)
            
            # Return as download
            response = HttpResponse(pdf_file, content_type='application/pdf')
            filename = f'inspection_{inspection.inspection_id}.pdf'
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to generate PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def download_prechecklist_pdf(self, request, pk=None):
        """
        Download Pre-Checklist PDF report for an inspection.
        Includes only pre-trip sections (Driver Info, Health/Fitness, 
        Documentation, Vehicle Checks).
        
        PDF can only be downloaded for approved inspections.
        Fleet managers can approve and download in one request by including ?approve=true
        
        GET /api/v1/inspections/{id}/download_prechecklist_pdf/
        GET /api/v1/inspections/{id}/download_prechecklist_pdf/?approve=true (fleet managers only)
        """
        inspection = self.get_object()
        user = request.user
        
        # Check if fleet manager wants to approve first
        approve_param = request.query_params.get('approve', 'false').lower() == 'true'
        
        if approve_param:
            # Only fleet managers or superusers can approve
            if not (user.is_superuser_role or user.is_fleet_manager_role):
                return Response(
                    {"error": "Only fleet managers can approve inspections"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Only submitted inspections can be approved
            if inspection.status == InspectionStatus.SUBMITTED:
                inspection.status = InspectionStatus.APPROVED
                inspection.approved_by = user
                inspection.approval_status_updated_at = timezone.now()
                inspection.save(update_fields=['status', 'approved_by', 'approval_status_updated_at', 'updated_at'])
        
        # Permission check: PDF only for approved or completed inspections
        # Fleet managers and superusers can download any status
        allowed_statuses = [InspectionStatus.APPROVED, InspectionStatus.POST_TRIP_COMPLETED]
        if inspection.status not in allowed_statuses:
            if not (user.is_superuser_role or user.is_fleet_manager_role):
                # Check if user is a fleet manager - they get a different message
                return Response(
                    {
                        "error": "Pre-checklist PDF can only be generated for approved inspections",
                        "requires_approval": True,
                        "can_approve": False,
                        "message": "Please contact the fleet manager to approve this inspection before downloading the PDF."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            else:
                # Fleet manager can still download but warn them it's not approved
                pass  # Allow the download for fleet managers
        
        try:
            # Generate Pre-Checklist PDF
            pdf_generator = InspectionPDFGenerator()
            pdf_file = pdf_generator.generate_prechecklist_report(inspection.id)
            
            # Return as download
            response = HttpResponse(pdf_file, content_type='application/pdf')
            filename = f'prechecklist_{inspection.inspection_id}.pdf'
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to generate PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """
        Get dashboard statistics for inspections.
        Returns different stats based on user role.
        
        GET /api/v1/inspections/dashboard_stats/
        """
        from ..models import RiskScoreSummary
        
        user = request.user
        
        # Filter inspections based on user role
        if user.is_transport_supervisor_role:
            inspections = PreTripInspection.objects.filter(supervisor=user)
        else:
            inspections = PreTripInspection.objects.all()
        
        # Calculate statistics
        stats = {
            'total_inspections': inspections.count(),
            'status_breakdown': {
                'draft': inspections.filter(status='draft').count(),
                'submitted': inspections.filter(status='submitted').count(),
                'approved': inspections.filter(status='approved').count(),
                'rejected': inspections.filter(status='rejected').count(),
            },
            'high_risk_drivers': RiskScoreSummary.objects.filter(
                risk_level='high'
            ).count(),
            'medium_risk_drivers': RiskScoreSummary.objects.filter(
                risk_level='medium'
            ).count(),
        }
        
        # Add pending approvals count for fleet managers
        if user.is_fleet_manager_role or user.is_superuser_role:
            stats['pending_approvals'] = PreTripInspection.objects.filter(
                status='submitted'
            ).count()
        
        # Add recent inspections (last 7 days)
        from datetime import timedelta
        from django.utils import timezone
        
        seven_days_ago = timezone.now() - timedelta(days=7)
        stats['recent_inspections'] = {
            'last_7_days': inspections.filter(
                created_at__gte=seven_days_ago
            ).count(),
            'approved_last_7_days': inspections.filter(
                status='approved',
                approval_status_updated_at__gte=seven_days_ago
            ).count(),
        }
        
        # Add critical failures count
        from ..models import (
            VehicleExteriorCheck,
            EngineFluidCheck,
            InteriorCabinCheck,
            FunctionalCheck,
            SafetyEquipmentCheck
        )
        
        critical_failures = 0
        for model in [VehicleExteriorCheck, EngineFluidCheck, InteriorCabinCheck, 
                      FunctionalCheck, SafetyEquipmentCheck]:
            critical_failures += model.objects.filter(
                status='fail',
                is_critical_failure=True,
                inspection__in=inspections
            ).count()
        
        stats['critical_failures'] = critical_failures
        
        return Response(stats)
