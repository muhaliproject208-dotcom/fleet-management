from rest_framework import serializers
from ..models import DocumentationCompliance


class DocumentationComplianceSerializer(serializers.ModelSerializer):
    """Serializer for Documentation & Compliance Check"""
    
    class Meta:
        model = DocumentationCompliance
        fields = [
            'id',
            'inspection',
            'certificate_of_fitness',
            'road_tax_valid',
            'insurance_valid',
            'trip_authorization_signed',
            'logbook_present',
            'driver_handbook_present',
            'permits_valid',
            'ppe_available',
            'route_familiarity',
            'emergency_procedures_known',
            'gps_activated',
            'safety_briefing_provided',
            'rtsa_clearance',
            'emergency_contact',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'inspection', 'created_at', 'updated_at']
    
    def validate(self, attrs):
        """Validate that all required documents are provided"""
        # Get values from attrs or instance if updating
        cert_fitness = attrs.get('certificate_of_fitness')
        if not cert_fitness and self.instance:
            cert_fitness = self.instance.certificate_of_fitness
        
        road_tax = attrs.get('road_tax_valid')
        if road_tax is None and self.instance:
            road_tax = self.instance.road_tax_valid
        
        insurance = attrs.get('insurance_valid')
        if insurance is None and self.instance:
            insurance = self.instance.insurance_valid
        
        trip_auth = attrs.get('trip_authorization_signed')
        if trip_auth is None and self.instance:
            trip_auth = self.instance.trip_authorization_signed
        
        logbook = attrs.get('logbook_present')
        if logbook is None and self.instance:
            logbook = self.instance.logbook_present
        
        # Validate required documents
        missing = []
        
        if cert_fitness != 'valid':
            missing.append('Certificate of Fitness must be valid')
        if not road_tax:
            missing.append('Road Tax must be valid')
        if not insurance:
            missing.append('Insurance must be valid')
        if not trip_auth:
            missing.append('Trip Authorization must be signed')
        if not logbook:
            missing.append('Logbook must be present')
        
        if missing:
            raise serializers.ValidationError({
                'error': f'Missing required documents: {", ".join(missing)}'
            })
        
        return attrs
