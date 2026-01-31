from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction

from ..models import (
    PreTripInspection,
    VehicleExteriorCheck,
    EngineFluidCheck,
    InteriorCabinCheck,
    FunctionalCheck,
    SafetyEquipmentCheck,
    BrakesSteeringCheck,
)
from ..serializers import (
    VehicleExteriorCheckSerializer,
    EngineFluidCheckSerializer,
    InteriorCabinCheckSerializer,
    FunctionalCheckSerializer,
    SafetyEquipmentCheckSerializer,
    BrakesSteeringCheckSerializer,
)


class BaseVehicleCheckViewSet(viewsets.ModelViewSet):
    """Base ViewSet for all vehicle check types with common functionality"""
    
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'put', 'delete', 'head', 'options']
    
    def get_queryset(self):
        """Get checks for the current user's accessible inspections"""
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
            # Supervisors only see checks for their inspections
            queryset = queryset.filter(inspection__supervisor=user)
        else:
            # Other users see nothing
            queryset = queryset.none()
        
        return queryset
    
    def perform_create(self, serializer):
        """Create check for the specified inspection"""
        # Get inspection ID from URL
        inspection_id = self.kwargs.get('inspection_pk')
        
        if not inspection_id:
            raise DjangoValidationError("Inspection ID is required")
        
        try:
            inspection = PreTripInspection.objects.get(id=inspection_id)
        except PreTripInspection.DoesNotExist:
            raise DjangoValidationError("Inspection not found")
        
        # Validate user has permission to create checks for this inspection
        user = self.request.user
        if not (user.is_superuser_role or user.is_fleet_manager_role):
            if user.is_transport_supervisor_role and inspection.supervisor != user:
                raise DjangoValidationError("You can only create checks for your own inspections")
        
        # Validate inspection is editable
        if not inspection.can_edit():
            raise DjangoValidationError(
                f"Cannot create checks for inspection with status: {inspection.status}"
            )
        
        serializer.save(inspection=inspection)
    
    def perform_update(self, serializer):
        """Validate inspection is editable before updating check"""
        instance = serializer.instance
        
        if not instance.inspection.can_edit():
            raise DjangoValidationError(
                f"Cannot edit check. Inspection status: {instance.inspection.status}"
            )
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """Validate inspection is editable before deleting check"""
        if not instance.inspection.can_edit():
            raise DjangoValidationError(
                f"Cannot delete check. Inspection status: {instance.inspection.status}"
            )
        
        instance.delete()
    
    @action(detail=False, methods=['post'], url_path='bulk-create')
    def bulk_create(self, request, inspection_pk=None):
        """
        Bulk create multiple checks at once.
        
        POST /api/v1/inspections/{id}/exterior-checks/bulk-create/
        Body: {
            "checks": [
                {"check_item": "tires", "status": "pass", "remarks": ""},
                {"check_item": "lights", "status": "pass", "remarks": ""}
            ]
        }
        """
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
                    {'error': 'You can only create checks for your own inspections'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Validate inspection is editable
        if not inspection.can_edit():
            return Response(
                {'error': f'Cannot create checks for inspection with status: {inspection.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        checks_data = request.data.get('checks', [])
        
        if not checks_data:
            return Response(
                {'error': 'No checks provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_checks = []
        errors = []
        
        with transaction.atomic():
            for idx, check_data in enumerate(checks_data):
                serializer = self.get_serializer(data=check_data)
                if serializer.is_valid():
                    serializer.save(inspection=inspection)
                    created_checks.append(serializer.data)
                else:
                    errors.append({
                        'index': idx,
                        'check_item': check_data.get('check_item'),
                        'errors': serializer.errors
                    })
        
        if errors:
            return Response(
                {
                    'error': 'Some checks could not be created',
                    'created_count': len(created_checks),
                    'failed_count': len(errors),
                    'errors': errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(
            {
                'message': f'Successfully created {len(created_checks)} checks',
                'count': len(created_checks),
                'checks': created_checks
            },
            status=status.HTTP_201_CREATED
        )


class VehicleExteriorCheckViewSet(BaseVehicleCheckViewSet):
    """ViewSet for Vehicle Exterior Checks"""
    serializer_class = VehicleExteriorCheckSerializer


class EngineFluidCheckViewSet(BaseVehicleCheckViewSet):
    """ViewSet for Engine & Fluid Checks"""
    serializer_class = EngineFluidCheckSerializer


class InteriorCabinCheckViewSet(BaseVehicleCheckViewSet):
    """ViewSet for Interior & Cabin Checks"""
    serializer_class = InteriorCabinCheckSerializer


class FunctionalCheckViewSet(BaseVehicleCheckViewSet):
    """ViewSet for Functional Checks"""
    serializer_class = FunctionalCheckSerializer


class SafetyEquipmentCheckViewSet(BaseVehicleCheckViewSet):
    """ViewSet for Safety Equipment Checks"""
    serializer_class = SafetyEquipmentCheckSerializer


class BrakesSteeringCheckViewSet(BaseVehicleCheckViewSet):
    """ViewSet for Brakes & Steering Checks"""
    serializer_class = BrakesSteeringCheckSerializer
