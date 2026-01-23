from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction

from ..models import (
    PreTripInspection,
    TripBehaviorMonitoring,
    DrivingBehaviorCheck,
)
from ..serializers import (
    TripBehaviorMonitoringSerializer,
    DrivingBehaviorCheckSerializer,
)


class BaseBehaviorViewSet(viewsets.ModelViewSet):
    """Base ViewSet for behavior monitoring with common functionality"""
    
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'put', 'delete', 'head', 'options']
    
    def get_queryset(self):
        """Get behaviors for the current user's accessible inspections"""
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
            # Supervisors only see behaviors for their inspections
            queryset = queryset.filter(inspection__supervisor=user)
        else:
            # Other users see nothing
            queryset = queryset.none()
        
        return queryset
    
    def perform_create(self, serializer):
        """Create behavior for the specified inspection"""
        # Get inspection ID from URL
        inspection_id = self.kwargs.get('inspection_pk')
        
        if not inspection_id:
            raise DjangoValidationError("Inspection ID is required")
        
        try:
            inspection = PreTripInspection.objects.get(id=inspection_id)
        except PreTripInspection.DoesNotExist:
            raise DjangoValidationError("Inspection not found")
        
        # Validate user has permission
        user = self.request.user
        if not (user.is_superuser_role or user.is_fleet_manager_role):
            if user.is_transport_supervisor_role and inspection.supervisor != user:
                raise DjangoValidationError("You can only create behaviors for your own inspections")
        
        # Validate inspection is editable
        if not inspection.can_edit():
            raise DjangoValidationError(
                f"Cannot create behaviors for inspection with status: {inspection.status}"
            )
        
        serializer.save(inspection=inspection)
    
    def perform_update(self, serializer):
        """Validate inspection is editable before updating"""
        instance = serializer.instance
        
        if not instance.inspection.can_edit():
            raise DjangoValidationError(
                f"Cannot edit behavior. Inspection status: {instance.inspection.status}"
            )
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """Validate inspection is editable before deleting"""
        if not instance.inspection.can_edit():
            raise DjangoValidationError(
                f"Cannot delete behavior. Inspection status: {instance.inspection.status}"
            )
        
        instance.delete()
    
    @action(detail=False, methods=['post'], url_path='bulk-create')
    def bulk_create(self, request, inspection_pk=None):
        """Bulk create multiple behaviors at once"""
        if not inspection_pk:
            return Response(
                {'error': 'Inspection ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            inspection = PreTripInspection.objects.get(id=inspection_pk)
        except PreTripInspection.DoesNotExist:
            return Response(
                {'error': 'Inspection not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Validate user has permission
        user = request.user
        if not (user.is_superuser_role or user.is_fleet_manager_role):
            if user.is_transport_supervisor_role and inspection.supervisor != user:
                return Response(
                    {'error': 'You can only create behaviors for your own inspections'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Validate inspection is editable
        if not inspection.can_edit():
            return Response(
                {'error': f'Cannot create behaviors for inspection with status: {inspection.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        behaviors_data = request.data.get('behaviors', [])
        
        if not behaviors_data:
            return Response(
                {'error': 'No behaviors provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_behaviors = []
        errors = []
        
        with transaction.atomic():
            for idx, behavior_data in enumerate(behaviors_data):
                serializer = self.get_serializer(data=behavior_data)
                if serializer.is_valid():
                    serializer.save(inspection=inspection)
                    created_behaviors.append(serializer.data)
                else:
                    errors.append({
                        'index': idx,
                        'behavior_item': behavior_data.get('behavior_item'),
                        'errors': serializer.errors
                    })
        
        if errors:
            return Response(
                {
                    'error': 'Some behaviors could not be created',
                    'created_count': len(created_behaviors),
                    'failed_count': len(errors),
                    'errors': errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(
            {
                'message': f'Successfully created {len(created_behaviors)} behaviors',
                'count': len(created_behaviors),
                'behaviors': created_behaviors
            },
            status=status.HTTP_201_CREATED
        )


class TripBehaviorMonitoringViewSet(BaseBehaviorViewSet):
    """ViewSet for Trip Behavior Monitoring"""
    serializer_class = TripBehaviorMonitoringSerializer


class DrivingBehaviorCheckViewSet(BaseBehaviorViewSet):
    """ViewSet for Driving Behavior Checks"""
    serializer_class = DrivingBehaviorCheckSerializer
