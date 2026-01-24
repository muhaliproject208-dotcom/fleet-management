'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated } from '@/lib/api/auth';
import { getInspections } from '@/lib/api/inspections';
import { PreTripInspection, InspectionStatus } from '@/lib/api/inspections/types';
import InspectionStatusBadge from '../components/InspectionStatusBadge';

export default function PostTripInspectionsPage() {
  const router = useRouter();
  const [inspections, setInspections] = useState<PreTripInspection[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showWarningModal, setShowWarningModal] = useState(false);
  const [selectedInspectionId, setSelectedInspectionId] = useState<string | null>(null);
  
  // Filter states
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const pageSize = 25;

  const fetchInspections = useCallback(async () => {
    // Only fetch approved inspections for post-trip
    const params: Record<string, string | number> = {
      page: currentPage,
      page_size: pageSize,
      status: InspectionStatus.APPROVED,
    };

    if (searchQuery.trim()) {
      params.search = searchQuery.trim();
    }

    const response = await getInspections(params);

    if (response.error) {
      setError(response.error);
    } else if (response.data) {
      setInspections(response.data.results || []);
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
      void fetchInspections();
    }, 100);

    return () => clearTimeout(timer);
  }, [router, fetchInspections]);

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

  const handleStartPostTrip = (inspectionId: string) => {
    setSelectedInspectionId(inspectionId);
    setShowWarningModal(true);
  };

  const confirmStartPostTrip = () => {
    if (selectedInspectionId) {
      router.push(`/dashboard/inspections/${selectedInspectionId}/post-trip`);
    }
    setShowWarningModal(false);
  };

  const totalPages = Math.ceil(totalCount / pageSize);

  if (loading) {
    return (
      <div className="container">
        <div className="text-center">
          <div className="spinner" style={{ margin: '0 auto' }}></div>
          <p style={{ marginTop: '20px' }}>Loading post-trip inspections...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      {/* Warning Modal */}
      {showWarningModal && (
        <div 
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
          }}
        >
          <div 
            style={{
              backgroundColor: 'white',
              borderRadius: '12px',
              padding: '30px',
              maxWidth: '500px',
              width: '90%',
              boxShadow: '0 4px 20px rgba(0, 0, 0, 0.15)',
            }}
          >
            <div style={{ textAlign: 'center', marginBottom: '20px' }}>
              <span 
                className="material-icons" 
                style={{ 
                  fontSize: '64px', 
                  color: '#FF9800',
                  marginBottom: '15px',
                  display: 'block',
                }}
              >
                warning
              </span>
              <h2 style={{ color: '#333', marginBottom: '10px' }}>Important Notice</h2>
            </div>
            
            <div style={{ 
              backgroundColor: '#FFF3E0', 
              padding: '20px', 
              borderRadius: '8px',
              marginBottom: '20px',
              border: '1px solid #FFE0B2',
            }}>
              <p style={{ color: '#E65100', marginBottom: '10px', fontWeight: '600' }}>
                ⚠️ You must complete the post-trip inspection in one session.
              </p>
              <p style={{ color: '#333', fontSize: '14px', marginBottom: '10px' }}>
                Once you start the post-trip inspection:
              </p>
              <ul style={{ 
                color: '#666', 
                fontSize: '14px', 
                paddingLeft: '20px',
                marginBottom: '0',
              }}>
                <li>Each form will be saved as you complete it</li>
                <li>You cannot save as draft and return later</li>
                <li>You must complete all 9 steps to finish</li>
                <li>Ensure you have all required information ready</li>
              </ul>
            </div>

            <div style={{ display: 'flex', gap: '15px', justifyContent: 'center' }}>
              <button
                onClick={() => setShowWarningModal(false)}
                className="button-secondary"
                style={{ padding: '12px 24px', width: 'auto' }}
              >
                Cancel
              </button>
              <button
                onClick={confirmStartPostTrip}
                className="button-primary"
                style={{ 
                  padding: '12px 24px', 
                  width: 'auto',
                  backgroundColor: '#4CAF50',
                  borderColor: '#4CAF50',
                }}
              >
                I Understand, Start Post-Trip
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="dashboard-header">
        <div>
          <h1>Post-Trip Inspections</h1>
          <p style={{ color: '#666', marginTop: '5px' }}>
            Complete post-trip inspections for approved pre-trip records
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

      {/* Info Banner */}
      <div 
        style={{ 
          backgroundColor: '#E3F2FD', 
          padding: '15px 20px', 
          borderRadius: '8px', 
          marginBottom: '20px',
          display: 'flex',
          alignItems: 'center',
          gap: '15px',
          border: '1px solid #BBDEFB',
        }}
      >
        <span className="material-icons" style={{ color: '#1976D2', fontSize: '24px' }}>
          info
        </span>
        <div>
          <p style={{ color: '#1565C0', margin: 0, fontWeight: '500' }}>
            Only approved pre-trip inspections are shown here
          </p>
          <p style={{ color: '#1976D2', margin: 0, fontSize: '13px' }}>
            Complete the post-trip inspection after the driver returns from their trip
          </p>
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

      {/* Inspections Table */}
      {inspections.length === 0 ? (
        <div className="profile-card" style={{ textAlign: 'center', padding: '60px 20px' }}>
          <span className="material-icons" style={{ fontSize: '64px', color: '#ccc', marginBottom: '20px' }}>
            assignment_turned_in
          </span>
          <h2>No Inspections Ready for Post-Trip</h2>
          <p style={{ color: '#666', marginBottom: '20px' }}>
            {searchQuery 
              ? 'No approved inspections match your search' 
              : 'All approved pre-trip inspections have been completed or none exist yet'}
          </p>
          <button 
            onClick={() => router.push('/dashboard/inspections')} 
            className="button-primary" 
            style={{ width: 'auto' }}
          >
            View Pre-Trip Inspections
          </button>
        </div>
      ) : (
        <>
          <div style={{ backgroundColor: 'white', borderRadius: '8px', overflow: 'hidden' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ backgroundColor: '#f8f9fa', borderBottom: '2px solid #dee2e6' }}>
                  <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600', color: '#000' }}>
                    Inspection ID
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
                {inspections.map((inspection) => (
                  <tr 
                    key={inspection.id} 
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
                    onClick={() => router.push(`/dashboard/inspections/${inspection.id}`)}
                  >
                    <td style={{ padding: '12px', color: '#000', fontWeight: '500' }}>
                      {inspection.inspection_id}
                    </td>
                    <td style={{ padding: '12px', color: '#000' }}>
                      {formatDate(inspection.inspection_date)}
                    </td>
                    <td style={{ padding: '12px', color: '#000' }}>
                      {inspection.driver.full_name}
                    </td>
                    <td style={{ padding: '12px', color: '#000' }}>
                      {inspection.vehicle.registration_number}
                    </td>
                    <td style={{ padding: '12px', color: '#000' }}>
                      {inspection.route}
                    </td>
                    <td style={{ padding: '12px' }}>
                      <InspectionStatusBadge status={inspection.status} size="sm" />
                    </td>
                    <td style={{ padding: '12px', textAlign: 'center' }}>
                      <div style={{ display: 'flex', gap: '8px', justifyContent: 'center' }}>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            router.push(`/dashboard/inspections/${inspection.id}`);
                          }}
                          className="button-secondary"
                          style={{ 
                            padding: '6px 12px', 
                            fontSize: '14px',
                            width: 'auto',
                          }}
                        >
                          View
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleStartPostTrip(inspection.id);
                          }}
                          className="button-primary"
                          style={{ 
                            padding: '6px 12px', 
                            fontSize: '14px',
                            width: 'auto',
                            backgroundColor: '#4CAF50',
                            borderColor: '#4CAF50',
                          }}
                        >
                          Start Post-Trip
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
                Showing {((currentPage - 1) * pageSize) + 1} to {Math.min(currentPage * pageSize, totalCount)} of {totalCount} inspections
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
