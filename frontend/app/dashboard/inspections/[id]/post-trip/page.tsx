'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { isAuthenticated } from '@/lib/api/auth';
import ProgressTracker from '../../components/ProgressTracker';
import { RadioOption } from '../../components/FormComponents';

interface PostTripFormData {
  // Form 10: Trip Behavior Monitoring
  behaviors: Array<{
    behavior: string;
    status: 'compliant' | 'violation' | 'none' | null;
    notes: string;
    points: number;
  }>;
  
  // Form 11: Driving Behavior Check
  driving_behaviors: Array<{
    behavior: string;
    status: boolean | null;
    remarks: string;
  }>;
  
  // Form 12: Post-Trip Report
  vehicle_fault_reported: boolean | null;
  fault_notes: string;
  final_inspection_signed: boolean | null;
  compliance_with_policy: boolean | null;
  attitude_cooperation: boolean | null;
  incidents_recorded: boolean | null;
  incident_notes: string;
  total_trip_duration: string;
  
  // Form 13: Risk Score (auto-calculated)
  // Form 14: Corrective Measures
  corrective_measures: Array<{
    measure_type: string;
    required: boolean;
    due_date: string;
    completed: boolean;
    completed_date: string;
    notes: string;
  }>;
  
  // Form 15: Enforcement Actions
  enforcement_actions: Array<{
    action_type: string;
    is_applied: boolean;
    start_date: string;
    end_date: string;
    notes: string;
  }>;
  
  // Form 16: Supervisor Remarks
  supervisor_remarks: string;
  recommendation: string;
  
  // Form 17: Evaluation Summary
  pre_trip_score: number | null;
  driving_conduct_score: number | null;
  incident_management_score: number | null;
  post_trip_feedback_score: number | null;
  compliance_documentation_score: number | null;
  comments: string;
  
  // Form 18: Driver Sign-Off
  driver_signature: string;
}

const TOTAL_STEPS = 9;
const VIOLATION_POINTS: Record<string, number> = {
  'Speed in School Zones (≤40 km/hr)': 5,
  'Speed in Market Areas (≤40 km/hr)': 5,
  'Max Speed on Open Road': 3,
  'Railway Crossing Stop': 10,
  'Toll Gate Stop': 2,
  'Hazardous Zone Speeding': 10,
  'Excessive Continuous Driving (>4 hrs)': 8,
  'Traffic Infractions (RTSA/Police)': 10,
  'Incidents/Accidents': 15,
  'Takes Scheduled Breaks (every 2 hours)': 3,
  'Reports Fatigue/Sleepiness Immediately': 5,
  'Uses Rest Stops and Designated Parking Areas': 2,
};

