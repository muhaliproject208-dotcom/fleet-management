// Inspection Module TypeScript Types
// Based on backend models in backend/inspections/models/

export enum InspectionStatus {
  DRAFT = 'draft',
  SUBMITTED = 'submitted',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  POST_TRIP_IN_PROGRESS = 'post_trip_in_progress',
  POST_TRIP_COMPLETED = 'post_trip_completed',
}

export enum HealthCheckStatus {
  PASS = 'pass',
  FAIL = 'fail',
}

export enum CheckStatus {
  PASS = 'pass',
  FAIL = 'fail',
}

export enum DocumentStatus {
  VALID = 'valid',
  EXPIRED = 'expired',
  MISSING = 'missing',
}

// Basic model with common fields present on most API objects
export interface BaseModel {
  id: string;
  created_at: string;
  updated_at: string;
}

// Core Inspection Types

export interface CompletionInfo {
  completed_steps: number[];
  next_step: number | null;
  completion_percentage: number;
  total_steps: number;
  is_complete?: boolean;
}

export interface PreTripInspection {
  id: string;
  inspection_id: string;
  
  // Core relationships
  driver: {
    id: string;
    driver_id: string;
    full_name: string;
  };
  vehicle: {
    id: string;
    vehicle_id: string;
    registration_number: string;
  };
  supervisor: {
    id: string;
    full_name: string;
  };
  mechanic?: {
    id: string;
    mechanic_id: string;
    full_name: string;
  };
  
  // Inspection details
  inspection_date: string;
  route: string;
  approved_driving_hours: string;
  approved_rest_stops: number;
  driver_rest_approved?: boolean;
  
  // Workflow
  status: InspectionStatus;
  approval_status_updated_at?: string;
  approved_by?: {
    id: string;
    full_name: string;
    email: string;
  };
  rejection_reason?: string;
  
  // Completion tracking for drafts
  completion_info?: CompletionInfo | null;
  
  // Completion tracking for post-trip
  post_trip_completion_info?: CompletionInfo | null;
  
  // Timestamps
  created_at: string;
  updated_at: string;
}

// Vehicle Check Types
export interface VehicleCheck {
  id: string;
  inspection: string;
  check_item: string;
  status: CheckStatus;
  remarks?: string;
  created_at: string;
  updated_at: string;
}

// Trip Behavior Monitoring
export interface TripBehavior {
  id: string;
  inspection: string;
  behavior_item: string;
  status: 'compliant' | 'violation' | 'none';
  notes?: string;
  violation_points: number;
  created_at: string;
  updated_at: string;
}

// Post-Trip Report
export interface PostTripReport {
  id: string;
  inspection: string;
  vehicle_fault_submitted: boolean;
  fault_notes?: string;
  final_inspection_signed: boolean;
  compliance_with_policy: boolean;
  attitude_cooperation: boolean;
  incidents_recorded: boolean;
  incident_notes?: string;
  total_trip_duration: string;
  created_at: string;
  updated_at: string;
}

// Risk Score Summary
export interface RiskScoreSummary {
  id: string;
  inspection: string;
  total_points_this_trip: number;
  risk_level: 'low' | 'medium' | 'high';
  total_points_30_days: number;
  risk_level_30_days: 'low' | 'medium' | 'high';
  created_at: string;
  updated_at: string;
}

// Evaluation Summary
export interface EvaluationSummary {
  id: string;
  inspection: string;
  pre_trip_inspection_score: number;
  driving_conduct_score: number;
  incident_management_score: number;
  post_trip_reporting_score: number;
  compliance_documentation_score: number;
  overall_performance: 'excellent' | 'satisfactory' | 'needs_improvement' | 'non_compliant';
  comments?: string;
  created_at: string;
  updated_at: string;
}

