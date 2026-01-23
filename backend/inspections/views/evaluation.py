from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError as DjangoValidationError

from ..models import SupervisorRemarks, EvaluationSummary, PreTripInspection
from ..serializers import SupervisorRemarksSerializer, EvaluationSummarySerializer


class SupervisorRemarksViewSet(viewsets.ModelViewSet):
    """ViewSet for Supervisor Remarks"""
    
    serializer_class = SupervisorRemarksSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'put', 'head', 'options']  # Disable DELETE
    
    def get_queryset(self):
        """Get supervisor remarks for the current user's accessible inspections"""
        user = self.request.user
        
        # Get the inspection ID from the URL if nested routing is used
        inspection_id = self.kwargs.get('inspection_pk')
        
        if inspection_id:
            queryset = SupervisorRemarks.objects.filter(
                inspection__id=inspection_id
            ).select_related('inspection')
        else:
            queryset = SupervisorRemarks.objects.select_related('inspection')
        
        # Apply role-based filtering
        if user.is_superuser_role or user.is_fleet_manager_role:
            pass
        elif user.is_transport_supervisor_role:
            queryset = queryset.filter(inspection__supervisor=user)
        else:
            queryset = queryset.none()
        
        return queryset
    
    def perform_create(self, serializer):
        """Create supervisor remarks for the specified inspection"""
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
                raise DjangoValidationError("You can only create remarks for your own inspections")
        
        serializer.save(inspection=inspection)
    
    def perform_update(self, serializer):
        """Update supervisor remarks"""
        serializer.save()


class EvaluationSummaryViewSet(viewsets.ModelViewSet):
    """ViewSet for Evaluation Summaries"""
    
    serializer_class = EvaluationSummarySerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'put', 'head', 'options']  # Disable DELETE
    
    def get_queryset(self):
        """Get evaluation summaries for the current user's accessible inspections"""
        user = self.request.user
        
        # Get the inspection ID from the URL if nested routing is used
        inspection_id = self.kwargs.get('inspection_pk')
        
        if inspection_id:
            queryset = EvaluationSummary.objects.filter(
                inspection__id=inspection_id
            ).select_related('inspection')
        else:
            queryset = EvaluationSummary.objects.select_related('inspection')
        
        # Apply role-based filtering
        if user.is_superuser_role or user.is_fleet_manager_role:
            pass
        elif user.is_transport_supervisor_role:
            queryset = queryset.filter(inspection__supervisor=user)
        else:
            queryset = queryset.none()
        
        return queryset
    
    def perform_create(self, serializer):
        """Create evaluation summary for the specified inspection"""
        inspection_id = self.kwargs.get('inspection_pk')
        
        if not inspection_id:
            raise DjangoValidationError("Inspection ID is required")
        
        try:
            inspection = PreTripInspection.objects.get(id=inspection_id)
        except PreTripInspection.DoesNotExist:
            raise DjangoValidationError("Inspection not found")
        
        # Validate user has permission (typically supervisor or fleet manager)
        user = self.request.user
        if not (user.is_superuser_role or user.is_fleet_manager_role):
            if user.is_transport_supervisor_role and inspection.supervisor != user:
                raise DjangoValidationError("You can only create evaluations for your own inspections")
        
        serializer.save(inspection=inspection)
    
    def perform_update(self, serializer):
        """Update evaluation summary (will auto-recalculate overall performance)"""
        serializer.save()
