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
    TripBehaviorMonitoring,
    DrivingBehaviorCheck,
    PostTripReport,
    RiskScoreSummary,
    CorrectiveMeasure,
    EnforcementAction,
    SupervisorRemarks,
    EvaluationSummary,
    InspectionSignOff,
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
            ['Vehicle:', f"{inspection.vehicle.registration_number} ({inspection.vehicle.make} {inspection.vehicle.model})", 'Type:', inspection.vehicle.vehicle_type],
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
        """Section 2: Health & Fitness Check"""
        try:
            health_fitness = HealthFitnessCheck.objects.get(inspection=inspection)
        except HealthFitnessCheck.DoesNotExist:
            return
        
        section = Paragraph("2. HEALTH & FITNESS CHECK", self.styles['SectionHeader'])
        self.story.append(section)
        
        data = [
            ['Physical Fitness:', self._get_status_display(health_fitness.physical_fitness)],
            ['Mental Alertness:', self._get_status_display(health_fitness.mental_alertness)],
            ['Substance Check:', self._get_status_display(health_fitness.substance_check)],
            ['Adequate Rest:', self._get_status_display(health_fitness.adequate_rest)],
        ]
        
        if health_fitness.remarks:
            data.append(['Remarks:', health_fitness.remarks])
        
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
            ['Driver License:', self._get_status_display(documentation.driver_license_status),
             'Expiry:', documentation.driver_license_expiry.strftime('%Y-%m-%d')],
            ['Vehicle License:', self._get_status_display(documentation.vehicle_license_status),
             'Expiry:', documentation.vehicle_license_expiry.strftime('%Y-%m-%d')],
            ['Insurance:', self._get_status_display(documentation.insurance_certificate_status),
             'Expiry:', documentation.insurance_expiry.strftime('%Y-%m-%d')],
            ['Roadworthiness:', self._get_status_display(documentation.roadworthiness_status),
             'Expiry:', documentation.roadworthiness_expiry.strftime('%Y-%m-%d')],
        ]
        
        if documentation.remarks:
            data.append(['Remarks:', documentation.remarks, '', ''])
        
        table = Table(data, colWidths=[1.5*inch, 1.8*inch, 0.8*inch, 1.4*inch])
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
                check.check_item,
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
        
        data = [['Component', 'Status', 'Level', 'Remarks']]
        for check in checks:
            data.append([
                check.check_item,
                self._get_status_display(check.status),
                check.fluid_level or 'N/A',
                check.remarks or 'N/A'
            ])
        
        table = Table(data, colWidths=[1.8*inch, 1.2*inch, 1*inch, 2.5*inch])
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
                check.check_item,
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
                check.check_item,
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
        
        data = [['Equipment', 'Status', 'Quantity', 'Remarks']]
        for check in checks:
            data.append([
                check.check_item,
                self._get_status_display(check.status),
                str(check.quantity) if check.quantity else 'N/A',
                check.remarks or 'N/A'
            ])
        
        table = Table(data, colWidths=[1.8*inch, 1.2*inch, 0.8*inch, 2.7*inch])
        table.setStyle(self._get_vehicle_check_table_style(len(data)))
        self.story.append(table)
        self.story.append(Spacer(1, 0.2*inch))
    
    def generate_trip_behaviors(self, inspection):
        """Section 9: Trip Behavior Monitoring"""
        behaviors = TripBehaviorMonitoring.objects.filter(inspection=inspection)
        if not behaviors.exists():
            return
        
        section = Paragraph("9. TRIP BEHAVIOR MONITORING", self.styles['SectionHeader'])
        self.story.append(section)
        
        data = [['Behavior Item', 'Status', 'Violation Points', 'Remarks']]
        for behavior in behaviors:
            data.append([
                behavior.behavior_item,
                self._get_status_display(behavior.status),
                str(behavior.violation_points),
                behavior.remarks or 'N/A'
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
                behavior.behavior_item,
                'Yes' if behavior.is_compliant else 'No',
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
            ['Actual Return Time:', post_trip.actual_return_time.strftime('%Y-%m-%d %H:%M') if post_trip.actual_return_time else 'N/A'],
            ['Final Odometer:', f"{post_trip.final_odometer_reading} km" if post_trip.final_odometer_reading else 'N/A'],
            ['Fuel Level:', post_trip.fuel_level_at_return or 'N/A'],
            ['Faults Detected:', 'Yes' if post_trip.faults_detected else 'No'],
            ['Incidents Reported:', 'Yes' if post_trip.incidents_reported else 'No'],
        ]
        
        if post_trip.faults_detected and post_trip.fault_description:
            data.append(['Fault Description:', post_trip.fault_description])
        
        if post_trip.incidents_reported and post_trip.incident_description:
            data.append(['Incident Description:', post_trip.incident_description])
        
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
        
        data = [
            ['Current Trip Points:', str(risk_score.current_trip_points)],
            ['30-Day Total Points:', str(risk_score.total_30_day_points)],
            ['Risk Level:', risk_score.risk_level.upper()],
            ['Requires Review:', 'Yes' if risk_score.requires_supervisor_review else 'No'],
        ]
        
        if risk_score.notes:
            data.append(['Notes:', risk_score.notes])
        
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
            ('BACKGROUND', (1, 2), (1, 2), risk_color),
            ('FONTNAME', (1, 2), (1, 2), 'Helvetica-Bold'),
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
        
        data = [['Measure Type', 'Description', 'Due Date', 'Status']]
        for measure in measures:
            data.append([
                measure.get_measure_type_display(),
                measure.description[:50] + '...' if len(measure.description) > 50 else measure.description,
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
        
        data = [['Action Type', 'Description', 'Start Date', 'End Date']]
        for action in actions:
            data.append([
                action.get_action_type_display(),
                action.description[:50] + '...' if len(action.description) > 50 else action.description,
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
        self.generate_trip_behaviors(inspection)
        self.generate_driving_behaviors(inspection)
        self.generate_post_trip(inspection)
        self.generate_risk_score(inspection)
        self.generate_corrective_measures(inspection)
        self.generate_enforcement_actions(inspection)
        self.generate_supervisor_remarks(inspection)
        self.generate_evaluation(inspection)
        self.generate_signatures(inspection)
        
        # Build PDF with custom canvas
        doc.build(self.story, canvasmaker=create_canvas)
        
        # Get PDF value
        pdf = buffer.getvalue()
        buffer.close()
        
        return pdf
    
    # Helper methods for styling
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
