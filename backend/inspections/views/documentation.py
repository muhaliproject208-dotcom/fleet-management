from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError as DjangoValidationError

from ..models import DocumentationCompliance, PreTripInspection
from ..serializers import DocumentationComplianceSerializer


class DocumentationComplianceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Documentation & Compliance Checks.
    
    Provides CRUD operations for documentation compliance:
    - Create: Create documentation check for an inspection
    - Retrieve: Get documentation details
    - Update: Update documentation (only if inspection is editable)
    - Delete: Not allowed
    
    Features:
    - Nested under inspections (accessed via /api/v1/inspections/{id}/documentation/)
    - Validates inspection is editable before updates
    - OneToOne relationship with PreTripInspection
    """
    
    serializer_class = DocumentationComplianceSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'put', 'head', 'options']  # Disable DELETE
    
    def get_queryset(self):
        """Get documentation checks for the current user's accessible inspections"""
        user = self.request.user
        
        # Get the inspection ID from the URL if nested routing is used
        inspection_id = self.kwargs.get('inspection_pk')
        
        if inspection_id:
            # Filter by specific inspection
            queryset = DocumentationCompliance.objects.filter(
                inspection__id=inspection_id
            ).select_related('inspection')
        else:
            # Get all documentation checks for accessible inspections
            queryset = DocumentationCompliance.objects.select_related('inspection')
        
        # Apply role-based filtering
        if user.is_superuser_role or user.is_fleet_manager_role:
            # Admins and Fleet Managers see all
            pass
        elif user.is_transport_supervisor_role:
            # Supervisors only see documentation for their inspections
            queryset = queryset.filter(inspection__supervisor=user)
        else:
            # Other users see nothing
            queryset = queryset.none()
        
        return queryset
    
    def perform_create(self, serializer):
        """Create documentation check for the specified inspection"""
        # Get inspection ID from URL
        inspection_id = self.kwargs.get('inspection_pk')
        
        if not inspection_id:
            raise DjangoValidationError("Inspection ID is required")
        
        try:
            inspection = PreTripInspection.objects.get(id=inspection_id)
        except PreTripInspection.DoesNotExist:
            raise DjangoValidationError("Inspection not found")
        
        # Validate user has permission to create documentation for this inspection
        user = self.request.user
        if not (user.is_superuser_role or user.is_fleet_manager_role):
            if user.is_transport_supervisor_role and inspection.supervisor != user:
                raise DjangoValidationError("You can only create documentation for your own inspections")
        
        # Validate inspection is editable
        if not inspection.can_edit():
            raise DjangoValidationError(
                f"Cannot create documentation for inspection with status: {inspection.status}"
            )
        
        serializer.save(inspection=inspection)
    
    def perform_update(self, serializer):
        """Validate inspection is editable before updating documentation"""
        instance = serializer.instance
        
        if not instance.inspection.can_edit():
            raise DjangoValidationError(
                f"Cannot edit documentation. Inspection status: {instance.inspection.status}"
            )
        
        serializer.save()
