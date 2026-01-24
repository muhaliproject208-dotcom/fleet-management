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
    
    def create(self, request, *args, **kwargs):
        """Create or update post-trip report (upsert behavior)"""
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
        
        # Validate user has permission
        user = request.user
        if not (user.is_superuser_role or user.is_fleet_manager_role):
            if user.is_transport_supervisor_role and inspection.supervisor != user:
                return Response(
                    {'error': 'You can only create post-trip reports for your own inspections'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Check if report already exists - update instead of create
        try:
            existing_report = PostTripReport.objects.get(inspection=inspection)
            serializer = self.get_serializer(existing_report, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PostTripReport.DoesNotExist:
            # Create new report
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(inspection=inspection)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
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
    
    def create(self, request, *args, **kwargs):
        """Create or update risk score (upsert behavior) - auto-calculates from trip behaviors"""
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
        
        # Validate user has permission
        user = request.user
        if not (user.is_superuser_role or user.is_fleet_manager_role):
            if user.is_transport_supervisor_role and inspection.supervisor != user:
                return Response(
                    {'error': 'You can only create risk scores for your own inspections'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Check if risk score already exists - update instead of create
        try:
            existing_score = RiskScoreSummary.objects.get(inspection=inspection)
            # Trigger recalculation by saving
            existing_score.save()
            serializer = self.get_serializer(existing_score)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except RiskScoreSummary.DoesNotExist:
            # Create new risk score - it will auto-calculate on save
            risk_score = RiskScoreSummary(inspection=inspection)
            risk_score.save()
            serializer = self.get_serializer(risk_score)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def perform_update(self, serializer):
        """Update risk score (will auto-recalculate)"""
        serializer.save()
