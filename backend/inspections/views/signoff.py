from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.exceptions import ValidationError as DjangoValidationError

from ..models import InspectionSignOff, PreTripInspection
from ..serializers import InspectionSignOffSerializer


class InspectionSignOffViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Inspection Sign-Offs.
    
    Sign-offs are immutable once created (CREATE only).
    Each inspection can have one sign-off per role (driver, supervisor, mechanic).
    """
    
    serializer_class = InspectionSignOffSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'options']  # CREATE and LIST only
    
    def get_queryset(self):
        """Get sign-offs for the current user's accessible inspections"""
        user = self.request.user
        
        # Get the inspection ID from the URL if nested routing is used
        inspection_id = self.kwargs.get('inspection_pk')
        
        if inspection_id:
            queryset = InspectionSignOff.objects.filter(
                inspection__id=inspection_id
            ).select_related('inspection')
        else:
            queryset = InspectionSignOff.objects.select_related('inspection')
        
        # Apply role-based filtering
        if user.is_superuser_role or user.is_fleet_manager_role:
            pass
        elif user.is_transport_supervisor_role:
            queryset = queryset.filter(inspection__supervisor=user)
        else:
            queryset = queryset.none()
        
        return queryset
    
    def perform_create(self, serializer):
        """Create sign-off for the specified inspection"""
        inspection_id = self.kwargs.get('inspection_pk')
        
        if not inspection_id:
            raise DjangoValidationError("Inspection ID is required")
        
        try:
            inspection = PreTripInspection.objects.get(id=inspection_id)
        except PreTripInspection.DoesNotExist:
            raise DjangoValidationError("Inspection not found")
        
        # Validate user has permission (supervisor creates all sign-offs)
        user = self.request.user
        if not (user.is_superuser_role or user.is_fleet_manager_role):
            if user.is_transport_supervisor_role and inspection.supervisor != user:
                raise DjangoValidationError("You can only create sign-offs for your own inspections")
        
        # Pass inspection to serializer context for validation
        serializer.context['inspection'] = inspection
        serializer.save(inspection=inspection)
    
    def create(self, request, *args, **kwargs):
        """Override create to provide better error messages"""
        try:
            return super().create(request, *args, **kwargs)
        except DjangoValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