export default function PostTripWizard() {
  const router = useRouter();
  const params = useParams();
  const inspectionId = params.id as string;
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  const [formData, setFormData] = useState<PostTripFormData>({
    behaviors: Object.keys(VIOLATION_POINTS).map(behavior => ({
      behavior,
      status: null,
      notes: '',
      points: VIOLATION_POINTS[behavior],
    })),
    
    driving_behaviors: [
      { behavior: 'Obeys All Traffic Rules and Road Signs', status: null, remarks: '' },
      { behavior: 'Maintains Safe Speed and Following Distance', status: null, remarks: '' },
      { behavior: 'Avoids Harsh Acceleration, Braking, Cornering', status: null, remarks: '' },
      { behavior: 'Avoids Phone Use/Distraction While Driving', status: null, remarks: '' },
      { behavior: 'Keeps Headlights On During Poor Visibility', status: null, remarks: '' },
      { behavior: 'Monitors Temperature, Oil Pressure, Warning Lights', status: null, remarks: '' },
      { behavior: 'Checks Load Security at Rest Stops', status: null, remarks: '' },
      { behavior: 'Reports Abnormal Sounds, Vibrations, Smoke', status: null, remarks: '' },
      { behavior: 'Avoids Overloading or Unauthorized Passengers', status: null, remarks: '' },
      { behavior: 'Reports Breakdowns or Near Misses Promptly', status: null, remarks: '' },
      { behavior: 'Follows Emergency Procedures for Crashes/Hazards', status: null, remarks: '' },
      { behavior: 'Contacts Control Centre for Route Diversion/Delays', status: null, remarks: '' },
    ],
    
    vehicle_fault_reported: null,
    fault_notes: '',
    final_inspection_signed: null,
    compliance_with_policy: null,
    attitude_cooperation: null,
    incidents_recorded: null,
    incident_notes: '',
    total_trip_duration: '',
    
    corrective_measures: [],
    enforcement_actions: [],
    
    supervisor_remarks: '',
    recommendation: '',
    
    pre_trip_score: null,
    driving_conduct_score: null,
    incident_management_score: null,
    post_trip_feedback_score: null,
    compliance_documentation_score: null,
    comments: '',
    
    driver_signature: '',
  });

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
    }
  }, [router]);

  const calculateRiskScore = () => {
    const totalPoints = formData.behaviors
      .filter(b => b.status === 'violation')
      .reduce((sum, b) => sum + b.points, 0);
    
    let riskLevel = 'Low';
    let color = '#4CAF50';
    
    if (totalPoints >= 10) {
      riskLevel = 'High';
      color = '#f44336';
    } else if (totalPoints >= 4) {
      riskLevel = 'Medium';
      color = '#FF9800';
    }
    
    return { totalPoints, riskLevel, color };
  };

  const calculateOverallScore = () => {
    const scores = [
      formData.pre_trip_score,
      formData.driving_conduct_score,
      formData.incident_management_score,
      formData.post_trip_feedback_score,
      formData.compliance_documentation_score,
    ].filter(s => s !== null) as number[];
    
    if (scores.length === 0) return { average: 0, rating: 'N/A', color: '#999' };
    
    const average = scores.reduce((a, b) => a + b, 0) / scores.length;
    let rating = 'Non-Compliant';
    let color = '#f44336';
    
    if (average >= 4.5) {
      rating = 'Excellent';
      color = '#4CAF50';
    } else if (average >= 3.5) {
      rating = 'Satisfactory';
      color = '#8BC34A';
    } else if (average >= 2.0) {
      rating = 'Needs Improvement';
      color = '#FF9800';
    }
    
    return { average: average.toFixed(2), rating, color };
  };

  const validateStep = (step: number): boolean => {
    setError('');
    
    switch (step) {
      case 1:
        if (!formData.behaviors.every(b => b.status !== null)) {
          setError('Please complete all behavior monitoring items');
          return false;
        }
        break;
      case 2:
        if (!formData.driving_behaviors.every(b => b.status !== null)) {
          setError('Please complete all driving behavior checks');
          return false;
        }
        break;
      case 3:
        if (formData.vehicle_fault_reported === null || formData.final_inspection_signed === null ||
            formData.compliance_with_policy === null || formData.attitude_cooperation === null ||
            formData.incidents_recorded === null || !formData.total_trip_duration.trim()) {
          setError('Please complete all post-trip report fields');
          return false;
        }
        break;
      case 6:
        if (!formData.supervisor_remarks.trim()) {
          setError('Supervisor remarks are required');
          return false;
        }
        break;
      case 7:
        if (formData.pre_trip_score === null || formData.driving_conduct_score === null ||
            formData.incident_management_score === null || formData.post_trip_feedback_score === null ||
            formData.compliance_documentation_score === null) {
          setError('Please complete all evaluation scores');
          return false;
        }
        break;
      case 8:
        if (!formData.driver_signature.trim()) {
          setError('Driver signature is required');
          return false;
        }
        break;
    }
    
    return true;
  };

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(prev => Math.min(prev + 1, TOTAL_STEPS));
      window.scrollTo(0, 0);
    }
  };

  const handlePrevious = () => {
    setError('');
    setCurrentStep(prev => Math.max(prev - 1, 1));
    window.scrollTo(0, 0);
  };

  const handleSubmit = async () => {
    if (!validateStep(currentStep)) return;

    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('access_token');
      const headers = { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      };

      // Save trip behaviors
      for (const behavior of formData.behaviors) {
        await fetch(`http://localhost:8000/api/v1/inspections/${inspectionId}/trip-behaviors/`, {
          method: 'POST',
          headers,
          body: JSON.stringify({
            inspection: inspectionId,
            behavior_item: behavior.behavior,
            status: behavior.status,
            notes: behavior.notes,
            violation_points: behavior.status === 'violation' ? behavior.points : 0,
          }),
        });
      }

      // Save driving behaviors
      for (const behavior of formData.driving_behaviors) {
        await fetch(`http://localhost:8000/api/v1/inspections/${inspectionId}/driving-behaviors/`, {
          method: 'POST',
          headers,
          body: JSON.stringify({
            inspection: inspectionId,
            behavior_item: behavior.behavior,
            compliant: behavior.status,
            remarks: behavior.remarks,
          }),
        });
      }

      // Save post-trip report
      await fetch(`http://localhost:8000/api/v1/inspections/${inspectionId}/post-trip/`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          inspection: inspectionId,
          vehicle_fault_reported: formData.vehicle_fault_reported,
          fault_notes: formData.fault_notes,
          final_inspection_signed: formData.final_inspection_signed,
          compliance_with_policy: formData.compliance_with_policy,
          attitude_cooperation: formData.attitude_cooperation,
          incidents_recorded: formData.incidents_recorded,
          incident_notes: formData.incident_notes,
          total_trip_duration: formData.total_trip_duration,
        }),
      });

      // Save corrective measures
      for (const measure of formData.corrective_measures) {
        await fetch(`http://localhost:8000/api/v1/inspections/${inspectionId}/corrective-measures/`, {
          method: 'POST',
          headers,
          body: JSON.stringify({
            inspection: inspectionId,
            ...measure,
          }),
        });
      }

      // Save enforcement actions
      for (const action of formData.enforcement_actions) {
        await fetch(`http://localhost:8000/api/v1/inspections/${inspectionId}/enforcement-actions/`, {
          method: 'POST',
          headers,
          body: JSON.stringify({
            inspection: inspectionId,
            ...action,
          }),
        });
      }

      // Save supervisor remarks
      await fetch(`http://localhost:8000/api/v1/inspections/${inspectionId}/supervisor-remarks/`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          inspection: inspectionId,
          remarks: formData.supervisor_remarks,
          recommendation: formData.recommendation,
        }),
      });

      // Save evaluation
      await fetch(`http://localhost:8000/api/v1/inspections/${inspectionId}/evaluation/`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          inspection: inspectionId,
          pre_trip_score: formData.pre_trip_score,
          driving_conduct_score: formData.driving_conduct_score,
          incident_management_score: formData.incident_management_score,
          post_trip_feedback_score: formData.post_trip_feedback_score,
          compliance_documentation_score: formData.compliance_documentation_score,
          comments: formData.comments,
        }),
      });

      // Save driver sign-off
      await fetch(`http://localhost:8000/api/v1/inspections/${inspectionId}/sign-offs/`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          inspection: inspectionId,
          signer_type: 'driver',
          signature_data: formData.driver_signature,
        }),
      });

      setSuccess('Post-trip inspection completed successfully! Redirecting...');
      setTimeout(() => {
        router.push('/dashboard/inspections');
      }, 2000);
    } catch (err) {
      setError(`Failed to submit post-trip: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const getFormTitle = () => {
    const titles = [
      'Trip Behavior Monitoring',
      'Driving Behavior Check',
      'Post-Trip Report',
      'Risk Score Summary',
      'Corrective Measures',
      'Enforcement Actions',
      'Supervisor Remarks',
      'Evaluation Summary',
      'Driver Sign-Off'
    ];
    return titles[currentStep - 1];
  };

  const addCorrectiveMeasure = () => {
    setFormData({
      ...formData,
      corrective_measures: [
        ...formData.corrective_measures,
        {
          measure_type: 'Safety Training',
          required: true,
          due_date: '',
          completed: false,
          completed_date: '',
          notes: '',
        },
      ],
    });
  };

  const addEnforcementAction = () => {
    setFormData({
      ...formData,
      enforcement_actions: [
        ...formData.enforcement_actions,
        {
          action_type: 'Verbal Warning',
          is_applied: false,
          start_date: '',
          end_date: '',
          notes: '',
        },
      ],
    });
  };

  const renderForm = () => {
    switch (currentStep) {
      case 1:
        return (
          <div>
            <h2 style={{ color: '#000', marginBottom: '20px' }}>{getFormTitle()}</h2>
            <p style={{ color: '#666', marginBottom: '30px' }}>
              Monitor driver behavior during the trip. Mark violations and add notes.
            </p>
            {formData.behaviors.map((behavior, index) => (
              <div key={index} style={{ marginBottom: '30px', paddingBottom: '20px', borderBottom: '1px solid #e0e0e0' }}>
                <label style={{ display: 'block', fontWeight: '600', color: '#000', marginBottom: '10px' }}>
                  {behavior.behavior} <span style={{ color: '#999', fontSize: '14px' }}>({behavior.points} points)</span>
                </label>
                <div style={{ display: 'flex', gap: '15px', marginBottom: '10px' }}>
                  <RadioOption
                    label="Compliant"
                    value="compliant"
                    selected={behavior.status === 'compliant'}
                    onChange={() => {
                      const updated = [...formData.behaviors];
                      updated[index].status = 'compliant';
                      setFormData({ ...formData, behaviors: updated });
                    }}
                  />
                  <RadioOption
                    label="Violation"
                    value="violation"
                    selected={behavior.status === 'violation'}
                    onChange={() => {
                      const updated = [...formData.behaviors];
                      updated[index].status = 'violation';
                      setFormData({ ...formData, behaviors: updated });
                    }}
                  />
                  <RadioOption
                    label="None"
                    value="none"
                    selected={behavior.status === 'none'}
                    onChange={() => {
                      const updated = [...formData.behaviors];
                      updated[index].status = 'none';
                      setFormData({ ...formData, behaviors: updated });
                    }}
                  />
                </div>
                <textarea
                  className="input"
                  rows={2}
                  placeholder="Notes..."
                  value={behavior.notes}
                  onChange={(e) => {
                    const updated = [...formData.behaviors];
                    updated[index].notes = e.target.value;
                    setFormData({ ...formData, behaviors: updated });
                  }}
                  style={{ marginTop: '10px' }}
                />
              </div>
            ))}
          </div>
        );

      case 2:
        return (
          <div>
            <h2 style={{ color: '#000', marginBottom: '20px' }}>{getFormTitle()}</h2>
            {formData.driving_behaviors.map((behavior, index) => (
              <div key={index} style={{ marginBottom: '30px' }}>
                <label style={{ display: 'block', fontWeight: '600', color: '#000', marginBottom: '10px' }}>
                  {behavior.behavior}
                </label>
                <div style={{ display: 'flex', gap: '15px', marginBottom: '10px' }}>
                  <RadioOption
                    label="Yes"
                    value="yes"
                    selected={behavior.status === true}
                    onChange={() => {
                      const updated = [...formData.driving_behaviors];
                      updated[index].status = true;
                      setFormData({ ...formData, driving_behaviors: updated });
                    }}
                  />
                  <RadioOption
                    label="No"
                    value="no"
                    selected={behavior.status === false}
                    onChange={() => {
                      const updated = [...formData.driving_behaviors];
                      updated[index].status = false;
                      setFormData({ ...formData, driving_behaviors: updated });
                    }}
                  />
                </div>
                <textarea
                  className="input"
                  rows={2}
                  placeholder="Remarks..."
                  value={behavior.remarks}
                  onChange={(e) => {
                    const updated = [...formData.driving_behaviors];
                    updated[index].remarks = e.target.value;
                    setFormData({ ...formData, driving_behaviors: updated });
                  }}
                  style={{ marginTop: '10px' }}
                />
              </div>
            ))}
          </div>
        );

      case 3:
        return (
          <div>
            <h2 style={{ color: '#000', marginBottom: '20px' }}>{getFormTitle()}</h2>
            
            <div style={{ marginBottom: '25px' }}>
              <label style={{ display: 'block', fontWeight: '600', color: '#000', marginBottom: '10px' }}>
                Vehicle Fault Report Submitted *
              </label>
              <div style={{ display: 'flex', gap: '15px', marginBottom: '10px' }}>
                <RadioOption
                  label="Yes"
                  value="yes"
                  selected={formData.vehicle_fault_reported === true}
                  onChange={() => setFormData({ ...formData, vehicle_fault_reported: true })}
                />
                <RadioOption
                  label="No"
                  value="no"
                  selected={formData.vehicle_fault_reported === false}
                  onChange={() => setFormData({ ...formData, vehicle_fault_reported: false })}
                />
              </div>
              <textarea
                className="input"
                rows={3}
                placeholder="Fault Notes..."
                value={formData.fault_notes}
                onChange={(e) => setFormData({ ...formData, fault_notes: e.target.value })}
                style={{ marginTop: '10px' }}
              />
            </div>

            {[
              { key: 'final_inspection_signed', label: 'Final Inspection Signed Off' },
              { key: 'compliance_with_policy', label: 'Compliance with Company Safety Policy' },
              { key: 'attitude_cooperation', label: 'Attitude and Cooperation During Journey' },
              { key: 'incidents_recorded', label: 'Any Incidents/Near Misses or Accidents Recorded & Reported' },
            ].map(({ key, label }) => (
              <div key={key} style={{ marginBottom: '25px' }}>
                <label style={{ display: 'block', fontWeight: '600', color: '#000', marginBottom: '10px' }}>
                  {label} *
                </label>
                <div style={{ display: 'flex', gap: '15px' }}>
                  <RadioOption
                    label="Yes"
                    value="yes"
                    selected={formData[key as keyof PostTripFormData] === true}
                    onChange={() => setFormData({ ...formData, [key]: true })}
                  />
                  <RadioOption
                    label="No"
                    value="no"
                    selected={formData[key as keyof PostTripFormData] === false}
                    onChange={() => setFormData({ ...formData, [key]: false })}
                  />
                </div>
              </div>
            ))}

            <div style={{ marginBottom: '20px' }}>
              <label className="label">Incident Notes</label>
              <textarea
                className="input"
                rows={3}
                placeholder="Describe any incidents..."
                value={formData.incident_notes}
                onChange={(e) => setFormData({ ...formData, incident_notes: e.target.value })}
              />
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label className="label">Total Trip Duration *</label>
              <input
                type="text"
                className="input"
                placeholder="e.g., 6 hours 30 minutes"
                value={formData.total_trip_duration}
                onChange={(e) => setFormData({ ...formData, total_trip_duration: e.target.value })}
              />
            </div>
          </div>
        );

      case 4:
        const riskScore = calculateRiskScore();
        return (
          <div>
            <h2 style={{ color: '#000', marginBottom: '20px' }}>{getFormTitle()}</h2>
            <p style={{ color: '#666', marginBottom: '30px' }}>
              Auto-calculated based on trip behavior monitoring
            </p>
            
            <div style={{ 
              padding: '30px', 
              backgroundColor: '#f5f5f5', 
              borderRadius: '8px',
              marginBottom: '30px'
            }}>
              <h3 style={{ color: '#000', marginBottom: '20px' }}>This Trip</h3>
              <div style={{ fontSize: '48px', fontWeight: 'bold', color: riskScore.color, marginBottom: '10px' }}>
                {riskScore.totalPoints} points
              </div>
              <div style={{ 
                fontSize: '24px', 
                fontWeight: '600', 
                color: riskScore.color,
                padding: '10px 20px',
                backgroundColor: '#fff',
                borderRadius: '8px',
                display: 'inline-block'
              }}>
                Risk Level: {riskScore.riskLevel}
              </div>
            </div>

            <div style={{ 
              padding: '20px', 
              backgroundColor: '#e3f2fd', 
              borderRadius: '8px',
              border: '1px solid #2196F3'
            }}>
              <h4 style={{ color: '#1976D2', marginBottom: '10px' }}>Risk Level Guide</h4>
              <ul style={{ margin: 0, paddingLeft: '20px', color: '#000' }}>
                <li><span style={{ color: '#4CAF50', fontWeight: 'bold' }}>Low (0-3 points)</span> - Excellent performance</li>
                <li><span style={{ color: '#FF9800', fontWeight: 'bold' }}>Medium (4-9 points)</span> - Requires monitoring</li>
                <li><span style={{ color: '#f44336', fontWeight: 'bold' }}>High (10+ points)</span> - Immediate action required</li>
              </ul>
            </div>
          </div>
        );

      case 5:
        return (
          <div>
            <h2 style={{ color: '#000', marginBottom: '20px' }}>{getFormTitle()}</h2>
            <p style={{ color: '#666', marginBottom: '20px' }}>
              Add corrective measures if risk level is Medium or High
            </p>
            
            {formData.corrective_measures.map((measure, index) => (
              <div key={index} style={{ 
                padding: '20px', 
                backgroundColor: '#f9f9f9', 
                borderRadius: '8px',
                marginBottom: '20px',
                border: '1px solid #e0e0e0'
              }}>
                <div style={{ marginBottom: '15px' }}>
                  <label className="label">Measure Type</label>
                  <select
                    className="input"
                    value={measure.measure_type}
                    onChange={(e) => {
                      const updated = [...formData.corrective_measures];
                      updated[index].measure_type = e.target.value;
                      setFormData({ ...formData, corrective_measures: updated });
                    }}
                  >
                    <option value="Safety Training">Safety Training</option>
                    <option value="Performance Review">Performance Review</option>
                    <option value="Probationary Period">Probationary Period</option>
                    <option value="Policy Acknowledgment">Policy Acknowledgment</option>
                  </select>
                </div>
                <div style={{ marginBottom: '15px' }}>
                  <label className="label">Due Date</label>
                  <input
                    type="date"
                    className="input"
                    value={measure.due_date}
                    onChange={(e) => {
                      const updated = [...formData.corrective_measures];
                      updated[index].due_date = e.target.value;
                      setFormData({ ...formData, corrective_measures: updated });
                    }}
                  />
                </div>
                <div style={{ marginBottom: '15px' }}>
                  <label className="label">Notes</label>
                  <textarea
                    className="input"
                    rows={2}
                    value={measure.notes}
                    onChange={(e) => {
                      const updated = [...formData.corrective_measures];
                      updated[index].notes = e.target.value;
                      setFormData({ ...formData, corrective_measures: updated });
                    }}
                  />
                </div>
                <button
                  onClick={() => {
                    const updated = formData.corrective_measures.filter((_, i) => i !== index);
                    setFormData({ ...formData, corrective_measures: updated });
                  }}
                  className="button-secondary"
                  style={{ width: 'auto', fontSize: '14px', padding: '6px 12px' }}
                >
                  Remove
                </button>
              </div>
            ))}
            
            <button
              onClick={addCorrectiveMeasure}
              className="button-primary"
              style={{ width: 'auto' }}
            >
              Add Corrective Measure
            </button>
            
            {formData.corrective_measures.length === 0 && (
              <p style={{ color: '#666', marginTop: '20px', fontStyle: 'italic' }}>
                Skip if no corrective measures required
              </p>
            )}
          </div>
        );

      case 6:
        return (
          <div>
            <h2 style={{ color: '#000', marginBottom: '20px' }}>{getFormTitle()}</h2>
            <p style={{ color: '#666', marginBottom: '20px' }}>
              Add enforcement actions if violations occurred
            </p>
            
            {formData.enforcement_actions.map((action, index) => (
              <div key={index} style={{ 
                padding: '20px', 
                backgroundColor: '#fff3e0', 
                borderRadius: '8px',
                marginBottom: '20px',
                border: '1px solid #FF9800'
              }}>
                <div style={{ marginBottom: '15px' }}>
                  <label className="label">Action Type</label>
                  <select
                    className="input"
                    value={action.action_type}
                    onChange={(e) => {
                      const updated = [...formData.enforcement_actions];
                      updated[index].action_type = e.target.value;
                      setFormData({ ...formData, enforcement_actions: updated });
                    }}
                  >
                    <option value="Verbal Warning">Verbal Warning</option>
                    <option value="Written Warning">Written Warning</option>
                    <option value="Suspension">Suspension</option>
                    <option value="Final Warning">Final Warning</option>
                    <option value="Termination">Termination</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
                <div style={{ marginBottom: '15px' }}>
                  <label className="label">Start Date</label>
                  <input
                    type="date"
                    className="input"
                    value={action.start_date}
                    onChange={(e) => {
                      const updated = [...formData.enforcement_actions];
                      updated[index].start_date = e.target.value;
                      setFormData({ ...formData, enforcement_actions: updated });
                    }}
                  />
                </div>
                {action.action_type === 'Suspension' && (
                  <div style={{ marginBottom: '15px' }}>
                    <label className="label">End Date</label>
                    <input
                      type="date"
                      className="input"
                      value={action.end_date}
                      onChange={(e) => {
                        const updated = [...formData.enforcement_actions];
                        updated[index].end_date = e.target.value;
                        setFormData({ ...formData, enforcement_actions: updated });
                      }}
                    />
                  </div>
                )}
                <div style={{ marginBottom: '15px' }}>
                  <label className="label">Notes</label>
                  <textarea
                    className="input"
                    rows={2}
                    value={action.notes}
                    onChange={(e) => {
                      const updated = [...formData.enforcement_actions];
                      updated[index].notes = e.target.value;
                      setFormData({ ...formData, enforcement_actions: updated });
                    }}
                  />
                </div>
                <button
                  onClick={() => {
                    const updated = formData.enforcement_actions.filter((_, i) => i !== index);
                    setFormData({ ...formData, enforcement_actions: updated });
                  }}
                  className="button-secondary"
                  style={{ width: 'auto', fontSize: '14px', padding: '6px 12px' }}
                >
                  Remove
                </button>
              </div>
            ))}
            
            <button
              onClick={addEnforcementAction}
              className="button-primary"
              style={{ width: 'auto' }}
            >
              Add Enforcement Action
            </button>
            
            {formData.enforcement_actions.length === 0 && (
              <p style={{ color: '#666', marginTop: '20px', fontStyle: 'italic' }}>
                Skip if no enforcement actions required
              </p>
            )}
          </div>
        );

      case 7:
        return (
          <div>
            <h2 style={{ color: '#000', marginBottom: '20px' }}>{getFormTitle()}</h2>
            
            <div style={{ marginBottom: '20px' }}>
              <label className="label">Supervisor Remarks *</label>
              <textarea
                className="input"
                rows={5}
                placeholder="Enter detailed supervisor remarks..."
                value={formData.supervisor_remarks}
                onChange={(e) => setFormData({ ...formData, supervisor_remarks: e.target.value })}
              />
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label className="label">Recommendation</label>
              <textarea
                className="input"
                rows={3}
                placeholder="Enter recommendations for driver..."
                value={formData.recommendation}
                onChange={(e) => setFormData({ ...formData, recommendation: e.target.value })}
              />
            </div>
          </div>
        );

      case 8:
        const overallScore = calculateOverallScore();
        return (
          <div>
            <h2 style={{ color: '#000', marginBottom: '20px' }}>{getFormTitle()}</h2>
            <p style={{ color: '#666', marginBottom: '30px' }}>
              Rate each area on a scale of 1-5
            </p>
            
            {[
              { key: 'pre_trip_score', label: 'Pre-Trip Inspection Score' },
              { key: 'driving_conduct_score', label: 'Driving Conduct Score' },
              { key: 'incident_management_score', label: 'Incident Management Score' },
              { key: 'post_trip_feedback_score', label: 'Post-Trip Feedback & Reporting Score' },
              { key: 'compliance_documentation_score', label: 'Compliance & Documentation Score' },
            ].map(({ key, label }) => (
              <div key={key} style={{ marginBottom: '25px' }}>
                <label style={{ display: 'block', fontWeight: '600', color: '#000', marginBottom: '10px' }}>
                  {label} *
                </label>
                <div style={{ display: 'flex', gap: '10px' }}>
                  {[1, 2, 3, 4, 5].map(score => (
                    <button
                      key={score}
                      onClick={() => setFormData({ ...formData, [key]: score })}
                      style={{
                        width: '50px',
                        height: '50px',
                        borderRadius: '50%',
                        border: `2px solid ${formData[key as keyof PostTripFormData] === score ? '#2196F3' : '#ccc'}`,
                        backgroundColor: formData[key as keyof PostTripFormData] === score ? '#2196F3' : '#fff',
                        color: formData[key as keyof PostTripFormData] === score ? '#fff' : '#000',
                        fontSize: '20px',
                        fontWeight: 'bold',
                        cursor: 'pointer',
                      }}
                    >
                      {score}
                    </button>
                  ))}
                </div>
              </div>
            ))}

            <div style={{ 
              padding: '30px', 
              backgroundColor: '#f5f5f5', 
              borderRadius: '8px',
              marginTop: '30px',
              marginBottom: '30px'
            }}>
              <h3 style={{ color: '#000', marginBottom: '15px' }}>Overall Safety Performance</h3>
              <div style={{ fontSize: '36px', fontWeight: 'bold', color: overallScore.color, marginBottom: '10px' }}>
                {overallScore.average}
              </div>
              <div style={{ 
                fontSize: '20px', 
                fontWeight: '600', 
                color: overallScore.color
              }}>
                {overallScore.rating}
              </div>
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label className="label">Comments</label>
              <textarea
                className="input"
                rows={4}
                placeholder="Additional comments..."
                value={formData.comments}
                onChange={(e) => setFormData({ ...formData, comments: e.target.value })}
              />
            </div>
          </div>
        );

      case 9:
        return (
          <div>
            <h2 style={{ color: '#000', marginBottom: '20px' }}>{getFormTitle()}</h2>
            
            <div style={{ 
              padding: '20px', 
              backgroundColor: '#fff3cd', 
              borderRadius: '8px',
              marginBottom: '30px',
              border: '1px solid #ffc107'
            }}>
              <h3 style={{ color: '#856404', marginBottom: '10px' }}>Declaration</h3>
              <p style={{ color: '#856404', marginBottom: '0' }}>
                I acknowledge that the information provided in this post-trip report is accurate and complete. 
                I understand that any violations noted may result in corrective actions or enforcement measures.
              </p>
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label className="label">Driver Name (Auto-filled)</label>
              <input
                type="text"
                className="input"
                value="Current Driver"
                disabled
                style={{ backgroundColor: '#f5f5f5' }}
              />
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label className="label">Signature *</label>
              <input
                type="text"
                className="input"
                placeholder="Type your full name as signature"
                value={formData.driver_signature}
                onChange={(e) => setFormData({ ...formData, driver_signature: e.target.value })}
              />
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label className="label">Date/Time</label>
              <input
                type="text"
                className="input"
                value={new Date().toLocaleString()}
                disabled
                style={{ backgroundColor: '#f5f5f5' }}
              />
            </div>

            <div style={{ 
              marginTop: '30px', 
              padding: '20px', 
              backgroundColor: '#e8f5e9', 
              borderRadius: '8px',
              border: '1px solid #4CAF50'
            }}>
              <h3 style={{ color: '#2e7d32', marginBottom: '10px' }}>Ready to Submit</h3>
              <p style={{ color: '#000', marginBottom: '0' }}>
                You&apos;ve completed all sections of the post-trip inspection. Click &quot;Submit Post-Trip&quot; to finalize.
              </p>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <div>
          <h1>Post-Trip Inspection</h1>
          <p style={{ color: '#666', marginTop: '5px' }}>
            Complete all post-trip sections after journey completion
          </p>
        </div>
        <button 
          onClick={() => router.push('/dashboard/inspections')} 
          className="button-secondary"
          style={{ width: 'auto' }}
        >
          Cancel
        </button>
      </div>

      <div className="profile-card">
        <ProgressTracker 
          currentStep={currentStep} 
          totalSteps={TOTAL_STEPS}
        />

        {error && <div className="alert alert-error" style={{ marginBottom: '20px' }}>{error}</div>}
        {success && <div className="alert alert-success" style={{ marginBottom: '20px' }}>{success}</div>}

        {renderForm()}

        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          marginTop: '30px',
          paddingTop: '20px',
          borderTop: '1px solid #e0e0e0'
        }}>
          <button
            onClick={handlePrevious}
            disabled={currentStep === 1 || loading}
            className="button-secondary"
            style={{ 
              width: 'auto',
              opacity: currentStep === 1 ? 0.5 : 1,
              cursor: currentStep === 1 ? 'not-allowed' : 'pointer',
            }}
          >
            Previous
          </button>

          {currentStep < TOTAL_STEPS ? (
            <button
              onClick={handleNext}
              disabled={loading}
              className="button-primary"
              style={{ width: 'auto' }}
            >
              Next
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={loading}
              className="button-primary"
              style={{ width: 'auto' }}
            >
              {loading ? 'Submitting...' : 'Submit Post-Trip'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
