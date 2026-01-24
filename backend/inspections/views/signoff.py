from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.exceptions import ValidationError as DjangoValidationError

from ..models import InspectionSignOff, PreTripInspection
from ..serializers import InspectionSignOffSerializer


class InspectionSignOffViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Inspection Sign-Offs.
    
    Sign-offs support upsert - if a sign-off for the same role exists, it updates.
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
    
    def create(self, request, *args, **kwargs):
        """Create or update sign-off (upsert behavior based on role)"""
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
        
        # Validate user has permission (supervisor creates all sign-offs)
        user = request.user
        if not (user.is_superuser_role or user.is_fleet_manager_role):
            if user.is_transport_supervisor_role and inspection.supervisor != user:
                return Response(
                    {'error': 'You can only create sign-offs for your own inspections'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        role = request.data.get('role')
        
        # Check if sign-off already exists for this role - update if so
        try:
            existing = InspectionSignOff.objects.get(inspection=inspection, role=role)
            serializer = self.get_serializer(existing, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            # Check and update post-trip completion status
            inspection.check_and_update_post_trip_status()
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        except InspectionSignOff.DoesNotExist:
            # Create new sign-off
            serializer = self.get_serializer(data=request.data)
            serializer.context['inspection'] = inspection
            serializer.is_valid(raise_exception=True)
            serializer.save(inspection=inspection)
            
            # Check and update post-trip completion status
            inspection.check_and_update_post_trip_status()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
