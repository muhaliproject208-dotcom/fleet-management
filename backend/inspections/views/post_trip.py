from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError as DjangoValidationError

from ..models import PostTripReport, RiskScoreSummary, PreTripInspection
from ..serializers import PostTripReportSerializer, RiskScoreSummarySerializer


class PostTripReportViewSet(viewsets.ModelViewSet):
    """ViewSet for Post-Trip Reports"""
    
    serializer_class = PostTripReportSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'put', 'head', 'options']  # Disable DELETE
    
    def get_queryset(self):
        """Get post-trip reports for the current user's accessible inspections"""
        user = self.request.user
        
        # Get the inspection ID from the URL if nested routing is used
        inspection_id = self.kwargs.get('inspection_pk')
        
        if inspection_id:
            queryset = PostTripReport.objects.filter(
                inspection__id=inspection_id
            ).select_related('inspection')
        else:
            queryset = PostTripReport.objects.select_related('inspection')
        
        # Apply role-based filtering
        if user.is_superuser_role or user.is_fleet_manager_role:
            pass
        elif user.is_transport_supervisor_role:
            queryset = queryset.filter(inspection__supervisor=user)
        else:
            queryset = queryset.none()
        
        return queryset
    
    def perform_create(self, serializer):
        """Create post-trip report for the specified inspection"""
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
                raise DjangoValidationError("You can only create post-trip reports for your own inspections")
        
        serializer.save(inspection=inspection)
    
    def perform_update(self, serializer):
        """Update post-trip report"""
        serializer.save()


class RiskScoreSummaryViewSet(viewsets.ModelViewSet):
    """ViewSet for Risk Score Summaries"""
    
    serializer_class = RiskScoreSummarySerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'put', 'head', 'options']  # Disable DELETE
    
    def get_queryset(self):
        """Get risk scores for the current user's accessible inspections"""
        user = self.request.user
        
        # Get the inspection ID from the URL if nested routing is used
        inspection_id = self.kwargs.get('inspection_pk')
        
        if inspection_id:
            queryset = RiskScoreSummary.objects.filter(
                inspection__id=inspection_id
            ).select_related('inspection')
        else:
            queryset = RiskScoreSummary.objects.select_related('inspection')
        
        # Apply role-based filtering
        if user.is_superuser_role or user.is_fleet_manager_role:
            pass
        elif user.is_transport_supervisor_role:
            queryset = queryset.filter(inspection__supervisor=user)
        else:
            queryset = queryset.none()
        
        return queryset
    
    def perform_create(self, serializer):
        """Create risk score for the specified inspection"""
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
                raise DjangoValidationError("You can only create risk scores for your own inspections")
        
        serializer.save(inspection=inspection)
    
    def perform_update(self, serializer):
        """Update risk score (will auto-recalculate)"""
        serializer.save()
