from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError as DjangoValidationError

from ..models import (
    PreTripInspection,
    CorrectiveMeasure,
    EnforcementAction,
)
from ..serializers import (
    CorrectiveMeasureSerializer,
    EnforcementActionSerializer,
)


class BaseEnforcementViewSet(viewsets.ModelViewSet):
    """Base ViewSet for enforcement-related records"""
    
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'put', 'delete', 'head', 'options']
    
    def get_queryset(self):
        """Get records for the current user's accessible inspections"""
        user = self.request.user
        
        # Get the inspection ID from the URL if nested routing is used
        inspection_id = self.kwargs.get('inspection_pk')
        
        # Start with base queryset
        queryset = self.serializer_class.Meta.model.objects.select_related('inspection')
        
        if inspection_id:
            # Filter by specific inspection
            queryset = queryset.filter(inspection__id=inspection_id)
        
        # Apply role-based filtering
        if user.is_superuser_role or user.is_fleet_manager_role:
            # Admins and Fleet Managers see all
            pass
        elif user.is_transport_supervisor_role:
            # Supervisors only see records for their inspections
            queryset = queryset.filter(inspection__supervisor=user)
        else:
            # Other users see nothing
            queryset = queryset.none()
        
        return queryset
    
    def perform_create(self, serializer):
        """Create record for the specified inspection"""
        # Get inspection ID from URL
        inspection_id = self.kwargs.get('inspection_pk')
        
        if not inspection_id:
            raise DjangoValidationError("Inspection ID is required")
        
        try:
            inspection = PreTripInspection.objects.get(id=inspection_id)
        except PreTripInspection.DoesNotExist:
            raise DjangoValidationError("Inspection not found")
        
        # Validate user has permission (typically Fleet Manager or Supervisor)
        user = self.request.user
        if not (user.is_superuser_role or user.is_fleet_manager_role):
            if user.is_transport_supervisor_role and inspection.supervisor != user:
                raise DjangoValidationError("You can only create records for your own inspections")
        
        serializer.save(inspection=inspection)
    
    def perform_update(self, serializer):
        """Update record"""
        serializer.save()
    
    def perform_destroy(self, instance):
        """Delete record"""
        instance.delete()


class CorrectiveMeasureViewSet(BaseEnforcementViewSet):
    """ViewSet for Corrective Measures"""
    serializer_class = CorrectiveMeasureSerializer


class EnforcementActionViewSet(BaseEnforcementViewSet):
    """ViewSet for Enforcement Actions"""
    serializer_class = EnforcementActionSerializer