export interface PreTripInspectionFull extends PreTripInspection {
  // OneToOne relationships
  health_fitness?: HealthFitnessCheck | null;
  documentation?: DocumentationCompliance | null;
  supervisor_remarks?: SupervisorRemarks | null;
  post_trip?: PostTripReport | null;
  risk_score?: RiskScoreSummary | null;
  pre_trip_score?: PreTripScoreSummary | null;
  post_checklist_score?: PostChecklistScoreSummary | null;
  final_score?: FinalScoreSummary | null;
  evaluation?: EvaluationSummary | null;
  
  // Vehicle checks (ForeignKey many)
  exterior_checks?: VehicleCheck[];
  engine_fluid_checks?: VehicleCheck[];
  interior_cabin_checks?: VehicleCheck[];
  functional_checks?: VehicleCheck[];
  safety_equipment_checks?: VehicleCheck[];
  brakes_steering_checks?: VehicleCheck[];
  
  // Trip behaviors (ForeignKey many)
  trip_behaviors?: TripBehavior[];
  
  // Computed fields
  completion_percentage?: number;
  total_violation_points?: number;
  has_critical_failures?: boolean;
}

// Supervisor Remarks
export interface SupervisorRemarks {
  id: string;
  inspection: string;
  supervisor_name: string;
  remarks: string;
  recommendation?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateInspectionData {
  driver: string;
  vehicle: string;
  mechanic?: string;
  inspection_date: string;
  route: string;
  approved_driving_hours: string;
  approved_rest_stops: number;
}

export type UpdateInspectionData = Partial<CreateInspectionData>;

// Health & Fitness Check

export interface HealthFitnessScoreItem {
  item: string;
  earned: number; // 0 or 1
  status: string;
  critical: boolean;
}

export interface HealthFitnessScoreBreakdown {
  items: HealthFitnessScoreItem[];
  total: number;
  max: number;
  section_percentage: number; // Percentage within this section
  total_percentage: number; // Percentage of total prechecklist
  risk_level: SectionRiskLevel;
  risk_display: string;
}

export interface HealthFitnessCheck extends BaseModel {
  inspection: string;

  // Fatigue / Rest Clearance - CRITICAL
  adequate_rest: boolean | null;
  rest_clearance_status: 'cleared' | 'not_cleared' | '';
  
  // Checks
  alcohol_test_status: HealthCheckStatus;
  alcohol_test_remarks?: string;
  temperature_check_status: HealthCheckStatus;
  temperature_value?: number;

  // Fitness flags
  fit_for_duty: boolean;
  medication_status: boolean;
  medication_remarks?: string;
  no_health_impairment: boolean;

  // Fatigue
  fatigue_checklist_completed: boolean;
  fatigue_remarks?: string;
  
  // Scoring (1 point per question)
  section_score?: number;
  max_possible_score?: number;
  score_earned?: number;
  score_max?: number;
  score_percentage?: number;
  is_travel_cleared?: boolean;
  clearance_message?: string;
  score_breakdown?: HealthFitnessScoreBreakdown;
}

export interface CreateHealthFitnessData {
  inspection: string;
  adequate_rest: boolean | null;
  alcohol_test_status: HealthCheckStatus;
  alcohol_test_remarks?: string;
  temperature_check_status: HealthCheckStatus;
  temperature_value?: number;
  fit_for_duty: boolean;
  medication_status: boolean;
  medication_remarks?: string;
  no_health_impairment: boolean;
  fatigue_checklist_completed: boolean;
  fatigue_remarks?: string;
}

// Documentation Compliance

export interface DocumentationCompliance {
  id: string;
  inspection: string;
  
  // Documentation checks
  certificate_of_fitness: 'valid' | 'invalid';
  certificate_of_fitness_valid?: 'yes' | 'no';
  road_tax_valid: boolean;
  insurance_valid: boolean;
  trip_authorization_signed: boolean;
  logbook_present: boolean;
  driver_handbook_present: boolean;
  permits_valid: boolean;
  ppe_available: boolean;
  route_familiarity: boolean;
  emergency_procedures_known: boolean;
  gps_activated: boolean;
  safety_briefing_provided: boolean | string;
  rtsa_clearance: boolean | string;
  emergency_contact: string;
  emergency_contact_employer?: string;
  emergency_contact_government?: string;
  time_briefing_conducted?: string;
  
