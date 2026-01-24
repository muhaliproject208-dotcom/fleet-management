'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated } from '@/lib/api/auth';
import { getInspections } from '@/lib/api/inspections';
import { PreTripInspection, InspectionStatus } from '@/lib/api/inspections/types';
import InspectionStatusBadge from '../inspections/components/InspectionStatusBadge';

interface ReportWithScores extends PreTripInspection {
  evaluation?: {
    pre_trip_inspection_score: number;
    driving_conduct_score: number;
    incident_management_score: number;
    post_trip_reporting_score: number;
    compliance_documentation_score: number;
    total_score?: number;
  };
}

export default function ReportsPage() {
  const router = useRouter();
  const [reports, setReports] = useState<ReportWithScores[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [downloadingId, setDownloadingId] = useState<string | null>(null);
  
  // Filter states
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const pageSize = 25;

  const fetchReports = useCallback(async () => {
    // Fetch approved and post-trip completed inspections for reports
    const params: Record<string, string | number> = {
      page: currentPage,
      page_size: pageSize,
      status: `${InspectionStatus.APPROVED},${InspectionStatus.POST_TRIP_COMPLETED}`,
    };

    if (searchQuery.trim()) {
      params.search = searchQuery.trim();
    }

    const response = await getInspections(params);

    if (response.error) {
      setError(response.error);
    } else if (response.data) {
      // For now, use the inspection data - evaluation scores would come from the API
      setReports(response.data.results || []);
      setTotalCount(response.data.count || 0);
    }

    setLoading(false);
  }, [currentPage, searchQuery]);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }

    const timer = setTimeout(() => {
      void fetchReports();
    }, 100);

    return () => clearTimeout(timer);
  }, [router, fetchReports]);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    });
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
    setCurrentPage(1);
  };

  const handleDownloadPDF = async (inspectionId: string, inspectionCode: string) => {
    setDownloadingId(inspectionId);
    
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(
        `http://localhost:8000/api/v1/inspections/${inspectionId}/download_pdf/`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );
      
      if (!response.ok) {
        throw new Error('Failed to download PDF');
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `inspection-${inspectionCode}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Error downloading PDF:', err);
      alert('Failed to download PDF. Please try again.');
    } finally {
      setDownloadingId(null);
    }
  };

  const totalPages = Math.ceil(totalCount / pageSize);

  if (loading) {
    return (
      <div className="container">
        <div className="text-center">
          <div className="spinner" style={{ margin: '0 auto' }}></div>
          <p style={{ marginTop: '20px' }}>Loading reports...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <div>
          <h1>Inspection Reports</h1>
          <p style={{ color: '#666', marginTop: '5px' }}>
            View completed inspection reports, scores, and download PDFs
          </p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button 
            onClick={() => router.push('/dashboard/inspections')} 
            className="button-secondary" 
            style={{ width: 'auto' }}
          >
            Pre-Trip Inspections
          </button>
          <button 
            onClick={() => router.push('/dashboard')} 
            className="button-secondary" 
            style={{ width: 'auto' }}
          >
            Back to Dashboard
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
        gap: '20px', 
        marginBottom: '20px' 
      }}>
        <div className="profile-card" style={{ padding: '20px', textAlign: 'center' }}>
          <span className="material-icons" style={{ fontSize: '40px', color: '#4CAF50', marginBottom: '10px' }}>
            check_circle
          </span>
          <h3 style={{ margin: '0 0 5px', color: '#000' }}>{totalCount}</h3>
          <p style={{ margin: 0, color: '#666', fontSize: '14px' }}>Completed Reports</p>
        </div>
        <div className="profile-card" style={{ padding: '20px', textAlign: 'center' }}>
          <span className="material-icons" style={{ fontSize: '40px', color: '#2196F3', marginBottom: '10px' }}>
            picture_as_pdf
          </span>
          <h3 style={{ margin: '0 0 5px', color: '#000' }}>PDF</h3>
          <p style={{ margin: 0, color: '#666', fontSize: '14px' }}>Download Available</p>
        </div>
        <div className="profile-card" style={{ padding: '20px', textAlign: 'center' }}>
          <span className="material-icons" style={{ fontSize: '40px', color: '#FF9800', marginBottom: '10px' }}>
            assessment
          </span>
          <h3 style={{ margin: '0 0 5px', color: '#000' }}>Scores</h3>
          <p style={{ margin: 0, color: '#666', fontSize: '14px' }}>Evaluation Results</p>
        </div>
      </div>

      {/* Search */}
      <div 
        style={{ 
          backgroundColor: 'white', 
          padding: '20px', 
          borderRadius: '8px', 
          marginBottom: '20px',
          display: 'flex',
          gap: '15px',
          flexWrap: 'wrap',
          alignItems: 'center',
        }}
      >
        <div style={{ flex: '1 1 300px' }}>
          <input
            type="text"
            className="input"
            placeholder="Search by ID, driver, vehicle, or route..."
            value={searchQuery}
            onChange={handleSearchChange}
            style={{ width: '100%' }}
          />
        </div>
        
        {searchQuery && (
          <button
            onClick={() => {
              setSearchQuery('');
              setCurrentPage(1);
            }}
            className="button-secondary"
            style={{ width: 'auto' }}
          >
            Clear Search
          </button>
        )}
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {/* Reports Table */}
      {reports.length === 0 ? (
        <div className="profile-card" style={{ textAlign: 'center', padding: '60px 20px' }}>
          <span className="material-icons" style={{ fontSize: '64px', color: '#ccc', marginBottom: '20px' }}>
            summarize
          </span>
          <h2>No Reports Available</h2>
          <p style={{ color: '#666', marginBottom: '20px' }}>
            {searchQuery 
              ? 'No reports match your search' 
              : 'Completed inspection reports will appear here after approval'}
          </p>
          <button 
            onClick={() => router.push('/dashboard/inspections')} 
            className="button-primary" 
            style={{ width: 'auto' }}
          >
            View Inspections
          </button>
        </div>
      ) : (
        <>
          <div style={{ backgroundColor: 'white', borderRadius: '8px', overflow: 'hidden' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ backgroundColor: '#f8f9fa', borderBottom: '2px solid #dee2e6' }}>
                  <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600', color: '#000' }}>
                    Report ID
                  </th>
                  <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600', color: '#000' }}>
                    Date
                  </th>
                  <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600', color: '#000' }}>
                    Driver
                  </th>
                  <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600', color: '#000' }}>
                    Vehicle
                  </th>
                  <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600', color: '#000' }}>
                    Route
                  </th>
                  <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600', color: '#000' }}>
                    Status
                  </th>
                  <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600', color: '#000' }}>
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody>
                {reports.map((report) => (
                    <tr 
                      key={report.id} 
                      style={{ 
                        borderBottom: '1px solid #dee2e6',
                        cursor: 'pointer',
                        transition: 'background-color 0.2s',
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.backgroundColor = '#f8f9fa';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.backgroundColor = 'transparent';
                      }}
                      onClick={() => router.push(`/dashboard/inspections/${report.id}`)}
                    >
                      <td style={{ padding: '12px', color: '#000', fontWeight: '500' }}>
                        {report.inspection_id}
                      </td>
                      <td style={{ padding: '12px', color: '#000' }}>
                        {formatDate(report.inspection_date)}
                      </td>
                      <td style={{ padding: '12px', color: '#000' }}>
                        {report.driver.full_name}
                      </td>
                      <td style={{ padding: '12px', color: '#000' }}>
                        {report.vehicle.registration_number}
                      </td>
                      <td style={{ padding: '12px', color: '#000' }}>
                        {report.route}
                      </td>
                      <td style={{ padding: '12px' }}>
                        <InspectionStatusBadge status={report.status} size="sm" />
                      </td>
                      <td style={{ padding: '12px', textAlign: 'center' }}>
                        <div style={{ display: 'flex', gap: '8px', justifyContent: 'center' }}>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              router.push(`/dashboard/inspections/${report.id}/report`);
                            }}
                            className="button-secondary"
                            style={{ 
                              padding: '6px 12px', 
                              fontSize: '14px',
                              width: 'auto',
                            }}
                          >
                            View Report
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDownloadPDF(report.id, report.inspection_id);
                            }}
                            disabled={downloadingId === report.id}
                            className="button-primary"
                            style={{ 
                              padding: '6px 12px', 
                              fontSize: '14px',
                              width: 'auto',
                              backgroundColor: '#000',
                              borderColor: '#000',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '5px',
                            }}
                          >
                            {downloadingId === report.id ? (
                              <>
                                <div className="spinner" style={{ width: '14px', height: '14px', borderWidth: '2px' }}></div>
                                Downloading...
                              </>
                            ) : (
                              <>
                                <span className="material-icons" style={{ fontSize: '16px' }}>download</span>
                                PDF
                              </>
                            )}
                          </button>
                        </div>
                      </td>
                    </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div 
              style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                marginTop: '20px',
                padding: '15px',
                backgroundColor: 'white',
                borderRadius: '8px',
              }}
            >
              <div style={{ color: '#666' }}>
                Showing {((currentPage - 1) * pageSize) + 1} to {Math.min(currentPage * pageSize, totalCount)} of {totalCount} reports
              </div>
              
              <div style={{ display: 'flex', gap: '5px' }}>
                <button
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="button-secondary"
                  style={{ 
                    padding: '8px 16px',
                    width: 'auto',
                    opacity: currentPage === 1 ? 0.5 : 1,
                    cursor: currentPage === 1 ? 'not-allowed' : 'pointer',
                  }}
                >
                  Previous
                </button>
                
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  let pageNum;
                  if (totalPages <= 5) {
                    pageNum = i + 1;
                  } else if (currentPage <= 3) {
                    pageNum = i + 1;
                  } else if (currentPage >= totalPages - 2) {
                    pageNum = totalPages - 4 + i;
                  } else {
                    pageNum = currentPage - 2 + i;
                  }
                  
                  return (
                    <button
                      key={pageNum}
                      onClick={() => setCurrentPage(pageNum)}
                      className={currentPage === pageNum ? 'button-primary' : 'button-secondary'}
                      style={{ 
                        padding: '8px 12px',
                        width: 'auto',
                        minWidth: '40px',
                      }}
                    >
                      {pageNum}
                    </button>
                  );
                })}
                
                <button
                  onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                  className="button-secondary"
                  style={{ 
                    padding: '8px 16px',
                    width: 'auto',
                    opacity: currentPage === totalPages ? 0.5 : 1,
                    cursor: currentPage === totalPages ? 'not-allowed' : 'pointer',
                  }}
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
