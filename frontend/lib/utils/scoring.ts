/**
 * Pre-Checklist Scoring Constants and Utilities
 * Matches backend: backend/inspections/models/scoring.py
 * 
 * Formula: Section Max % = (questions × 100) / TOTAL_PRECHECKLIST_QUESTIONS
 *          Earned % = (earned × 100) / TOTAL_PRECHECKLIST_QUESTIONS
 */

// Total questions across all 8 pre-checklist forms
export const TOTAL_PRECHECKLIST_QUESTIONS = 63;

// Section question counts
export const SECTION_QUESTIONS = {
  health_fitness: 7,        // 7 × 100 / 63 = 11.11%
  documentation: 16,        // 16 × 100 / 63 = 25.40%
  vehicle_exterior: 7,      // 7 × 100 / 63 = 11.11%
  engine_fluid: 6,          // 6 × 100 / 63 = 9.52%
  interior_cabin: 6,        // 6 × 100 / 63 = 9.52%
  functional: 4,            // 4 × 100 / 63 = 6.35%
  safety_equipment: 8,      // 8 × 100 / 63 = 12.70%
  brakes_steering: 9,       // 9 × 100 / 63 = 14.29%
} as const;

// Section weights as percentage of total (calculated from question counts)
// Formula: (questions × 100) / TOTAL_PRECHECKLIST_QUESTIONS
export const SECTION_WEIGHTS = {
  health_fitness: 11.11,
  documentation: 25.40,
  vehicle_exterior: 11.11,
  engine_fluid: 9.52,
  interior_cabin: 9.52,
  functional: 6.35,
  safety_equipment: 12.70,
  brakes_steering: 14.29,
} as const;

// Section display names
export const SECTION_NAMES = {
  health_fitness: 'Health & Fitness',
  documentation: 'Doc/Compliance',
  vehicle_exterior: 'Vehicle Exterior',
  engine_fluid: 'Engine/Fluids',
  interior_cabin: 'Interior/Cabin',
  functional: 'Functional Checks',
  safety_equipment: 'Safety Equipment',
  brakes_steering: 'Brakes/Steering',
} as const;

export type SectionKey = keyof typeof SECTION_QUESTIONS;

export type RiskLevel = 'no_risk' | 'very_low_risk' | 'low_risk' | 'high_risk';

export interface SectionScore {
  section: SectionKey;
  name: string;
  questions: number;
  earned: number;
  maxWeight: number;       // Max % this section contributes (questions × 100 / 63)
  earnedWeight: number;    // Earned % contribution (earned × 100 / 63)
  sectionPercentage: number; // Within-section % (earned / questions × 100)
  riskLevel: RiskLevel;
  riskDisplay: string;
}

export interface TotalScore {
  totalQuestions: number;
  totalEarned: number;
  totalMaxWeight: number;  // Always 100%
  totalEarnedWeight: number; // Sum of all section earned weights
  overallPercentage: number;
  riskLevel: RiskLevel;
  riskDisplay: string;
}

/**
 * Get risk level based on section percentage (within-section)
 */
export function getRiskLevel(percentage: number): RiskLevel {
  if (percentage >= 100) return 'no_risk';
  if (percentage >= 85) return 'very_low_risk';
  if (percentage >= 70) return 'low_risk';
  return 'high_risk';
}

/**
 * Get display name for risk level
 */
export function getRiskDisplay(level: RiskLevel): string {
  const displays: Record<RiskLevel, string> = {
    no_risk: 'No Risk',
    very_low_risk: 'Very Low Risk',
    low_risk: 'Low Risk',
    high_risk: 'High Risk',
  };
  return displays[level];
}

/**
 * Get risk level styling
 */
export function getRiskStyle(level: RiskLevel): { bg: string; text: string; label: string } {
  switch (level) {
    case 'no_risk':
      return { bg: '#e8f5e9', text: '#2e7d32', label: 'No Risk' };
    case 'very_low_risk':
      return { bg: '#e3f2fd', text: '#1565c0', label: 'Very Low Risk' };
    case 'low_risk':
      return { bg: '#fff3e0', text: '#ef6c00', label: 'Low Risk' };
    case 'high_risk':
      return { bg: '#ffebee', text: '#c62828', label: 'High Risk' };
  }
}