  created_at: string;
  updated_at: string;
}

export interface CreateDocumentationData {
  inspection: string;
  certificate_of_fitness: 'valid' | 'invalid';
  certificate_of_fitness_valid?: 'yes' | 'no';
  road_tax_valid: boolean;
  insurance_valid: boolean;
  trip_authorization_signed: boolean;
  logbook_present: boolean;
  driver_handbook_present: boolean;
  permits_valid: boolean;
  ppe_available: boolean;
  route_familiarity: boolean;
  emergency_procedures_known: boolean;
  gps_activated: boolean;
  safety_briefing_provided: boolean | string;
  rtsa_clearance: boolean | string;
  emergency_contact: string;
  emergency_contact_employer?: string;
  emergency_contact_government?: string;
  time_briefing_conducted?: string;
}

// API Response Types

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface APIResponse<T> {
  data?: T;
  error?: string;
}

// Pre-Trip Score Summary

export type RiskStatus = 'no_risk' | 'very_low_risk' | 'low_risk' | 'high_risk';

export type SectionRiskLevel = 'no_risk' | 'very_low_risk' | 'low_risk' | 'high_risk';

export interface SectionScoreSummary {
  section: string;
  score: number;
  max: number;
  section_percentage: number; // Percentage within this section (score/max * 100)
  total_percentage: number; // Percentage of total prechecklist (score/64 * 100)
  max_weight: number; // Max percentage this section can contribute
  risk_level: SectionRiskLevel;
  risk_display: string;
  questions?: number;
  subtotal?: string;
}

export interface PreTripScoreSummary {
  id: string;
  inspection: string;
  
  // Section scores with percentages and risk levels
  health_fitness_score: number;
  health_fitness_max: number;
  health_fitness_questions?: number;
  health_fitness_percentage?: number;
  health_fitness_risk?: SectionRiskLevel;
  
  documentation_score: number;
  documentation_max: number;
  documentation_questions?: number;
  documentation_percentage?: number;
  documentation_risk?: SectionRiskLevel;
  
  vehicle_exterior_score: number;
  vehicle_exterior_max: number;
  vehicle_exterior_questions?: number;
  vehicle_exterior_percentage?: number;
  vehicle_exterior_risk?: SectionRiskLevel;
  
  engine_fluid_score: number;
  engine_fluid_max: number;
  engine_fluid_questions?: number;
  engine_fluid_percentage?: number;
  engine_fluid_risk?: SectionRiskLevel;
  
  interior_cabin_score: number;
  interior_cabin_max: number;
  interior_cabin_questions?: number;
  interior_cabin_percentage?: number;
  interior_cabin_risk?: SectionRiskLevel;
  
  functional_score: number;
  functional_max: number;
  functional_questions?: number;
  functional_percentage?: number;
  functional_risk?: SectionRiskLevel;
  
  safety_equipment_score: number;
  safety_equipment_max: number;
  safety_equipment_questions?: number;
  safety_equipment_percentage?: number;
  safety_equipment_risk?: SectionRiskLevel;
  
  brakes_steering_score?: number;
  brakes_steering_max?: number;
  brakes_steering_questions?: number;
  brakes_steering_percentage?: number;
  brakes_steering_risk?: SectionRiskLevel;
  
  // Overall scores
  total_score: number;
  max_possible_score: number;
  total_questions?: number;
  total_prechecklist_questions?: number; // Always 64
  section_weights?: Record<string, number>; // Weight of each section as % of total
  score_percentage: number;
  score_level: 'excellent' | 'good' | 'fair' | 'poor';
  score_level_display?: string;
  risk_status?: RiskStatus;
  risk_status_display?: string;
  
