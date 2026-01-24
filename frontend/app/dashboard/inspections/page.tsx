'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated } from '@/lib/api/auth';
import { getInspections } from '@/lib/api/inspections';
import { PreTripInspection, InspectionStatus } from '@/lib/api/inspections/types';
import InspectionStatusBadge from './components/InspectionStatusBadge';

export default function InspectionsPage() {
  const router = useRouter();
  const [inspections, setInspections] = useState<PreTripInspection[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Filter states
  const [statusFilter, setStatusFilter] = useState<InspectionStatus | 'all'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const pageSize = 25;

  const fetchInspections = useCallback(async () => {
    const params: Record<string, string | number> = {
      page: currentPage,
      page_size: pageSize,
    };

    if (statusFilter !== 'all') {
      params.status = statusFilter;
    }

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
  }, [currentPage, statusFilter, searchQuery]);

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
    setCurrentPage(1); // Reset to first page on search
  };

  const handleStatusFilterChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setStatusFilter(e.target.value as InspectionStatus | 'all');
    setCurrentPage(1); // Reset to first page on filter
  };

  const totalPages = Math.ceil(totalCount / pageSize);

  if (loading) {
    return (
      <div className="container">
        <div className="text-center">
          <div className="spinner" style={{ margin: '0 auto' }}></div>
          <p style={{ marginTop: '20px' }}>Loading inspections...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <div>
          <h1>Inspections</h1>
          <p style={{ color: '#666', marginTop: '5px' }}>
            Manage and track vehicle inspections
          </p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button 
            onClick={() => router.push('/dashboard/inspections/new')} 
            className="button-primary" 
            style={{ width: 'auto' }}
          >
            + New Inspection
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

      {/* Quick Status Filters */}
      <div style={{ 
        display: 'flex', 
        gap: '10px', 
        marginBottom: '15px',
        flexWrap: 'wrap',
      }}>
        <button
          onClick={() => {
            setStatusFilter('all');
            setCurrentPage(1);
          }}
          className={statusFilter === 'all' ? 'button-primary' : 'button-secondary'}
          style={{ width: 'auto', padding: '8px 16px' }}
        >
          All ({totalCount})
        </button>
        <button
          onClick={() => {
            setStatusFilter(InspectionStatus.DRAFT);
            setCurrentPage(1);
          }}
          className={statusFilter === InspectionStatus.DRAFT ? 'button-primary' : 'button-secondary'}
          style={{ width: 'auto', padding: '8px 16px' }}
        >
          Drafts
        </button>
        <button
          onClick={() => {
            setStatusFilter(InspectionStatus.SUBMITTED);
            setCurrentPage(1);
          }}
          className={statusFilter === InspectionStatus.SUBMITTED ? 'button-primary' : 'button-secondary'}
          style={{ width: 'auto', padding: '8px 16px' }}
        >
          Submitted
        </button>
        <button
          onClick={() => {
            setStatusFilter(InspectionStatus.APPROVED);
            setCurrentPage(1);
          }}
          className={statusFilter === InspectionStatus.APPROVED ? 'button-primary' : 'button-secondary'}
          style={{ width: 'auto', padding: '8px 16px' }}
        >
          Approved
        </button>
        <button
          onClick={() => {
            setStatusFilter(InspectionStatus.REJECTED);
            setCurrentPage(1);
          }}
          className={statusFilter === InspectionStatus.REJECTED ? 'button-primary' : 'button-secondary'}
          style={{ width: 'auto', padding: '8px 16px' }}
        >
          Rejected
        </button>
      </div>

      {/* Search and Filters */}
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
        
        <div style={{ flex: '0 1 200px' }}>
          <select
            className="input"
            value={statusFilter}
            onChange={handleStatusFilterChange}
            style={{ width: '100%' }}
          >
            <option value="all">All Status</option>
            <option value={InspectionStatus.DRAFT}>Draft</option>
            <option value={InspectionStatus.SUBMITTED}>Submitted</option>
            <option value={InspectionStatus.APPROVED}>Approved</option>
            <option value={InspectionStatus.POST_TRIP_IN_PROGRESS}>Post-Trip In Progress</option>
            <option value={InspectionStatus.POST_TRIP_COMPLETED}>Completed</option>
            <option value={InspectionStatus.REJECTED}>Rejected</option>
          </select>
        </div>

        {(statusFilter !== 'all' || searchQuery) && (
          <button
            onClick={() => {
              setStatusFilter('all');
              setSearchQuery('');
              setCurrentPage(1);
            }}
            className="button-secondary"
            style={{ width: 'auto' }}
          >
            Clear Filters
          </button>
        )}
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {/* Inspections Table */}
      {inspections.length === 0 ? (
        <div className="profile-card" style={{ textAlign: 'center', padding: '60px 20px' }}>
          <span className="material-icons" style={{ fontSize: '64px', color: '#ccc', marginBottom: '20px' }}>
            assignment
          </span>
          <h2>No Inspections Found</h2>
          <p style={{ color: '#666', marginBottom: '20px' }}>
            {searchQuery || statusFilter !== 'all' 
              ? 'No inspections match your filters' 
              : 'Get started by creating your first inspection'}
          </p>
          {statusFilter === InspectionStatus.DRAFT ? (
            <p style={{ color: '#666', marginBottom: '20px' }}>
              You have no draft inspections. Start a new inspection to create a draft.
            </p>
          ) : null}
          <button 
            onClick={() => router.push('/dashboard/inspections/new')} 
            className="button-primary" 
            style={{ width: 'auto' }}
          >
            + New Inspection
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
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                        <InspectionStatusBadge status={inspection.status} size="sm" />
                        {inspection.completion_info && (
                          <span style={{ fontSize: '12px', color: '#666' }}>
                            {inspection.completion_info.completion_percentage}% complete
                          </span>
                        )}
                      </div>
                    </td>
                    <td style={{ padding: '12px', textAlign: 'center' }}>
                      <div style={{ display: 'flex', gap: '8px', justifyContent: 'center' }}>
                        {inspection.status === InspectionStatus.DRAFT ? (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              // Resume from where user left off
                              const nextStep = inspection.completion_info?.next_step || 2;
                              router.push(`/dashboard/inspections/new?id=${inspection.id}&step=${nextStep}`);
                            }}
                            className="button-primary"
                            style={{ 
                              padding: '6px 12px', 
                              fontSize: '14px',
                              width: 'auto',
                              backgroundColor: '#666',
                              borderColor: '#666',
                            }}
                          >
                            Resume Pre-Trip ({inspection.completion_info?.next_step || 2}/9)
                          </button>
                        ) : inspection.status === InspectionStatus.APPROVED && inspection.post_trip_completion_info && inspection.post_trip_completion_info.completed_steps.length > 0 ? (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              // Go to step after highest completed
                              const completedSteps = inspection.post_trip_completion_info?.completed_steps || [];
                              const highestCompleted = completedSteps.length > 0 ? Math.max(...completedSteps) : 0;
                              const nextStep = Math.min(highestCompleted + 1, 9);
                              router.push(`/dashboard/inspections/${inspection.id}/post-trip?step=${nextStep}`);
                            }}
                            className="button-primary"
                            style={{ 
                              padding: '6px 12px', 
                              fontSize: '14px',
                              width: 'auto',
                              backgroundColor: '#FF9800',
                              borderColor: '#FF9800',
                            }}
                          >
                            Resume Post-Trip ({inspection.post_trip_completion_info?.completed_steps.length || 0}/9)
                          </button>
                        ) : inspection.status === InspectionStatus.APPROVED ? (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              router.push(`/dashboard/inspections/${inspection.id}/post-trip`);
                            }}
                            className="button-primary"
                            style={{ 
                              padding: '6px 12px', 
                              fontSize: '14px',
                              width: 'auto',
                              backgroundColor: '#2196F3',
                              borderColor: '#2196F3',
                            }}
                          >
                            Start Post-Trip
                          </button>
                        ) : inspection.status === InspectionStatus.POST_TRIP_IN_PROGRESS ? (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              // Go to step after highest completed
                              const completedSteps = inspection.post_trip_completion_info?.completed_steps || [];
                              const highestCompleted = completedSteps.length > 0 ? Math.max(...completedSteps) : 0;
                              const nextStep = Math.min(highestCompleted + 1, 9);
                              router.push(`/dashboard/inspections/${inspection.id}/post-trip?step=${nextStep}`);
                            }}
                            className="button-primary"
                            style={{ 
                              padding: '6px 12px', 
                              fontSize: '14px',
                              width: 'auto',
                              backgroundColor: '#FF9800',
                              borderColor: '#FF9800',
                            }}
                          >
                            Resume Post-Trip ({inspection.post_trip_completion_info?.completed_steps.length || 0}/9)
                          </button>
                        ) : inspection.status === InspectionStatus.POST_TRIP_COMPLETED ? (
                          <span
                            style={{ 
                              padding: '6px 12px', 
                              fontSize: '14px',
                              color: '#4CAF50',
                              fontWeight: '600',
                            }}
                          >
                            Completed
                          </span>
                        ) : (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              router.push(`/dashboard/inspections/${inspection.id}`);
                            }}
                            className="button-primary"
                            style={{ 
                              padding: '6px 12px', 
                              fontSize: '14px',
                              width: 'auto',
                              backgroundColor: '#000',
                              borderColor: '#000',
                            }}
                          >
                            View Report
                          </button>
                        )}
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