/**
 * Calculate section score
 * @param section - Section key
 * @param earned - Number of questions answered positively
 */
export function calculateSectionScore(section: SectionKey, earned: number): SectionScore {
  const questions = SECTION_QUESTIONS[section];
  const name = SECTION_NAMES[section];
  
  // Max weight = (questions × 100) / 63
  const maxWeight = (questions * 100) / TOTAL_PRECHECKLIST_QUESTIONS;
  
  // Earned weight = (earned × 100) / 63
  const earnedWeight = (earned * 100) / TOTAL_PRECHECKLIST_QUESTIONS;
  
  // Section percentage = (earned / questions) × 100
  const sectionPercentage = questions > 0 ? (earned / questions) * 100 : 0;
  
  const riskLevel = getRiskLevel(sectionPercentage);
  const riskDisplay = getRiskDisplay(riskLevel);
  
  return {
    section,
    name,
    questions,
    earned,
    maxWeight: Number(maxWeight.toFixed(2)),
    earnedWeight: Number(earnedWeight.toFixed(2)),
    sectionPercentage: Number(sectionPercentage.toFixed(2)),
    riskLevel,
    riskDisplay,
  };
}

/**
 * Calculate total score from all section scores
 */
export function calculateTotalScore(sectionScores: SectionScore[]): TotalScore {
  const totalQuestions = sectionScores.reduce((sum, s) => sum + s.questions, 0);
  const totalEarned = sectionScores.reduce((sum, s) => sum + s.earned, 0);
  const totalMaxWeight = sectionScores.reduce((sum, s) => sum + s.maxWeight, 0);
  const totalEarnedWeight = sectionScores.reduce((sum, s) => sum + s.earnedWeight, 0);
  
  // Overall percentage = total earned weight (already calculated as % of 63)
  const overallPercentage = totalEarnedWeight;
  
  const riskLevel = getRiskLevel(overallPercentage);
  const riskDisplay = getRiskDisplay(riskLevel);
  
  return {
    totalQuestions,
    totalEarned,
    totalMaxWeight: Number(totalMaxWeight.toFixed(2)),
    totalEarnedWeight: Number(totalEarnedWeight.toFixed(2)),
    overallPercentage: Number(overallPercentage.toFixed(2)),
    riskLevel,
    riskDisplay,
  };
}

/**
 * Calculate live score for a form step
 * Returns { earned, possible, answered, total, sectionPercentage, earnedWeight, maxWeight }
 */
export interface LiveScoreResult {
  earned: number;          // Points earned (1 per question)
  possible: number;        // Max points possible for section
  answered: number;        // Number of questions answered
  total: number;           // Total questions in section
  sectionPercentage: number; // Within-section % (earned/possible × 100)
  earnedWeight: number;    // % of total checklist earned (earned × 100 / 63)
  maxWeight: number;       // Max % this section contributes
  riskLevel: RiskLevel;
  riskDisplay: string;
  riskStyle: { bg: string; text: string; label: string };
}

export function calculateLiveScore(
  section: SectionKey,
  passedCount: number,
  answeredCount: number
): LiveScoreResult {
  const questions = SECTION_QUESTIONS[section];
  const maxWeight = SECTION_WEIGHTS[section];
  
  const earned = passedCount;
  const possible = questions;
  const earnedWeight = (passedCount * 100) / TOTAL_PRECHECKLIST_QUESTIONS;
  const sectionPercentage = answeredCount > 0 ? (passedCount / answeredCount) * 100 : 0;
  const riskLevel = getRiskLevel(sectionPercentage);
  const riskDisplay = getRiskDisplay(riskLevel);
  const riskStyle = getRiskStyle(riskLevel);
  
  return {
    earned,
    possible,
    answered: answeredCount,
    total: questions,
    sectionPercentage: Number(sectionPercentage.toFixed(2)),
    earnedWeight: Number(earnedWeight.toFixed(2)),
    maxWeight,
    riskLevel,
    riskDisplay,
    riskStyle,
  };
}