  // Critical failures
  critical_failures: string[];
  has_critical_failures: boolean;
  
  // Travel clearance
  is_cleared_for_travel: boolean;
  clearance_notes: string;
  
  // Computed
  section_summary?: SectionScoreSummary[];
  total_summary?: {
    total_score: number;
    max_possible_score: number;
    total_questions: number;
    score_percentage: number;
    risk_status: RiskStatus;
    risk_status_display?: string;
  };
  
  created_at: string;
  updated_at: string;
}

// Post-Checklist Score Summary
export interface PostChecklistScoreSummary {
  id: string;
  inspection: string;
  
  // Trip Behavior Monitoring (12 questions)
  trip_behavior_score: number;
  trip_behavior_max: number;
  trip_behavior_questions: number;
  trip_behavior_percentage: number;
  trip_behavior_risk: SectionRiskLevel;
  trip_behavior_risk_display: string;
  
  // Driving Behavior Check (11 questions)
  driving_behavior_score: number;
  driving_behavior_max: number;
  driving_behavior_questions: number;
  driving_behavior_percentage: number;
  driving_behavior_risk: SectionRiskLevel;
  driving_behavior_risk_display: string;
  
  // Post-Trip Report (5 questions)
  post_trip_report_score: number;
  post_trip_report_max: number;
  post_trip_report_questions: number;
  post_trip_report_percentage: number;
  post_trip_report_risk: SectionRiskLevel;
  post_trip_report_risk_display: string;
  
  // Totals
  total_score: number;
  max_possible_score: number;
  total_questions: number;
  total_postchecklist_questions: number;
  score_percentage: number;
  risk_status: SectionRiskLevel;
  risk_status_display: string;
  
  section_summary?: Array<{
    section: string;
    score: number;
    max: number;
    questions: number;
    percentage: number;
    risk_level: SectionRiskLevel;
    risk_display: string;
  }>;
  
  created_at: string;
  updated_at: string;
}

// Final Risk Level
export type FinalRiskLevel = 'no_risk' | 'very_low_risk' | 'low_risk' | 'high_risk';

// Final Status
export type FinalStatus = 'passed' | 'failed' | 'needs_review';

// Final Score Summary (Pre-Checklist 50% + Post-Checklist 50%)
export interface FinalScoreSummary {
  id: string;
  inspection: string;
  
  // Pre-Checklist component (50%)
  pre_checklist_score: number;
  pre_checklist_max: number;
  pre_checklist_percentage: number;
  pre_checklist_weighted: number;
  
  // Post-Checklist component (50%)
  post_checklist_score: number;
  post_checklist_max: number;
  post_checklist_percentage: number;
  post_checklist_weighted: number;
  
  // Final Results
  final_percentage: number;
  final_risk_level: FinalRiskLevel;
  final_risk_display: string;
  final_status: FinalStatus;
  final_status_display: string;
  final_comment: string;
  
  // Detailed breakdown
  breakdown?: {
    pre_checklist: {
      name: string;
      weight: number;
      score: number;
      max: number;
      percentage: number;
      weighted_contribution: number;
      sections: Array<{
        section: string;
        score: number;
        max: number;
        questions: number;
        percentage: number;
        risk_level: SectionRiskLevel;
        risk_display: string;
      }>;
    };
    post_checklist: {
      name: string;
      weight: number;
      score: number;
      max: number;
      percentage: number;
      weighted_contribution: number;
      sections: Array<{
        section: string;
        score: number;
        max: number;
        questions: number;
        percentage: number;
        risk_level: SectionRiskLevel;
        risk_display: string;
      }>;
    };
    final: {
      percentage: number;
      risk_level: FinalRiskLevel;
      risk_display: string;
      status: FinalStatus;
      status_display: string;
      comment: string;
    };
  };
  
  created_at: string;
  updated_at: string;
}
