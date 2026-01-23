from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.http import HttpResponse

from ..models import PreTripInspection, InspectionStatus
from ..serializers import (
    InspectionListSerializer,
    InspectionDetailSerializer,
    InspectionCreateUpdateSerializer
)
from ..pdf_generator import InspectionPDFGenerator
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
    filterset_fields = ['status', 'driver', 'vehicle', 'inspection_date']
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
        
        if not instance.can_edit():
            raise DjangoValidationError(
                f"Cannot edit inspection after submission. Current status: {instance.status}"
            )
        
        serializer.save()
    
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
        Only approved inspections can be downloaded by regular users.
        Fleet managers and admins can download any inspection.
        
        GET /api/v1/inspections/{id}/download_pdf/
        """
        inspection = self.get_object()
        user = request.user
        
        # Permission check: only approved inspections or fleet manager/admin
        if inspection.status != 'approved':
            if not (user.is_superuser_role or user.is_fleet_manager_role):
                return Response(
                    {"error": "Only approved inspections can be downloaded"},
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
