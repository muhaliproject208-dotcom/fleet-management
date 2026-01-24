'use client';

import { useRouter, useParams } from 'next/navigation';
import { useEffect, useState, useRef } from 'react';
import { isAuthenticated } from '@/lib/api/auth';
import { getInspection } from '@/lib/api/inspections';
import { PreTripInspectionFull } from '@/lib/api/inspections/types';
import InspectionStatusBadge from '../../components/InspectionStatusBadge';

export default function InspectionReportPage() {
  const router = useRouter();
  const params = useParams();
  const id = params?.id as string;
  const reportRef = useRef<HTMLDivElement>(null);

  const [inspection, setInspection] = useState<PreTripInspectionFull | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }

    const fetchInspectionData = async () => {
      const response = await getInspection(id);

      if (response.error) {
        setError(response.error);
      } else if (response.data) {
        setInspection(response.data);
      }

      setLoading(false);
    };

    void fetchInspectionData();
  }, [router, id]);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    // Use UTC to prevent hydration mismatch between server and client timezones
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric',
      timeZone: 'UTC'
    });
  };

  const handleDownloadPDF = async () => {
    setDownloading(true);
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8000/api/v1/inspections/${id}/download_pdf/`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to generate PDF');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `inspection-report-${inspection?.inspection_id || id}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('PDF download error:', err);
      // Fallback to browser print
      window.print();
    } finally {
      setDownloading(false);
    }
  };

  const getRiskLevelStyle = (level: string) => {
    switch (level) {
      case 'low':
        return { bg: '#f5f5f5', text: '#333', label: 'Low Risk' };
      case 'medium':
        return { bg: '#e0e0e0', text: '#000', label: 'Medium Risk' };
      case 'high':
        return { bg: '#000', text: '#fff', label: 'High Risk' };
      default:
        return { bg: '#f5f5f5', text: '#666', label: level };
    }
  };

  const getPerformanceStyle = (level: string) => {
    switch (level) {
      case 'excellent':
        return { label: 'Excellent', score: '5/5', color: '#2e7d32' };
      case 'satisfactory':
        return { label: 'Satisfactory', score: '4/5', color: '#1976d2' };
      case 'needs_improvement':
        return { label: 'Needs Improvement', score: '3/5', color: '#f57c00' };
      case 'non_compliant':
        return { label: 'Non-Compliant', score: '1/5', color: '#c62828' };
      default:
        return { label: level, score: 'N/A', color: '#666' };
    }
  };

  const formatBehaviorItem = (item: string) => {
    const labels: Record<string, string> = {
      'speed_school_zone': 'Speed in School Zones (≤40 km/hr)',
      'speed_market_area': 'Speed in Market Areas (≤40 km/hr)',
      'max_speed_open_road': 'Max Speed on Open Road',
      'railway_crossing': 'Railway Crossing Stop',
      'toll_gate': 'Toll Gate Stop',
      'hazardous_zone_speed': 'Hazardous Zone Speeding',
      'excessive_driving': 'Excessive Continuous Driving (>4 hrs)',
      'traffic_infractions': 'Traffic Infractions (RTSA/Police)',
      'incidents': 'Incidents/Accidents',
      'scheduled_breaks': 'Takes Scheduled Breaks (every 2 hours)',
      'fatigue_reporting': 'Reports Fatigue/Sleepiness Immediately',
      'rest_stops_usage': 'Uses Rest Stops and Designated Parking Areas',
    };
    return labels[item] || item.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  if (loading) {
    return (
      <div className="container">
        <div className="text-center">
          <div className="spinner" style={{ margin: '0 auto' }}></div>
          <p style={{ marginTop: '20px' }}>Loading report...</p>
        </div>
      </div>
    );
  }

  if (error || !inspection) {
    return (
      <div className="dashboard-container">
        <div className="dashboard-header">
          <h1>Report Not Found</h1>
          <button 
            onClick={() => router.push('/dashboard/inspections')} 
            className="button-secondary"
            style={{ width: 'auto' }}
          >
            Back to Inspections
          </button>
        </div>
        <div className="alert alert-error">{error || 'Report not found'}</div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      {/* Header with Actions */}
      <div className="dashboard-header" style={{ marginBottom: '20px' }}>
        <div>
          <h1>Inspection Report</h1>
          <p style={{ color: '#666', marginTop: '5px' }}>
            {inspection.inspection_id} - {formatDate(inspection.inspection_date)}
          </p>
        </div>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <button 
            onClick={handleDownloadPDF}
            disabled={downloading}
            className="button-primary"
            style={{ 
              width: 'auto',
              backgroundColor: '#000',
              borderColor: '#000',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}
          >
            <span className="material-icons" style={{ fontSize: '18px' }}>download</span>
            {downloading ? 'Generating...' : 'Download PDF'}
          </button>
          <button 
            onClick={() => router.push(`/dashboard/inspections/${inspection.id}`)} 
            className="button-secondary"
            style={{ width: 'auto' }}
          >
            Back to Inspection
          </button>
        </div>
      </div>

      {/* Report Content */}
      <div ref={reportRef} style={{ backgroundColor: '#fff', borderRadius: '8px', overflow: 'hidden' }}>
        {/* Report Header */}
        <div style={{ 
          padding: '30px', 
          borderBottom: '2px solid #000',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
        }}>
          <div>
            <h2 style={{ color: '#000', fontSize: '24px', marginBottom: '10px' }}>
              Fleet Management Inspection Report
            </h2>
            <p style={{ color: '#666' }}>
              Generated on {formatDate(new Date().toISOString())}
            </p>
          </div>
          <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
            <InspectionStatusBadge status={inspection.status} size="lg" />
            {inspection.evaluation && (
              <div style={{
                padding: '10px 20px',
                backgroundColor: '#000',
                color: '#fff',
                borderRadius: '8px',
                fontWeight: '600',
              }}>
                Overall: {getPerformanceStyle(inspection.evaluation.overall_performance).label}
              </div>
            )}
            {inspection.risk_score && (
              <div style={{
                padding: '10px 20px',
                borderRadius: '8px',
                fontWeight: '600',
                ...(() => {
                  const style = getRiskLevelStyle(inspection.risk_score.risk_level);
                  return { backgroundColor: style.bg, color: style.text };
                })(),
              }}>
                Risk: {getRiskLevelStyle(inspection.risk_score.risk_level).label}
              </div>
            )}
          </div>
        </div>

        {/* Driver Performance Summary - Prominent Section */}
        {(inspection.evaluation || inspection.risk_score) && (
          <div style={{ 
            padding: '30px', 
            borderBottom: '1px solid #eee',
          }}>
            <h3 style={{ color: '#000', marginBottom: '25px', fontSize: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span className="material-icons" style={{ fontSize: '24px' }}>person</span>
              Driver Performance Summary - {inspection.driver.full_name}
            </h3>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
              {inspection.evaluation && (
                <div style={{ 
                  padding: '25px', 
                  backgroundColor: '#fff', 
                  borderRadius: '12px',
                  border: '1px solid #e5e7eb',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                }}>
                  <h4 style={{ color: '#374151', fontSize: '14px', marginBottom: '15px', fontWeight: '600' }}>Overall Performance</h4>
                  <div style={{ fontSize: '36px', fontWeight: '700', color: getPerformanceStyle(inspection.evaluation.overall_performance).color, marginBottom: '10px' }}>
                    {getPerformanceStyle(inspection.evaluation.overall_performance).label}
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginTop: '15px' }}>
                    <div>
                      <div style={{ fontSize: '12px', color: '#6b7280' }}>Pre-Trip</div>
                      <div style={{ fontSize: '18px', fontWeight: '600', color: '#000' }}>{inspection.evaluation.pre_trip_inspection_score}/5</div>
                    </div>
                    <div>
                      <div style={{ fontSize: '12px', color: '#6b7280' }}>Driving</div>
                      <div style={{ fontSize: '18px', fontWeight: '600', color: '#000' }}>{inspection.evaluation.driving_conduct_score}/5</div>
                    </div>
                    <div>
                      <div style={{ fontSize: '12px', color: '#6b7280' }}>Post-Trip</div>
                      <div style={{ fontSize: '18px', fontWeight: '600', color: '#000' }}>{inspection.evaluation.post_trip_reporting_score}/5</div>
                    </div>
                    <div>
                      <div style={{ fontSize: '12px', color: '#6b7280' }}>Compliance</div>
                      <div style={{ fontSize: '18px', fontWeight: '600', color: '#000' }}>{inspection.evaluation.compliance_documentation_score}/5</div>
                    </div>
                  </div>
                </div>
              )}

              {inspection.risk_score && (
                <div style={{ 
                  padding: '25px', 
                  backgroundColor: '#fff', 
                  borderRadius: '12px',
                  border: '1px solid #e5e7eb',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                }}>
                  <h4 style={{ color: '#374151', fontSize: '14px', marginBottom: '15px', fontWeight: '600' }}>Risk Assessment (This Trip)</h4>
                  <div style={{ fontSize: '36px', fontWeight: '700', color: getRiskLevelStyle(inspection.risk_score.risk_level).text, marginBottom: '5px' }}>
                    {getRiskLevelStyle(inspection.risk_score.risk_level).label}
                  </div>
                  <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '15px' }}>
                    {inspection.risk_score.total_points_this_trip} violation points
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Basic Info Grid */}
        <div style={{ padding: '30px', borderBottom: '1px solid #eee' }}>
          <h3 style={{ color: '#000', marginBottom: '20px', fontSize: '18px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span className="material-icons" style={{ fontSize: '20px' }}>info</span>
            Basic Information
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px' }}>
            <InfoItem label="Inspection ID" value={inspection.inspection_id} />
            <InfoItem label="Date" value={formatDate(inspection.inspection_date)} />
            <InfoItem label="Driver" value={inspection.driver.full_name} />
            <InfoItem label="Driver ID" value={inspection.driver.driver_id} />
            <InfoItem label="Vehicle" value={inspection.vehicle.registration_number} />
            <InfoItem label="Route" value={inspection.route} />
            <InfoItem label="Driving Hours" value={inspection.approved_driving_hours} />
            <InfoItem label="Rest Stops" value={inspection.approved_rest_stops.toString()} />
            <InfoItem label="Supervisor" value={inspection.supervisor.full_name} />
            {inspection.mechanic && (
              <InfoItem label="Mechanic" value={inspection.mechanic.full_name} />
            )}
            {inspection.approved_by && (
              <InfoItem label="Approved By" value={inspection.approved_by.full_name} />
            )}
          </div>
        </div>

        {/* Pre-Trip Section */}
        <div style={{ padding: '30px', borderBottom: '1px solid #eee', backgroundColor: '#fafafa' }}>
          <h3 style={{ color: '#000', marginBottom: '20px', fontSize: '18px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span className="material-icons" style={{ fontSize: '20px' }}>assignment</span>
            Pre-Trip Inspection Summary
          </h3>
          
          {/* Health & Fitness */}
          {inspection.health_fitness && (
            <div style={{ marginBottom: '20px' }}>
              <h4 style={{ color: '#333', marginBottom: '10px', fontSize: '14px', fontWeight: '600' }}>
                Health & Fitness Check
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '10px' }}>
                <CheckItem label="Alcohol Test" status={inspection.health_fitness.alcohol_test_status === 'pass'} />
                <CheckItem label="Temperature Check" status={inspection.health_fitness.temperature_check_status === 'pass'} />
                <CheckItem label="Fit for Duty" status={inspection.health_fitness.fit_for_duty} />
                <CheckItem label="No Health Impairment" status={inspection.health_fitness.no_health_impairment} />
                <CheckItem label="Fatigue Checklist" status={inspection.health_fitness.fatigue_checklist_completed} />
              </div>
            </div>
          )}

          {/* Documentation */}
          {inspection.documentation && (
            <div style={{ marginBottom: '20px' }}>
              <h4 style={{ color: '#333', marginBottom: '10px', fontSize: '14px', fontWeight: '600' }}>
                Documentation & Compliance
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '10px' }}>
                <CheckItem label="Certificate of Fitness" status={inspection.documentation.certificate_of_fitness === 'valid'} />
                <CheckItem label="Road Tax Valid" status={inspection.documentation.road_tax_valid} />
                <CheckItem label="Insurance Valid" status={inspection.documentation.insurance_valid} />
                <CheckItem label="Trip Authorization" status={inspection.documentation.trip_authorization_signed} />
                <CheckItem label="GPS Activated" status={inspection.documentation.gps_activated} />
                <CheckItem label="PPE Available" status={inspection.documentation.ppe_available} />
              </div>
            </div>
          )}

          {/* Vehicle Checks Summary */}
          <div>
            <h4 style={{ color: '#333', marginBottom: '10px', fontSize: '14px', fontWeight: '600' }}>
              Vehicle Checks
            </h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
              <CheckSummary 
                label="Exterior Checks" 
                total={inspection.exterior_checks?.length || 0}
                passed={inspection.exterior_checks?.filter(c => c.status === 'pass').length || 0}
              />
              <CheckSummary 
                label="Engine & Fluids" 
                total={inspection.engine_fluid_checks?.length || 0}
                passed={inspection.engine_fluid_checks?.filter(c => c.status === 'pass').length || 0}
              />
              <CheckSummary 
                label="Interior & Cabin" 
                total={inspection.interior_cabin_checks?.length || 0}
                passed={inspection.interior_cabin_checks?.filter(c => c.status === 'pass').length || 0}
              />
              <CheckSummary 
                label="Functional Checks" 
                total={inspection.functional_checks?.length || 0}
                passed={inspection.functional_checks?.filter(c => c.status === 'pass').length || 0}
              />
              <CheckSummary 
                label="Safety Equipment" 
                total={inspection.safety_equipment_checks?.length || 0}
                passed={inspection.safety_equipment_checks?.filter(c => c.status === 'pass').length || 0}
              />
            </div>
          </div>
        </div>

        {/* Post-Trip Section */}
        {inspection.post_trip && (
          <div style={{ padding: '30px', borderBottom: '1px solid #eee' }}>
            <h3 style={{ color: '#000', marginBottom: '20px', fontSize: '18px', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span className="material-icons" style={{ fontSize: '20px' }}>fact_check</span>
              Post-Trip Report
            </h3>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '20px' }}>
              <CheckItem label="Vehicle Fault Submitted" status={!inspection.post_trip.vehicle_fault_submitted} invertLabel="No Faults" />
              <CheckItem label="Final Inspection Signed" status={inspection.post_trip.final_inspection_signed} />
              <CheckItem label="Policy Compliance" status={inspection.post_trip.compliance_with_policy} />
              <CheckItem label="Good Attitude & Cooperation" status={inspection.post_trip.attitude_cooperation} />
              <CheckItem label="Incidents Recorded" status={!inspection.post_trip.incidents_recorded} invertLabel="No Incidents" />
              <InfoItem label="Trip Duration" value={inspection.post_trip.total_trip_duration || 'N/A'} />
            </div>

            {inspection.post_trip.fault_notes && (
              <div style={{ padding: '15px', backgroundColor: '#f5f5f5', borderRadius: '8px', marginBottom: '15px' }}>
                <strong style={{ color: '#000' }}>Fault Notes:</strong>
                <p style={{ color: '#333', marginTop: '5px' }}>{inspection.post_trip.fault_notes}</p>
              </div>
            )}

            {inspection.post_trip.incident_notes && (
              <div style={{ padding: '15px', backgroundColor: '#f5f5f5', borderRadius: '8px' }}>
                <strong style={{ color: '#000' }}>Incident Notes:</strong>
                <p style={{ color: '#333', marginTop: '5px' }}>{inspection.post_trip.incident_notes}</p>
              </div>
            )}
          </div>
        )}

        {/* Risk Score Section */}
        {inspection.risk_score && (
          <div style={{ padding: '30px', borderBottom: '1px solid #eee' }}>
            <h3 style={{ color: '#000', marginBottom: '20px', fontSize: '18px', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span className="material-icons" style={{ fontSize: '20px' }}>analytics</span>
              Risk Assessment
            </h3>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginBottom: '20px' }}>
              <div style={{ 
                padding: '20px', 
                backgroundColor: '#fff', 
                borderRadius: '8px',
                border: '1px solid #ddd',
              }}>
                <h4 style={{ color: '#666', fontSize: '14px', marginBottom: '10px' }}>This Trip</h4>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: '32px', fontWeight: '700', color: '#000' }}>
                    {inspection.risk_score.total_points_this_trip}
                  </span>
                  <span style={{
                    padding: '8px 16px',
                    borderRadius: '20px',
                    fontSize: '14px',
                    fontWeight: '600',
                    ...(() => {
                      const style = getRiskLevelStyle(inspection.risk_score.risk_level);
                      return { backgroundColor: style.bg, color: style.text };
                    })(),
                  }}>
                    {getRiskLevelStyle(inspection.risk_score.risk_level).label}
                  </span>
                </div>
                <p style={{ color: '#666', fontSize: '12px', marginTop: '5px' }}>violation points</p>
              </div>

              <div style={{ 
                padding: '20px', 
                backgroundColor: '#fff', 
                borderRadius: '8px',
                border: '1px solid #ddd',
              }}>
                <h4 style={{ color: '#666', fontSize: '14px', marginBottom: '10px' }}>30-Day Rolling</h4>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: '32px', fontWeight: '700', color: '#000' }}>
                    {inspection.risk_score.total_points_30_days}
                  </span>
                  <span style={{
                    padding: '8px 16px',
                    borderRadius: '20px',
                    fontSize: '14px',
                    fontWeight: '600',
                    ...(() => {
                      const style = getRiskLevelStyle(inspection.risk_score.risk_level_30_days);
                      return { backgroundColor: style.bg, color: style.text };
                    })(),
                  }}>
                    {getRiskLevelStyle(inspection.risk_score.risk_level_30_days).label}
                  </span>
                </div>
                <p style={{ color: '#666', fontSize: '12px', marginTop: '5px' }}>total points in last 30 days</p>
              </div>
            </div>

            {/* Risk Level Guide */}
            <div style={{ 
              padding: '15px', 
              backgroundColor: '#fff', 
              borderRadius: '8px',
              border: '1px solid #ddd',
              marginBottom: '20px',
            }}>
              <h4 style={{ color: '#000', fontSize: '14px', marginBottom: '10px' }}>Risk Level Guide</h4>
              <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
                <span><strong style={{ color: '#4CAF50' }}>Low (0-3 pts)</strong> - Excellent</span>
                <span><strong style={{ color: '#FF9800' }}>Medium (4-9 pts)</strong> - Monitoring Required</span>
                <span><strong style={{ color: '#f44336' }}>High (10+ pts)</strong> - Immediate Action</span>
              </div>
            </div>

            {/* Trip Behavior Breakdown - How Risk Was Calculated */}
            {inspection.trip_behaviors && inspection.trip_behaviors.length > 0 && (
              <div style={{ 
                padding: '20px', 
                backgroundColor: '#fff', 
                borderRadius: '8px',
                border: '1px solid #ddd',
              }}>
                <h4 style={{ color: '#000', fontSize: '14px', marginBottom: '15px' }}>
                  Trip Behavior Breakdown (How Risk Was Calculated)
                </h4>
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
                    <thead>
                      <tr style={{ borderBottom: '2px solid #eee' }}>
                        <th style={{ textAlign: 'left', padding: '10px', color: '#666' }}>Behavior Item</th>
                        <th style={{ textAlign: 'center', padding: '10px', color: '#666' }}>Status</th>
                        <th style={{ textAlign: 'center', padding: '10px', color: '#666' }}>Points</th>
                        <th style={{ textAlign: 'left', padding: '10px', color: '#666' }}>Notes</th>
                      </tr>
                    </thead>
                    <tbody>
                      {inspection.trip_behaviors.map((behavior, idx) => (
                        <tr key={behavior.id || idx} style={{ borderBottom: '1px solid #eee' }}>
                          <td style={{ padding: '10px', color: '#000' }}>
                            {formatBehaviorItem(behavior.behavior_item)}
                          </td>
                          <td style={{ padding: '10px', textAlign: 'center' }}>
                            <span style={{
                              padding: '4px 8px',
                              borderRadius: '4px',
                              fontSize: '12px',
                              fontWeight: '600',
                              backgroundColor: behavior.status === 'violation' ? '#ffebee' : 
                                             behavior.status === 'compliant' ? '#e8f5e9' : '#f5f5f5',
                              color: behavior.status === 'violation' ? '#c62828' : 
                                    behavior.status === 'compliant' ? '#2e7d32' : '#666',
                            }}>
                              {behavior.status.charAt(0).toUpperCase() + behavior.status.slice(1)}
                            </span>
                          </td>
                          <td style={{ 
                            padding: '10px', 
                            textAlign: 'center',
                            fontWeight: '700',
                            color: behavior.violation_points > 0 ? '#c62828' : '#666',
                          }}>
                            {behavior.violation_points > 0 ? `+${behavior.violation_points}` : '0'}
                          </td>
                          <td style={{ padding: '10px', color: '#666', fontSize: '13px' }}>
                            {behavior.notes || '-'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                    <tfoot>
                      <tr style={{ backgroundColor: '#f5f5f5' }}>
                        <td colSpan={2} style={{ padding: '10px', fontWeight: '700', color: '#000' }}>
                          Total Violation Points
                        </td>
                        <td style={{ padding: '10px', textAlign: 'center', fontWeight: '700', color: '#000', fontSize: '16px' }}>
                          {inspection.trip_behaviors.reduce((sum, b) => sum + (b.violation_points || 0), 0)}
                        </td>
                        <td></td>
                      </tr>
                    </tfoot>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Evaluation Summary */}
        {inspection.evaluation && (
          <div style={{ padding: '30px', borderBottom: '1px solid #eee' }}>
            <h3 style={{ color: '#000', marginBottom: '20px', fontSize: '18px', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span className="material-icons" style={{ fontSize: '20px' }}>assessment</span>
              Evaluation Summary
            </h3>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '15px', marginBottom: '20px' }}>
              <ScoreItem label="Pre-Trip Inspection" score={inspection.evaluation.pre_trip_inspection_score} />
              <ScoreItem label="Driving Conduct" score={inspection.evaluation.driving_conduct_score} />
              <ScoreItem label="Incident Management" score={inspection.evaluation.incident_management_score} />
              <ScoreItem label="Post-Trip Reporting" score={inspection.evaluation.post_trip_reporting_score} />
              <ScoreItem label="Compliance & Docs" score={inspection.evaluation.compliance_documentation_score} />
            </div>

            <div style={{ 
              padding: '20px', 
              backgroundColor: '#000', 
              color: '#fff',
              borderRadius: '8px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}>
              <span style={{ fontSize: '16px', fontWeight: '600' }}>Overall Performance</span>
              <span style={{ fontSize: '20px', fontWeight: '700' }}>
                {getPerformanceStyle(inspection.evaluation.overall_performance).label}
              </span>
            </div>

            {inspection.evaluation.comments && (
              <div style={{ padding: '15px', backgroundColor: '#f5f5f5', borderRadius: '8px', marginTop: '15px' }}>
                <strong style={{ color: '#000' }}>Comments:</strong>
                <p style={{ color: '#333', marginTop: '5px' }}>{inspection.evaluation.comments}</p>
              </div>
            )}
          </div>
        )}

        {/* Supervisor Remarks */}
        {inspection.supervisor_remarks && (
          <div style={{ padding: '30px' }}>
            <h3 style={{ color: '#000', marginBottom: '20px', fontSize: '18px', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span className="material-icons" style={{ fontSize: '20px' }}>rate_review</span>
              Supervisor Remarks
            </h3>
            
            <div style={{ marginBottom: '15px' }}>
              <span style={{ color: '#666', fontSize: '14px' }}>Supervisor:</span>
              <p style={{ color: '#000', fontWeight: '500', marginTop: '5px' }}>
                {inspection.supervisor_remarks.supervisor_name}
              </p>
            </div>

            <div style={{ marginBottom: '15px' }}>
              <span style={{ color: '#666', fontSize: '14px' }}>Remarks:</span>
              <p style={{ color: '#000', marginTop: '5px', whiteSpace: 'pre-line' }}>
                {inspection.supervisor_remarks.remarks}
              </p>
            </div>

            {inspection.supervisor_remarks.recommendation && (
              <div style={{ 
                padding: '15px', 
                backgroundColor: '#f5f5f5',
                borderRadius: '8px',
                borderLeft: '4px solid #000',
              }}>
                <span style={{ color: '#666', fontSize: '14px', fontWeight: '600' }}>Recommendation:</span>
                <p style={{ color: '#000', marginTop: '5px', fontWeight: '500' }}>
                  {inspection.supervisor_remarks.recommendation}
                </p>
              </div>
            )}
          </div>
        )}

        {/* Report Footer */}
        <div style={{ 
          padding: '20px 30px', 
          borderTop: '2px solid #000',
          backgroundColor: '#fafafa',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}>
          <p style={{ color: '#666', fontSize: '12px' }}>
            This report was generated by the Fleet Management System
          </p>
          <p style={{ color: '#666', fontSize: '12px' }}>
            Report ID: {inspection.inspection_id}
          </p>
        </div>
      </div>

      {/* Print Styles */}
      <style jsx global>{`
        @media print {
          body * {
            visibility: hidden;
          }
          .dashboard-container, .dashboard-container * {
            visibility: visible;
          }
          .dashboard-header {
            display: none !important;
          }
          .dashboard-container {
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
          }
        }
      `}</style>
    </div>
  );
}

// Helper Components
function InfoItem({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <span style={{ color: '#666', fontSize: '12px', display: 'block' }}>{label}</span>
      <span style={{ color: '#000', fontWeight: '500', fontSize: '14px' }}>{value}</span>
    </div>
  );
}

function CheckItem({ label, status, invertLabel }: { label: string; status: boolean; invertLabel?: string }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
      <span className="material-icons" style={{ 
        fontSize: '18px', 
        color: status ? '#000' : '#999' 
      }}>
        {status ? 'check_circle' : 'cancel'}
      </span>
      <span style={{ color: '#333', fontSize: '13px' }}>
        {status && invertLabel ? invertLabel : label}
      </span>
    </div>
  );
}

function CheckSummary({ label, total, passed }: { label: string; total: number; passed: number }) {
  const percentage = total > 0 ? Math.round((passed / total) * 100) : 0;
  return (
    <div style={{ 
      padding: '15px', 
      backgroundColor: '#fff', 
      borderRadius: '8px',
      border: '1px solid #ddd',
    }}>
      <span style={{ color: '#666', fontSize: '12px', display: 'block', marginBottom: '5px' }}>{label}</span>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: '10px' }}>
        <span style={{ fontSize: '24px', fontWeight: '700', color: '#000' }}>{passed}/{total}</span>
        <span style={{ fontSize: '14px', color: '#666' }}>({percentage}% pass)</span>
      </div>
    </div>
  );
}

function ScoreItem({ label, score }: { label: string; score: number }) {
  return (
    <div style={{ 
      padding: '15px', 
      backgroundColor: '#f5f5f5', 
      borderRadius: '8px',
      textAlign: 'center',
    }}>
      <span style={{ color: '#666', fontSize: '12px', display: 'block', marginBottom: '5px' }}>{label}</span>
      <span style={{ fontSize: '24px', fontWeight: '700', color: '#000' }}>{score}/5</span>
    </div>
  );
}
