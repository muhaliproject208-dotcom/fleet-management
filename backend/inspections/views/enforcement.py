from rest_framework import viewsets, status
from rest_framework.response import Response
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
    
    # Override this in subclasses to specify which field to use for upsert
    upsert_field = None
    
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
    
    def create(self, request, *args, **kwargs):
        """Create or update record (upsert behavior based on type field)"""
        inspection_id = self.kwargs.get('inspection_pk')
        
        if not inspection_id:
            return Response(
                {'error': 'Inspection ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            inspection = PreTripInspection.objects.get(id=inspection_id)
        except PreTripInspection.DoesNotExist:
            return Response(
                {'error': 'Inspection not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Validate user has permission (typically Fleet Manager or Supervisor)
        user = request.user
        if not (user.is_superuser_role or user.is_fleet_manager_role):
            if user.is_transport_supervisor_role and inspection.supervisor != user:
                return Response(
                    {'error': 'You can only create records for your own inspections'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Check if record already exists for this inspection and type field - update if so
        model = self.serializer_class.Meta.model
        
        if self.upsert_field:
            type_value = request.data.get(self.upsert_field)
            if type_value:
                try:
                    existing = model.objects.get(inspection=inspection, **{self.upsert_field: type_value})
                    serializer = self.get_serializer(existing, data=request.data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                except model.DoesNotExist:
                    pass
        
        # Create new record
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(inspection=inspection)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def perform_update(self, serializer):
        """Update record"""
        serializer.save()
    
    def perform_destroy(self, instance):
        """Delete record"""
        instance.delete()


class CorrectiveMeasureViewSet(BaseEnforcementViewSet):
    """ViewSet for Corrective Measures"""
    serializer_class = CorrectiveMeasureSerializer
    upsert_field = 'measure_type'


class EnforcementActionViewSet(BaseEnforcementViewSet):
    """ViewSet for Enforcement Actions"""
    serializer_class = EnforcementActionSerializer
    upsert_field = 'action_type'
