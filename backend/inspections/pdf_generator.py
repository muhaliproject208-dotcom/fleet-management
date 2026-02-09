"""
PDF Report Generator for Pre-Trip Inspections
Generates comprehensive inspection reports with all sections and signature placeholders.
"""

from io import BytesIO
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, Image
)
from reportlab.pdfgen import canvas

from .models import (
    PreTripInspection,
    HealthFitnessCheck,
    DocumentationCompliance,
    VehicleExteriorCheck,
    EngineFluidCheck,
    InteriorCabinCheck,
    FunctionalCheck,
    SafetyEquipmentCheck,
    BrakesSteeringCheck,
    TripBehaviorMonitoring,
    DrivingBehaviorCheck,
    PostTripReport,
    RiskScoreSummary,
    CorrectiveMeasure,
    EnforcementAction,
    SupervisorRemarks,
    EvaluationSummary,
    InspectionSignOff,
    PreTripScoreSummary,
    PostChecklistScoreSummary,
    FinalScoreSummary,
    RiskStatus,
    FinalRiskLevel,
    FinalStatus,
    SCORE_PER_QUESTION,
)


class NumberedCanvas(canvas.Canvas):
    """Custom canvas for adding page numbers and watermarks"""
    
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
        self.watermark_text = None
    
    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()
    
    def save(self):
        """Add page numbers and watermarks to all pages"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            if self.watermark_text:
                self.draw_watermark(self.watermark_text)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
    
    def draw_page_number(self, page_count):
        """Add page numbers to footer"""
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.grey)
        page_num = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(7.5 * inch, 0.5 * inch, page_num)
        
        # Add timestamp
        timestamp = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        self.drawString(1 * inch, 0.5 * inch, timestamp)
    
    def draw_watermark(self, text):
        """Add watermark for draft/rejected inspections"""
        self.saveState()
        self.setFont("Helvetica-Bold", 60)
        self.setFillColor(colors.red, alpha=0.1)
        self.translate(4.25 * inch, 5.5 * inch)
        self.rotate(45)
        self.drawCentredString(0, 0, text.upper())
        self.restoreState()


class InspectionPDFGenerator:
    """Generate PDF reports for pre-trip inspections"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        self.story = []
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c5aa0'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='SubSection',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#333333'),
            spaceAfter=8,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        ))
    
    def generate_header(self, inspection):
        """Generate document header with company info and form details"""
        # Title
        title = Paragraph("PRE-TRIP INSPECTION REPORT", self.styles['CustomTitle'])
        self.story.append(title)
        
        # Form details table
        form_data = [
            ['Form Code:', 'LMP-FSM-PTI/03', 'Version:', '1.0'],
            ['Inspection ID:', str(inspection.inspection_id), 'Status:', inspection.get_status_display().upper()],
        ]
        
        form_table = Table(form_data, colWidths=[1.5*inch, 2*inch, 1.2*inch, 1.8*inch])
        form_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 9),
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 9),
            ('FONT', (2, 0), (2, -1), 'Helvetica-Bold', 9),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('TEXTCOLOR', (1, 1), (1, 1), colors.HexColor('#2c5aa0')),
            ('FONTNAME', (1, 1), (1, 1), 'Helvetica-Bold'),
        ]))
        
        self.story.append(form_table)
        self.story.append(Spacer(1, 0.3*inch))
    
    def generate_driver_trip_info(self, inspection):
        """Section 1: Driver and Trip Information"""
        section = Paragraph("1. DRIVER & TRIP INFORMATION", self.styles['SectionHeader'])
        self.story.append(section)
        
        data = [
            ['Driver:', inspection.driver.full_name, 'License:', inspection.driver.license_number],
            ['Vehicle:', f"{inspection.vehicle.registration_number} - {inspection.vehicle.vehicle_type}", 'Vehicle ID:', inspection.vehicle.vehicle_id],
              ['Route:', inspection.route or 'N/A', 'Inspection Date:', inspection.inspection_date.strftime('%Y-%m-%d')],
              ['Planned Departure:', getattr(inspection, 'planned_departure_time', None).strftime('%H:%M') if getattr(inspection, 'planned_departure_time', None) else 'N/A',
               'Actual Departure:', getattr(inspection, 'actual_departure_time', None).strftime('%H:%M') if getattr(inspection, 'actual_departure_time', None) else 'N/A'],
        ]
        
        if inspection.supervisor:
            data.append(['Supervisor:', inspection.supervisor.get_full_name(), '', ''])
        
        table = Table(data, colWidths=[1.3*inch, 2.5*inch, 1.2*inch, 1.5*inch])
        table.setStyle(self._get_info_table_style())
        self.story.append(table)
        self.story.append(Spacer(1, 0.2*inch))
    
    def generate_health_fitness(self, inspection):
        """Section 2: Health & Fitness Check with Scoring"""
        try:
            health_fitness = HealthFitnessCheck.objects.get(inspection=inspection)
        except HealthFitnessCheck.DoesNotExist:
            return
        
        section = Paragraph("2. HEALTH & FITNESS CHECK", self.styles['SectionHeader'])
        self.story.append(section)
        
        # Get score information
        earned, max_score, percentage = health_fitness.calculate_score()
        is_cleared = health_fitness.is_travel_cleared()
        clearance_msg = health_fitness.get_clearance_message()
        
        # Clearance Status Banner
        if is_cleared:
            clearance_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#90EE90')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#006400')),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ])
        else:
            clearance_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FF6B6B')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ])
        
        clearance_table = Table([[clearance_msg]], colWidths=[6.5*inch])
        clearance_table.setStyle(clearance_style)
        self.story.append(clearance_table)
        self.story.append(Spacer(1, 0.15*inch))
        
        # Score Summary Box
        score_color = colors.HexColor('#90EE90') if percentage >= 80 else (colors.HexColor('#FFD700') if percentage >= 60 else colors.HexColor('#FF6B6B'))
        score_data = [
            ['HEALTH & FITNESS SCORE', f'{earned} / {max_score} points ({percentage}%)']
        ]
        score_table = Table(score_data, colWidths=[3*inch, 3.5*inch])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#2c5aa0')),
            ('BACKGROUND', (1, 0), (1, 0), score_color),
            ('TEXTCOLOR', (0, 0), (0, 0), colors.white),
            ('TEXTCOLOR', (1, 0), (1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        self.story.append(score_table)
        self.story.append(Spacer(1, 0.15*inch))
        
        # Detailed Score Breakdown with weights
        score_breakdown = health_fitness.get_score_breakdown()
        breakdown_data = [['Check Item', 'Weight', 'Earned', 'Status', 'Critical']]
        for item in score_breakdown['items']:
            status_display = item['status']
            critical_marker = '⚠️' if item['critical'] else ''
            breakdown_data.append([
                item['item'],
                str(item.get('weight', 1)),
                str(item['earned']),
                status_display,
                critical_marker
            ])
        
        breakdown_table = Table(breakdown_data, colWidths=[2.5*inch, 0.8*inch, 0.8*inch, 1.5*inch, 0.7*inch])
        breakdown_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (2, -1), 'CENTER'),
            ('ALIGN', (4, 0), (4, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])
        
        # Color code earned column based on whether points were earned
        for i, item in enumerate(score_breakdown['items'], 1):
            if item['earned'] == item.get('weight', 1):
                breakdown_style.add('BACKGROUND', (2, i), (2, i), colors.HexColor('#90EE90'))
            elif item['earned'] == 0 and item['critical']:
                breakdown_style.add('BACKGROUND', (2, i), (2, i), colors.HexColor('#FF6B6B'))
            elif item['earned'] == 0:
                breakdown_style.add('BACKGROUND', (2, i), (2, i), colors.HexColor('#FFD700'))
        
        breakdown_table.setStyle(breakdown_style)
        self.story.append(breakdown_table)
        self.story.append(Spacer(1, 0.15*inch))
        
        # Original detailed data
        data = [
            ['Adequate Rest (8+ hours):', 'Yes' if health_fitness.adequate_rest else 'No'],
            ['Alcohol Test:', self._get_status_display(health_fitness.alcohol_test_status)],
            ['Temperature Check:', self._get_status_display(health_fitness.temperature_check_status)],
            ['Temperature Value:', f"{health_fitness.temperature_value}°C" if health_fitness.temperature_value else 'N/A'],
            ['Fit for Duty:', 'Yes' if health_fitness.fit_for_duty else 'No'],
            ['On Medication:', 'Yes' if health_fitness.medication_status else 'No'],
            ['No Health Impairment:', 'Yes' if health_fitness.no_health_impairment else 'No'],
            ['Fatigue Checklist:', 'Completed' if health_fitness.fatigue_checklist_completed else 'Not Completed'],
        ]
        
        if health_fitness.alcohol_test_remarks:
            data.append(['Alcohol Test Remarks:', health_fitness.alcohol_test_remarks])
        if health_fitness.medication_remarks:
            data.append(['Medication Remarks:', health_fitness.medication_remarks])
        if health_fitness.fatigue_remarks:
            data.append(['Fatigue Remarks:', health_fitness.fatigue_remarks])
        
        table = Table(data, colWidths=[2*inch, 4.5*inch])
        table.setStyle(self._get_check_table_style())
        self.story.append(table)
        self.story.append(Spacer(1, 0.2*inch))
    
    def generate_documentation(self, inspection):
        """Section 3: Documentation & Compliance"""
        try:
            documentation = DocumentationCompliance.objects.get(inspection=inspection)
        except DocumentationCompliance.DoesNotExist:
            return
        
        section = Paragraph("3. DOCUMENTATION & COMPLIANCE", self.styles['SectionHeader'])
        self.story.append(section)
        
        data = [
            ['Certificate of Fitness:', self._get_status_display(documentation.certificate_of_fitness)],
            ['Road Tax Valid:', 'Yes' if documentation.road_tax_valid else 'No'],
            ['Insurance Valid:', 'Yes' if documentation.insurance_valid else 'No'],
            ['Trip Authorization Signed:', 'Yes' if documentation.trip_authorization_signed else 'No'],
            ['Logbook Present:', 'Yes' if documentation.logbook_present else 'No'],
            ['Driver Handbook Present:', 'Yes' if documentation.driver_handbook_present else 'No'],
            ['Permits Valid:', 'Yes' if documentation.permits_valid else 'No'],
            ['PPE Available:', 'Yes' if documentation.ppe_available else 'No'],
            ['Route Familiarity:', 'Yes' if documentation.route_familiarity else 'No'],
            ['Emergency Procedures Known:', 'Yes' if documentation.emergency_procedures_known else 'No'],
            ['GPS Activated:', 'Yes' if documentation.gps_activated else 'No'],
            ['Safety Briefing Provided:', 'Yes' if documentation.safety_briefing_provided else 'No'],
            ['RTSA Clearance:', 'Yes' if documentation.rtsa_clearance else 'No'],
        ]
        
        if documentation.emergency_contact:
            data.append(['Emergency Contact:', documentation.emergency_contact])
        
        table = Table(data, colWidths=[2.5*inch, 4*inch])
        table.setStyle(self._get_check_table_style())
        self.story.append(table)
        self.story.append(Spacer(1, 0.2*inch))
    
    def generate_vehicle_checks(self, inspection):
        """Sections 4-8: Vehicle Inspection Checks"""
        # Exterior Checks
        self._generate_exterior_checks(inspection)
        
        # Engine & Fluids
        self._generate_engine_checks(inspection)
        
        # Interior & Cabin
        self._generate_interior_checks(inspection)
        
        # Functional Checks
        self._generate_functional_checks(inspection)
        
        # Safety Equipment
        self._generate_safety_checks(inspection)
        
        # Brakes & Steering (Critical)
        self._generate_brakes_steering_checks(inspection)
    
    def _generate_exterior_checks(self, inspection):
        """Generate exterior checks section"""
        checks = VehicleExteriorCheck.objects.filter(inspection=inspection)
        if not checks.exists():
            return
        
        section = Paragraph("4. VEHICLE EXTERIOR CHECKS", self.styles['SectionHeader'])
        self.story.append(section)
        
        data = [['Component', 'Status', 'Remarks']]
        for check in checks:
            data.append([
                self._normalize_field_name(check.check_item),
                self._get_status_display(check.status),
                check.remarks or 'N/A'
            ])
        
        table = Table(data, colWidths=[2*inch, 1.5*inch, 3*inch])
        table.setStyle(self._get_vehicle_check_table_style(len(data)))
        self.story.append(table)
        self.story.append(Spacer(1, 0.2*inch))
    
    def _generate_engine_checks(self, inspection):
        """Generate engine and fluid checks section"""
        checks = EngineFluidCheck.objects.filter(inspection=inspection)
        if not checks.exists():
            return
        
        section = Paragraph("5. ENGINE & FLUID CHECKS", self.styles['SectionHeader'])
        self.story.append(section)
        
        data = [['Component', 'Status', 'Remarks']]
        for check in checks:
            data.append([
                self._normalize_field_name(check.check_item),
                self._get_status_display(check.status),
                check.remarks or 'N/A'
            ])
        
        table = Table(data, colWidths=[2*inch, 1.5*inch, 3*inch])
        table.setStyle(self._get_vehicle_check_table_style(len(data)))
        self.story.append(table)
        self.story.append(Spacer(1, 0.2*inch))
    
    def _generate_interior_checks(self, inspection):
        """Generate interior and cabin checks section"""
        checks = InteriorCabinCheck.objects.filter(inspection=inspection)
        if not checks.exists():
            return
        
        section = Paragraph("6. INTERIOR & CABIN CHECKS", self.styles['SectionHeader'])
        self.story.append(section)
        
        data = [['Component', 'Status', 'Remarks']]
        for check in checks:
            data.append([
                self._normalize_field_name(check.check_item),
                self._get_status_display(check.status),
                check.remarks or 'N/A'
            ])
        
        table = Table(data, colWidths=[2*inch, 1.5*inch, 3*inch])
        table.setStyle(self._get_vehicle_check_table_style(len(data)))
        self.story.append(table)
        self.story.append(Spacer(1, 0.2*inch))
    
    def _generate_functional_checks(self, inspection):
        """Generate functional checks section"""
        checks = FunctionalCheck.objects.filter(inspection=inspection)
        if not checks.exists():
            return
        
        section = Paragraph("7. FUNCTIONAL CHECKS", self.styles['SectionHeader'])
        self.story.append(section)
        
        data = [['Component', 'Status', 'Remarks']]
        for check in checks:
            data.append([
                self._normalize_field_name(check.check_item),
                self._get_status_display(check.status),
                check.remarks or 'N/A'
            ])
        
        table = Table(data, colWidths=[2*inch, 1.5*inch, 3*inch])
        table.setStyle(self._get_vehicle_check_table_style(len(data)))
        self.story.append(table)
        self.story.append(Spacer(1, 0.2*inch))
    
    def _generate_safety_checks(self, inspection):
        """Generate safety equipment checks section"""
        checks = SafetyEquipmentCheck.objects.filter(inspection=inspection)
        if not checks.exists():
            return
        
        section = Paragraph("8. SAFETY EQUIPMENT CHECKS", self.styles['SectionHeader'])
        self.story.append(section)
        
        data = [['Equipment', 'Status', 'Remarks']]
        for check in checks:
            data.append([
                self._normalize_field_name(check.check_item),
                self._get_status_display(check.status),
                check.remarks or 'N/A'
            ])
        
        table = Table(data, colWidths=[2*inch, 1.5*inch, 3*inch])
        table.setStyle(self._get_vehicle_check_table_style(len(data)))
        self.story.append(table)
        self.story.append(Spacer(1, 0.2*inch))
    
    def _generate_brakes_steering_checks(self, inspection):
        """Generate brakes and steering checks section"""
        checks = BrakesSteeringCheck.objects.filter(inspection=inspection)
        if not checks.exists():
            return
        
        section = Paragraph("9. BRAKES & STEERING CHECKS (CRITICAL)", self.styles['SectionHeader'])
        self.story.append(section)
        
        # Add warning banner for critical items
        warning_data = [['⚠ ALL ITEMS IN THIS SECTION ARE CRITICAL - FAILURES WILL PREVENT TRAVEL CLEARANCE']]
        warning_table = Table(warning_data, colWidths=[6.5*inch])
        warning_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FFF3CD')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#856404')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        self.story.append(warning_table)
        self.story.append(Spacer(1, 0.1*inch))
        
        data = [['Component', 'Status', 'Remarks']]
        for check in checks:
            data.append([
                self._normalize_field_name(check.check_item),
                self._get_status_display(check.status),
                check.remarks or 'N/A'
            ])
        
        table = Table(data, colWidths=[2*inch, 1.5*inch, 3*inch])
        table.setStyle(self._get_vehicle_check_table_style(len(data)))
        self.story.append(table)
        self.story.append(Spacer(1, 0.2*inch))
    
    def generate_trip_behaviors(self, inspection):
        """Section 10: Trip Behavior Monitoring"""
        behaviors = TripBehaviorMonitoring.objects.filter(inspection=inspection)
        if not behaviors.exists():
            return
        
        section = Paragraph("10. TRIP BEHAVIOR MONITORING", self.styles['SectionHeader'])
        self.story.append(section)
        
        data = [['Behavior Item', 'Status', 'Violation Points', 'Notes']]
        for behavior in behaviors:
            data.append([
                self._normalize_field_name(behavior.behavior_item),
                self._get_status_display(behavior.status),
                str(behavior.violation_points),
                behavior.notes or 'N/A'
            ])
        
        # Add total
        total_points = sum(b.violation_points for b in behaviors)
        data.append(['TOTAL VIOLATION POINTS', '', str(total_points), ''])
        
        table = Table(data, colWidths=[2.5*inch, 1.3*inch, 1.2*inch, 1.5*inch])
        table.setStyle(self._get_vehicle_check_table_style(len(data)))
        # Highlight total row
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0f0f0')),
            ('FONTNAME', (0, -1), (1, -1), 'Helvetica-Bold'),
        ]))
        self.story.append(table)
        self.story.append(Spacer(1, 0.2*inch))
    
    def generate_driving_behaviors(self, inspection):
        """Section 10: Driving Behavior Checks"""
        behaviors = DrivingBehaviorCheck.objects.filter(inspection=inspection)
        if not behaviors.exists():
            return
        
        section = Paragraph("10. DRIVING BEHAVIOR CHECKS", self.styles['SectionHeader'])
        self.story.append(section)
        
        data = [['Behavior', 'Compliant', 'Remarks']]
        for behavior in behaviors:
            data.append([
                self._normalize_field_name(behavior.behavior_item),
                'Yes' if behavior.status else 'No',
                behavior.remarks or 'N/A'
            ])
        
        table = Table(data, colWidths=[2.5*inch, 1.2*inch, 2.8*inch])
        table.setStyle(self._get_vehicle_check_table_style(len(data)))
        self.story.append(table)
        self.story.append(Spacer(1, 0.2*inch))
    
    def generate_post_trip(self, inspection):
        """Section 11: Post-Trip Report"""
        try:
            post_trip = PostTripReport.objects.get(inspection=inspection)
        except PostTripReport.DoesNotExist:
            return
        
        section = Paragraph("11. POST-TRIP REPORT", self.styles['SectionHeader'])
        self.story.append(section)
        
        data = [
            ['Vehicle Fault Submitted:', 'Yes' if post_trip.vehicle_fault_submitted else 'No'],
            ['Final Inspection Signed:', 'Yes' if post_trip.final_inspection_signed else 'No'],
            ['Compliance with Policy:', 'Yes' if post_trip.compliance_with_policy else 'No'],
            ['Attitude & Cooperation:', 'Yes' if post_trip.attitude_cooperation else 'No'],
            ['Incidents Recorded:', 'Yes' if post_trip.incidents_recorded else 'No'],
            ['Total Trip Duration:', post_trip.total_trip_duration or 'N/A'],
        ]
        
        if post_trip.vehicle_fault_submitted and post_trip.fault_notes:
            data.append(['Fault Notes:', post_trip.fault_notes])
        
        if post_trip.incidents_recorded and post_trip.incident_notes:
            data.append(['Incident Notes:', post_trip.incident_notes])
        
        table = Table(data, colWidths=[2*inch, 4.5*inch])
        table.setStyle(self._get_info_table_style())
        self.story.append(table)
        self.story.append(Spacer(1, 0.2*inch))
    
    def generate_risk_score(self, inspection):
        """Section 12: Risk Score Summary"""
        try:
            risk_score = RiskScoreSummary.objects.get(inspection=inspection)
        except RiskScoreSummary.DoesNotExist:
            return
        
        section = Paragraph("12. RISK SCORE SUMMARY", self.styles['SectionHeader'])
        self.story.append(section)
        
        # Risk score box with color coding
        risk_color = self._get_risk_color(risk_score.risk_level)
        risk_color_30 = self._get_risk_color(risk_score.risk_level_30_days)
        
        data = [
            ['Current Trip Points:', str(risk_score.total_points_this_trip)],
            ['Risk Level (This Trip):', risk_score.risk_level.upper()],
            ['30-Day Total Points:', str(risk_score.total_points_30_days)],
            ['Risk Level (30 Days):', risk_score.risk_level_30_days.upper()],
        ]
        
        table = Table(data, colWidths=[2*inch, 4.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BACKGROUND', (1, 1), (1, 1), risk_color),
            ('FONTNAME', (1, 1), (1, 1), 'Helvetica-Bold'),
            ('BACKGROUND', (1, 3), (1, 3), risk_color_30),
            ('FONTNAME', (1, 3), (1, 3), 'Helvetica-Bold'),
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.2*inch))
    
    def generate_corrective_measures(self, inspection):
        """Section 13: Corrective Measures"""
        measures = CorrectiveMeasure.objects.filter(inspection=inspection)
        if not measures.exists():
            return
        
        section = Paragraph("13. CORRECTIVE MEASURES", self.styles['SectionHeader'])
        self.story.append(section)
        
        data = [['Measure Type', 'Notes', 'Due Date', 'Status']]
        for measure in measures:
            notes_text = measure.notes[:50] + '...' if measure.notes and len(measure.notes) > 50 else (measure.notes or 'N/A')
            data.append([
                measure.get_measure_type_display(),
                notes_text,
                measure.due_date.strftime('%Y-%m-%d') if measure.due_date else 'N/A',
                'Completed' if measure.completed else 'Pending'
            ])
        
        table = Table(data, colWidths=[1.5*inch, 2.5*inch, 1.2*inch, 1.3*inch])
        table.setStyle(self._get_vehicle_check_table_style(len(data)))
        self.story.append(table)
        self.story.append(Spacer(1, 0.2*inch))
    
    def generate_enforcement_actions(self, inspection):
        """Section 14: Enforcement Actions"""
        actions = EnforcementAction.objects.filter(inspection=inspection)
        if not actions.exists():
            return
        
        section = Paragraph("14. ENFORCEMENT ACTIONS", self.styles['SectionHeader'])
        self.story.append(section)
        
        data = [['Action Type', 'Notes', 'Start Date', 'End Date']]
        for action in actions:
            notes_text = action.notes[:50] + '...' if action.notes and len(action.notes) > 50 else (action.notes or 'N/A')
            data.append([
                action.get_action_type_display(),
                notes_text,
                action.start_date.strftime('%Y-%m-%d') if action.start_date else 'N/A',
                action.end_date.strftime('%Y-%m-%d') if action.end_date else 'N/A'
            ])
        
        table = Table(data, colWidths=[1.5*inch, 2.3*inch, 1.3*inch, 1.4*inch])
        table.setStyle(self._get_vehicle_check_table_style(len(data)))
        self.story.append(table)
        self.story.append(Spacer(1, 0.2*inch))
    
    def generate_supervisor_remarks(self, inspection):
        """Section 15: Supervisor Remarks"""
        try:
            remarks = SupervisorRemarks.objects.get(inspection=inspection)
        except SupervisorRemarks.DoesNotExist:
            return
        
        section = Paragraph("15. SUPERVISOR REMARKS", self.styles['SectionHeader'])
        self.story.append(section)
        
        data = [
            ['Supervisor:', remarks.supervisor_name],
            ['Remarks:', remarks.remarks],
        ]
        
        if remarks.recommendation:
            data.append(['Recommendations:', remarks.recommendation])
        
        table = Table(data, colWidths=[2*inch, 4.5*inch])
        table.setStyle(self._get_info_table_style())
        self.story.append(table)
        self.story.append(Spacer(1, 0.2*inch))
    
    def generate_evaluation(self, inspection):
        """Section 16: Evaluation Summary"""
        try:
            evaluation = EvaluationSummary.objects.get(inspection=inspection)
        except EvaluationSummary.DoesNotExist:
            return
        
        section = Paragraph("16. EVALUATION SUMMARY", self.styles['SectionHeader'])
        self.story.append(section)
        
        data = [
            ['Criteria', 'Score (1-5)'],
            ['Pre-Trip Inspection', str(evaluation.pre_trip_inspection_score)],
            ['Driving Conduct', str(evaluation.driving_conduct_score)],
            ['Incident Management', str(evaluation.incident_management_score)],
            ['Post-Trip Reporting', str(evaluation.post_trip_reporting_score)],
            ['Compliance & Documentation', str(evaluation.compliance_documentation_score)],
            ['AVERAGE SCORE', f"{evaluation.calculate_average_score():.2f}"],
            ['OVERALL PERFORMANCE', evaluation.get_overall_performance_display().upper()],
        ]
        
        if evaluation.comments:
            data.append(['Comments:', evaluation.comments])
        
        table = Table(data, colWidths=[3*inch, 3.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BACKGROUND', (0, -2), (-1, -1), colors.HexColor('#f0f0f0')),
            ('FONTNAME', (0, -2), (-1, -1), 'Helvetica-Bold'),
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.2*inch))
    
    def generate_signatures(self, inspection):
        """Section 17: Sign-Off Section"""
        section = Paragraph("17. SIGN-OFFS", self.styles['SectionHeader'])
        self.story.append(section)
        
        # Get existing sign-offs
        sign_offs = InspectionSignOff.objects.filter(inspection=inspection)
        sign_off_dict = {so.role: so for so in sign_offs}
        
        # Create signature table
        roles = ['driver', 'supervisor', 'mechanic']
        data = [['Role', 'Name', 'Signature', 'Date']]
        
        for role in roles:
            sign_off = sign_off_dict.get(role)
            if sign_off:
                data.append([
                    role.upper(),
                    sign_off.signer_name,
                    '_________________',
                    sign_off.signed_at.strftime('%Y-%m-%d')
                ])
            else:
                data.append([
                    role.upper(),
                    '_________________',
                    '_________________',
                    '_________________'
                ])
        
        table = Table(data, colWidths=[1.3*inch, 2*inch, 1.8*inch, 1.4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 20),
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.3*inch))
    
    def generate_pre_trip_score_summary(self, inspection):
        """Generate Pre-Trip Score Summary Section"""
        # Try to get or create score summary
        try:
            score_summary = PreTripScoreSummary.objects.get(inspection=inspection)
        except PreTripScoreSummary.DoesNotExist:
            # Create and calculate score summary
            score_summary = PreTripScoreSummary(inspection=inspection)
            score_summary.save()
        
        section = Paragraph("PRE-TRIP CHECKLIST SCORE SUMMARY", self.styles['SectionHeader'])
        self.story.append(section)
        
        # Overall Score Box with Risk Status
        score_color = colors.HexColor('#90EE90') if float(score_summary.score_percentage) >= 85 else (
            colors.HexColor('#FFD700') if float(score_summary.score_percentage) >= 70 else colors.HexColor('#FF6B6B')
        )
        
        # Risk status color mapping - updated for new risk levels
        risk_colors = {
            'no_risk': colors.HexColor('#90EE90'),  # Green
            'very_low_risk': colors.HexColor('#E3F2FD'),  # Light Blue
            'low_risk': colors.HexColor('#FFF3E0'),  # Light Orange
            'high_risk': colors.HexColor('#FF6B6B'),  # Red
        }
        risk_color = risk_colors.get(score_summary.risk_status, colors.HexColor('#FF6B6B'))
        
        overall_data = [
            ['OVERALL PRE-TRIP SCORE', f'{float(score_summary.total_score):.1f} / {float(score_summary.max_possible_score):.1f} ({score_summary.score_percentage}%)'],
            ['TOTAL QUESTIONS', str(score_summary.total_questions)],
            ['SCORE PER QUESTION', '1 point'],
            ['SCORE LEVEL', score_summary.get_score_level_display()],
            ['RISK STATUS', score_summary.get_risk_status_display()],
            ['TRAVEL CLEARANCE', 'CLEARED ✓' if score_summary.is_cleared_for_travel else 'NOT CLEARED ⚠'],
        ]
        
        overall_table = Table(overall_data, colWidths=[3*inch, 3.5*inch])
        overall_style = TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('BACKGROUND', (1, 0), (1, 0), score_color),
            ('BACKGROUND', (1, 1), (1, 2), colors.HexColor('#f0f0f0')),
            ('BACKGROUND', (1, 3), (1, 3), colors.HexColor('#f0f0f0')),
            ('BACKGROUND', (1, 4), (1, 4), risk_color),
            ('BACKGROUND', (1, 5), (1, 5), colors.HexColor('#90EE90') if score_summary.is_cleared_for_travel else colors.HexColor('#FF6B6B')),
            ('TEXTCOLOR', (1, 5), (1, 5), colors.HexColor('#166534') if score_summary.is_cleared_for_travel else colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ])
        overall_table.setStyle(overall_style)
        self.story.append(overall_table)
        self.story.append(Spacer(1, 0.15*inch))
        
        # Section Breakdown with Subtotals, Max Weight and Risk Levels
        # Formula: Section % = (earned * 100) / 63, Max % = (questions * 100) / 63
        section_summary = score_summary.get_section_summary()
        breakdown_data = [['Section', 'Questions', 'Subtotal', 'Max %', 'Earned %', 'Risk Level']]
        for section in section_summary:
            pct = section['percentage']  # Section-specific percentage (earned/max * 100)
            subtotal = section.get('subtotal', f"{section['score']}/{section['max']}")
            questions = section.get('questions', '-')
            risk_display = section.get('risk_display', 'N/A')
            max_weight = section.get('max_weight', 0)  # Max % this section contributes
            earned_pct = section.get('total_percentage', 0)  # Earned % of total (earned * 100 / 63)
            breakdown_data.append([
                section['section'],
                str(questions),
                subtotal,
                f"{max_weight:.2f}%",
                f"{earned_pct:.2f}%",
                risk_display
            ])
        
        # Add totals row
        total_max_weight = sum(s.get('max_weight', 0) for s in section_summary)
        total_earned_pct = sum(s.get('total_percentage', 0) for s in section_summary)
        breakdown_data.append([
            'Overall Score',
            str(score_summary.total_questions),
            f"{int(score_summary.total_score)}/{int(score_summary.max_possible_score)}",
            f"100%",
            f"{total_earned_pct:.2f}%",
            score_summary.get_risk_status_display()
        ])
        
        breakdown_table = Table(breakdown_data, colWidths=[1.8*inch, 0.7*inch, 1.0*inch, 0.8*inch, 0.9*inch, 1.3*inch])
        breakdown_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (5, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            # Style the totals row
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8e8e8')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ])
        
        # Color code Earned % and Risk columns using thresholds
        # Column indices: 0=Section, 1=Questions, 2=Subtotal, 3=Max%, 4=Earned%, 5=Risk
        risk_colors = {
            'No Risk': colors.HexColor('#e8f5e9'),
            'Very Low Risk': colors.HexColor('#E3F2FD'),
            'Low Risk': colors.HexColor('#FFF3E0'),
            'High Risk': colors.HexColor('#FFEBEE'),
        }
        for i, section in enumerate(section_summary, 1):
            pct = section['percentage']  # Section completion % (earned/max * 100)
            # Color code Earned % column (column 4)
            if pct >= 100:
                breakdown_style.add('BACKGROUND', (4, i), (4, i), colors.HexColor('#e8f5e9'))
            elif pct >= 85:
                breakdown_style.add('BACKGROUND', (4, i), (4, i), colors.HexColor('#E3F2FD'))
            elif pct >= 70:
                breakdown_style.add('BACKGROUND', (4, i), (4, i), colors.HexColor('#FFF3E0'))
            else:
                breakdown_style.add('BACKGROUND', (4, i), (4, i), colors.HexColor('#FFEBEE'))
            
            # Color code Risk column (column 5)
            risk_display = section.get('risk_display', 'N/A')
            risk_bg = risk_colors.get(risk_display, colors.HexColor('#f5f5f5'))
            breakdown_style.add('BACKGROUND', (5, i), (5, i), risk_bg)
        
        breakdown_table.setStyle(breakdown_style)
        self.story.append(breakdown_table)
        self.story.append(Spacer(1, 0.15*inch))
        
        # Critical Failures (if any)
        if score_summary.has_critical_failures:
            failures_title = Paragraph(
                '<font color="red"><b>⚠ CRITICAL FAILURES</b></font>',
                self.styles['Normal']
            )
            self.story.append(failures_title)
            self.story.append(Spacer(1, 0.05*inch))
            
            for failure in score_summary.critical_failures:
                failure_item = Paragraph(f'• {failure}', self.styles['Normal'])
                self.story.append(failure_item)
            
            self.story.append(Spacer(1, 0.1*inch))
        
        # Clearance Notes
        if score_summary.clearance_notes:
            notes = Paragraph(
                f'<b>Clearance Notes:</b> {score_summary.clearance_notes}',
                self.styles['Normal']
            )
            self.story.append(notes)
        
        self.story.append(Spacer(1, 0.2*inch))
    
    def generate_post_checklist_score_summary(self, inspection):
        """Generate Post-Checklist Score Summary Section"""
        # Try to get or create post-checklist score summary
        try:
            score_summary = PostChecklistScoreSummary.objects.get(inspection=inspection)
        except PostChecklistScoreSummary.DoesNotExist:
            # Create and calculate score summary
            score_summary = PostChecklistScoreSummary(inspection=inspection)
            score_summary.save()
        
        section = Paragraph("POST-CHECKLIST SCORE SUMMARY", self.styles['SectionHeader'])
        self.story.append(section)
        
        # Overall Score Box with Risk Status
        pct = float(score_summary.score_percentage)
        score_color = colors.HexColor('#90EE90') if pct >= 100 else (
            colors.HexColor('#E3F2FD') if pct >= 85 else (
                colors.HexColor('#FFF3E0') if pct >= 70 else colors.HexColor('#FF6B6B')
            )
        )
        
        # Risk status color mapping
        risk_colors = {
            'no_risk': colors.HexColor('#90EE90'),  # Green
            'very_low_risk': colors.HexColor('#E3F2FD'),  # Light Blue
            'low_risk': colors.HexColor('#FFF3E0'),  # Light Orange
            'high_risk': colors.HexColor('#FF6B6B'),  # Red
        }
        risk_color = risk_colors.get(score_summary.risk_status, colors.HexColor('#FF6B6B'))
        
        overall_data = [
            ['OVERALL POST-CHECKLIST SCORE', f'{float(score_summary.total_score):.1f} / {float(score_summary.max_possible_score):.1f} ({score_summary.score_percentage}%)'],
            ['TOTAL QUESTIONS', str(score_summary.total_questions)],
            ['SCORE PER QUESTION', '1 point'],
            ['RISK STATUS', score_summary.get_risk_status_display()],
        ]
        
        overall_table = Table(overall_data, colWidths=[3*inch, 3.5*inch])
        overall_style = TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#4a7c4e')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('BACKGROUND', (1, 0), (1, 0), score_color),
            ('BACKGROUND', (1, 1), (1, 2), colors.HexColor('#f0f0f0')),
            ('BACKGROUND', (1, 3), (1, 3), risk_color),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ])
        overall_table.setStyle(overall_style)
        self.story.append(overall_table)
        self.story.append(Spacer(1, 0.15*inch))
        
        # Section Breakdown with Subtotals and Risk Levels
        section_summary = score_summary.get_section_summary()
        breakdown_data = [['Section', 'Questions', 'Subtotal', 'Percentage', 'Risk Level']]
        for section in section_summary:
            pct = section['percentage']
            subtotal = section.get('subtotal', f"{section['score']}/{section['max']}")
            questions = section.get('questions', '-')
            risk_display = section.get('risk_display', 'N/A')
            breakdown_data.append([
                section['section'],
                str(questions),
                subtotal,
                f"{pct}%",
                risk_display
            ])
        
        breakdown_table = Table(breakdown_data, colWidths=[2.0*inch, 0.8*inch, 1.2*inch, 1.0*inch, 1.5*inch])
        breakdown_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a7c4e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (4, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ])
        
        # Color code percentage and risk columns
        risk_bg_colors = {
            'No Risk': colors.HexColor('#e8f5e9'),
            'Very Low Risk': colors.HexColor('#E3F2FD'),
            'Low Risk': colors.HexColor('#FFF3E0'),
            'High Risk': colors.HexColor('#FFEBEE'),
        }
        for i, section in enumerate(section_summary, 1):
            pct = section['percentage']
            # Color code percentage column
            if pct >= 100:
                breakdown_style.add('BACKGROUND', (3, i), (3, i), colors.HexColor('#e8f5e9'))
            elif pct >= 85:
                breakdown_style.add('BACKGROUND', (3, i), (3, i), colors.HexColor('#E3F2FD'))
            elif pct >= 70:
                breakdown_style.add('BACKGROUND', (3, i), (3, i), colors.HexColor('#FFF3E0'))
            else:
                breakdown_style.add('BACKGROUND', (3, i), (3, i), colors.HexColor('#FFEBEE'))
            
            # Color code risk column
            risk_display = section.get('risk_display', 'N/A')
            risk_bg = risk_bg_colors.get(risk_display, colors.HexColor('#f5f5f5'))
            breakdown_style.add('BACKGROUND', (4, i), (4, i), risk_bg)
        
        breakdown_table.setStyle(breakdown_style)
        self.story.append(breakdown_table)
        self.story.append(Spacer(1, 0.2*inch))
    
    def generate_final_score_summary(self, inspection):
        """Generate Final Score Summary Section combining Pre and Post Checklists"""
        # Try to get or create final score summary
        try:
            final_summary = FinalScoreSummary.objects.get(inspection=inspection)
        except FinalScoreSummary.DoesNotExist:
            # Create and calculate final score summary
            final_summary = FinalScoreSummary(inspection=inspection)
            final_summary.save()
        
        section = Paragraph("FINAL EVALUATION REPORT", self.styles['SectionHeader'])
        self.story.append(section)
        
        # Final Status colors
        final_status_colors = {
            'passed': colors.HexColor('#90EE90'),
            'needs_review': colors.HexColor('#FFF3E0'),
            'failed': colors.HexColor('#FF6B6B'),
        }
        
        # Final Risk level colors
        final_risk_colors = {
            'no_risk': colors.HexColor('#90EE90'),
            'very_low_risk': colors.HexColor('#E3F2FD'),
            'low_risk': colors.HexColor('#FFF3E0'),
            'high_risk': colors.HexColor('#FF6B6B'),
        }
        
        status_color = final_status_colors.get(final_summary.final_status, colors.HexColor('#f0f0f0'))
        risk_color = final_risk_colors.get(final_summary.final_risk_level, colors.HexColor('#f0f0f0'))
        
        # Final Score Summary Table
        final_data = [
            ['PRE-CHECKLIST (50%)', f'{float(final_summary.pre_checklist_percentage):.1f}% → Weighted: {float(final_summary.pre_checklist_weighted):.1f}%'],
            ['POST-CHECKLIST (50%)', f'{float(final_summary.post_checklist_percentage):.1f}% → Weighted: {float(final_summary.post_checklist_weighted):.1f}%'],
            ['FINAL PERCENTAGE', f'{float(final_summary.final_percentage):.1f}%'],
            ['FINAL STATUS', final_summary.get_final_status_display()],
            ['FINAL RISK LEVEL', final_summary.get_final_risk_level_display()],
        ]
        
        final_table = Table(final_data, colWidths=[3*inch, 3.5*inch])
        final_style = TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#1976d2')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('BACKGROUND', (1, 0), (1, 1), colors.HexColor('#f0f0f0')),
            ('BACKGROUND', (1, 2), (1, 2), colors.HexColor('#e3f2fd')),
            ('BACKGROUND', (1, 3), (1, 3), status_color),
            ('BACKGROUND', (1, 4), (1, 4), risk_color),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ])
        final_table.setStyle(final_style)
        self.story.append(final_table)
        self.story.append(Spacer(1, 0.15*inch))
        
        # Final Comment
        if final_summary.final_comment:
            comment_title = Paragraph('<b>Final Comment:</b>', self.styles['Normal'])
            self.story.append(comment_title)
            self.story.append(Spacer(1, 0.05*inch))
            
            comment_text = Paragraph(final_summary.final_comment, self.styles['Normal'])
            self.story.append(comment_text)
            self.story.append(Spacer(1, 0.15*inch))
        
        # Module Performance Breakdown
        breakdown = final_summary.get_breakdown()
        if breakdown:
            breakdown_title = Paragraph('<b>Module Performance Breakdown:</b>', self.styles['Normal'])
            self.story.append(breakdown_title)
            self.story.append(Spacer(1, 0.1*inch))
            
            # Pre-Checklist Modules
            pre_title = Paragraph('<i>Pre-Checklist Modules:</i>', self.styles['Normal'])
            self.story.append(pre_title)
            
            pre_sections = breakdown.get('pre_checklist', {}).get('sections', [])
            if pre_sections:
                pre_data = [['Module', 'Score', 'Percentage', 'Risk']]
                for section in pre_sections:
                    pre_data.append([
                        section['section'],
                        f"{section['score']}/{section['max']}",
                        f"{section['percentage']}%",
                        section.get('risk_display', 'N/A')
                    ])
                
                pre_table = Table(pre_data, colWidths=[2.5*inch, 1.2*inch, 1.2*inch, 1.5*inch])
                pre_style = TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ])
                pre_table.setStyle(pre_style)
                self.story.append(pre_table)
                self.story.append(Spacer(1, 0.1*inch))
            
            # Post-Checklist Modules
            post_title = Paragraph('<i>Post-Checklist Modules:</i>', self.styles['Normal'])
            self.story.append(post_title)
            
            post_sections = breakdown.get('post_checklist', {}).get('sections', [])
            if post_sections:
                post_data = [['Module', 'Score', 'Percentage', 'Risk']]
                for section in post_sections:
                    post_data.append([
                        section['section'],
                        f"{section['score']}/{section['max']}",
                        f"{section['percentage']}%",
                        section.get('risk_display', 'N/A')
                    ])
                
                post_table = Table(post_data, colWidths=[2.5*inch, 1.2*inch, 1.2*inch, 1.5*inch])
                post_style = TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a7c4e')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ])
                post_table.setStyle(post_style)
                self.story.append(post_table)
        
        self.story.append(Spacer(1, 0.2*inch))

    def generate_section_pdf(self, inspection_id, section_name):
        """
        Generate PDF for a specific section of the pre-trip checklist wizard.
        This allows generating PDF for each form in the wizard before proceeding to next.
        
        Args:
            inspection_id: ID of the inspection
            section_name: One of 'health_fitness', 'documentation', 'exterior', 
                         'engine', 'interior', 'functional', 'safety', 'brakes_steering'
        
        Returns:
            PDF bytes
        """
        try:
            inspection = PreTripInspection.objects.select_related(
                'driver', 'vehicle', 'supervisor'
            ).get(id=inspection_id)
        except PreTripInspection.DoesNotExist:
            raise ValueError(f"Inspection with ID {inspection_id} not found")
        
        # Create PDF buffer
        buffer = BytesIO()
        
        # Set watermark based on status
        watermark = None
        if inspection.status == 'draft':
            watermark = 'DRAFT'
        
        def create_canvas(*args, **kwargs):
            c = NumberedCanvas(*args, **kwargs)
            c.watermark_text = watermark
            return c
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Build story for specific section
        self.story = []
        
        # Add header
        self._generate_section_header(inspection, section_name)
        
        # Generate appropriate section
        section_mapping = {
            'health_fitness': self.generate_health_fitness,
            'documentation': self.generate_documentation,
            'exterior': self._generate_exterior_checks,
            'engine': self._generate_engine_checks,
            'interior': self._generate_interior_checks,
            'functional': self._generate_functional_checks,
            'safety': self._generate_safety_checks,
            'brakes_steering': self._generate_brakes_steering_checks,
        }
        
        if section_name not in section_mapping:
            raise ValueError(f"Invalid section name: {section_name}")
        
        # Generate the section content
        section_mapping[section_name](inspection)
        
        # Add section score summary
        self._generate_section_score_summary(inspection, section_name)
        
        # Build PDF
        doc.build(self.story, canvasmaker=create_canvas)
        
        pdf = buffer.getvalue()
        buffer.close()
        
        return pdf
    
    def _generate_section_header(self, inspection, section_name):
        """Generate header for individual section PDF"""
        section_titles = {
            'health_fitness': 'Health & Fitness Check',
            'documentation': 'Documentation & Compliance',
            'exterior': 'Vehicle Exterior Checks',
            'engine': 'Engine & Fluid Checks',
            'interior': 'Interior & Cabin Checks',
            'functional': 'Functional Checks',
            'safety': 'Safety Equipment Checks',
            'brakes_steering': 'Brakes & Steering Checks',
        }
        
        title = Paragraph(
            f"PRE-TRIP CHECKLIST - {section_titles.get(section_name, section_name).upper()}", 
            self.styles['CustomTitle']
        )
        self.story.append(title)
        
        # Basic inspection info
        info_data = [
            ['Inspection ID:', inspection.inspection_id, 'Date:', inspection.inspection_date.strftime('%Y-%m-%d')],
            ['Driver:', inspection.driver.full_name, 'Vehicle:', inspection.vehicle.registration_number],
        ]
        
        info_table = Table(info_data, colWidths=[1.5*inch, 2*inch, 1.2*inch, 1.8*inch])
        info_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 9),
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 9),
            ('FONT', (2, 0), (2, -1), 'Helvetica-Bold', 9),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        
        self.story.append(info_table)
        self.story.append(Spacer(1, 0.3*inch))
    
    def _generate_section_score_summary(self, inspection, section_name):
        """Generate score summary for individual section"""
        try:
            score_summary, _ = PreTripScoreSummary.objects.get_or_create(inspection=inspection)
            score_summary.save()  # Recalculate scores
        except Exception:
            return
        
        # Map section names to score fields
        score_mapping = {
            'health_fitness': ('health_fitness_score', 'health_fitness_max', 'health_fitness_questions'),
            'documentation': ('documentation_score', 'documentation_max', 'documentation_questions'),
            'exterior': ('vehicle_exterior_score', 'vehicle_exterior_max', 'vehicle_exterior_questions'),
            'engine': ('engine_fluid_score', 'engine_fluid_max', 'engine_fluid_questions'),
            'interior': ('interior_cabin_score', 'interior_cabin_max', 'interior_cabin_questions'),
            'functional': ('functional_score', 'functional_max', 'functional_questions'),
            'safety': ('safety_equipment_score', 'safety_equipment_max', 'safety_equipment_questions'),
            'brakes_steering': ('brakes_steering_score', 'brakes_steering_max', 'brakes_steering_questions'),
        }
        
        if section_name not in score_mapping:
            return
        
        score_field, max_field, questions_field = score_mapping[section_name]
        score = float(getattr(score_summary, score_field, 0))
        max_score = float(getattr(score_summary, max_field, 0))
        questions = getattr(score_summary, questions_field, 0)
        
        if max_score > 0:
            percentage = round((score / max_score) * 100, 1)
        else:
            percentage = 0
        
        self.story.append(Spacer(1, 0.2*inch))
        
        # Section score box
        section_title = Paragraph("<b>SECTION SCORE SUMMARY</b>", self.styles['SubSection'])
        self.story.append(section_title)
        self.story.append(Spacer(1, 0.1*inch))
        
        score_color = colors.HexColor('#e8f5e9') if percentage >= 100 else (
            colors.HexColor('#E3F2FD') if percentage >= 85 else (
                colors.HexColor('#FFF3E0') if percentage >= 70 else colors.HexColor('#FFEBEE')
            )
        )
        
        score_data = [
            ['Questions', 'Score Per Question', 'Section Score', 'Percentage'],
            [str(questions), '1 point', f'{score:.1f} / {max_score:.1f}', f'{percentage}%']
        ]
        
        score_table = Table(score_data, colWidths=[1.5*inch, 1.5*inch, 2*inch, 1.5*inch])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BACKGROUND', (3, 1), (3, 1), score_color),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        self.story.append(score_table)
        
        # Risk indicator based on section percentage - updated thresholds
        if percentage >= 100:
            risk_text = 'NO RISK'
            risk_color = colors.HexColor('#e8f5e9')
        elif percentage >= 85:
            risk_text = 'VERY LOW RISK'
            risk_color = colors.HexColor('#E3F2FD')
        elif percentage >= 70:
            risk_text = 'LOW RISK'
            risk_color = colors.HexColor('#FFF3E0')
        else:
            risk_text = 'HIGH RISK'
            risk_color = colors.HexColor('#FFEBEE')
        
        self.story.append(Spacer(1, 0.1*inch))
        
        risk_data = [[f'Section Risk Status: {risk_text}']]
        risk_table = Table(risk_data, colWidths=[6.5*inch])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), risk_color),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        self.story.append(risk_table)
    
    def generate_full_report(self, inspection_id):
        """Generate complete PDF report for an inspection"""
        try:
            inspection = PreTripInspection.objects.select_related(
                'driver', 'vehicle', 'supervisor'
            ).get(id=inspection_id)
        except PreTripInspection.DoesNotExist:
            raise ValueError(f"Inspection with ID {inspection_id} not found")
        
        # Create PDF buffer
        buffer = BytesIO()
        
        # Create document with custom canvas for watermarks
        watermark = None
        if inspection.status == 'draft':
            watermark = 'DRAFT'
        elif inspection.status == 'rejected':
            watermark = 'REJECTED'
        
        def create_canvas(*args, **kwargs):
            canvas = NumberedCanvas(*args, **kwargs)
            canvas.watermark_text = watermark
            return canvas
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Build story
        self.story = []
        self.generate_header(inspection)
        self.generate_driver_trip_info(inspection)
        self.generate_health_fitness(inspection)
        self.generate_documentation(inspection)
        self.generate_vehicle_checks(inspection)
        self.generate_pre_trip_score_summary(inspection)  # Add score summary after pre-trip sections
        self.generate_trip_behaviors(inspection)
        self.generate_driving_behaviors(inspection)
        self.generate_post_trip(inspection)
        self.generate_post_checklist_score_summary(inspection)  # Add post-checklist score summary
        self.generate_risk_score(inspection)
        self.generate_corrective_measures(inspection)
        self.generate_enforcement_actions(inspection)
        self.generate_supervisor_remarks(inspection)
        self.generate_evaluation(inspection)
        self.generate_final_score_summary(inspection)  # Add final combined score summary
        self.generate_signatures(inspection)
        
        # Build PDF with custom canvas
        doc.build(self.story, canvasmaker=create_canvas)
        
        # Get PDF value
        pdf = buffer.getvalue()
        buffer.close()
        
        return pdf
    
    def generate_prechecklist_report(self, inspection_id):
        """Generate PDF report for pre-checklist only (sections 1-8)"""
        try:
            inspection = PreTripInspection.objects.select_related(
                'driver', 'vehicle', 'supervisor'
            ).get(id=inspection_id)
        except PreTripInspection.DoesNotExist:
            raise ValueError(f"Inspection with ID {inspection_id} not found")
        
        # Create PDF buffer
        buffer = BytesIO()
        
        # Create document with custom canvas for watermarks
        watermark = None
        if inspection.status == 'draft':
            watermark = 'DRAFT'
        elif inspection.status == 'rejected':
            watermark = 'REJECTED'
        elif inspection.status == 'submitted':
            watermark = 'PENDING APPROVAL'
        
        def create_canvas(*args, **kwargs):
            canvas = NumberedCanvas(*args, **kwargs)
            canvas.watermark_text = watermark
            return canvas
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Build story - Pre-Checklist sections only (1-8) with scores
        self.story = []
        self.generate_prechecklist_header(inspection)
        self.generate_driver_trip_info(inspection)
        self.generate_health_fitness(inspection)
        self.generate_documentation(inspection)
        self.generate_vehicle_checks(inspection)
        self.generate_pre_trip_score_summary(inspection)  # Add score summary
        
        # Build PDF with custom canvas
        doc.build(self.story, canvasmaker=create_canvas)
        
        # Get PDF value
        pdf = buffer.getvalue()
        buffer.close()
        
        return pdf
    
    def generate_prechecklist_header(self, inspection):
        """Generate document header for pre-checklist report"""
        # Title
        title = Paragraph("PRE-TRIP CHECKLIST REPORT", self.styles['CustomTitle'])
        self.story.append(title)
        
        # Form details table
        form_data = [
            ['Form Code:', 'LMP-FSM-PTI/03', 'Version:', '1.0'],
            ['Inspection ID:', str(inspection.inspection_id), 'Status:', inspection.get_status_display().upper()],
        ]
        
        form_table = Table(form_data, colWidths=[1.5*inch, 2*inch, 1.2*inch, 1.8*inch])
        form_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 9),
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 9),
            ('FONT', (2, 0), (2, -1), 'Helvetica-Bold', 9),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('TEXTCOLOR', (1, 1), (1, 1), colors.HexColor('#2c5aa0')),
            ('FONTNAME', (1, 1), (1, 1), 'Helvetica-Bold'),
        ]))
        
        self.story.append(form_table)
        self.story.append(Spacer(1, 0.3*inch))
    
    # Helper methods for styling
    def _normalize_field_name(self, field_name):
        """Convert snake_case field names to readable Title Case"""
        if not field_name:
            return 'N/A'
        # Replace underscores with spaces and convert to title case
        return field_name.replace('_', ' ').title()
    
    def _get_status_display(self, status):
        """Get colored status display"""
        status_text = status.replace('_', ' ').upper()
        if status in ['pass', 'valid', 'compliant']:
            return Paragraph(f'<font color="green"><b>{status_text}</b></font>', self.styles['Normal'])
        elif status in ['fail', 'expired', 'non_compliant', 'missing']:
            return Paragraph(f'<font color="red"><b>{status_text}</b></font>', self.styles['Normal'])
        else:
            return Paragraph(f'<b>{status_text}</b>', self.styles['Normal'])
    
    def _get_risk_color(self, risk_level):
        """Get color for risk level"""
        if risk_level == 'low':
            return colors.HexColor('#90EE90')  # Light green
        elif risk_level == 'medium':
            return colors.HexColor('#FFD700')  # Gold
        else:  # high
            return colors.HexColor('#FF6B6B')  # Light red
    
    def _get_info_table_style(self):
        """Standard style for info tables"""
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])
    
    def _get_check_table_style(self):
        """Standard style for check tables"""
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])
    
    def _get_vehicle_check_table_style(self, row_count):
        """Standard style for vehicle check tables with headers"""
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])
        
        # Alternate row colors for better readability
        for i in range(1, row_count):
            if i % 2 == 0:
                style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f9f9f9'))
        
        return style
