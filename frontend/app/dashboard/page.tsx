'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { getProfile, logout, getCurrentUser, isAuthenticated, User } from '@/lib/api/auth';
import { getDrivers, Driver } from '@/lib/api/drivers';
import { getVehicles, Vehicle } from '@/lib/api/vehicles';
import { getMechanics, Mechanic } from '@/lib/api/mechanics';

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [mechanics, setMechanics] = useState<Mechanic[]>([]);
  const [loadingData, setLoadingData] = useState(true);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }

    // Load profile on mount
    const fetchProfile = async () => {
      // Try to get cached user first
      const cachedUser = getCurrentUser();
      if (cachedUser) {
        setUser(cachedUser);
      }

      // Fetch fresh profile data
      const response = await getProfile();

      if (response.error) {
        setError(response.error);
        // If token expired, redirect to login
        if (response.error.includes('token') || response.error.includes('auth')) {
          await logout();
          router.push('/login');
        }
      } else if (response.data) {
        setUser(response.data);
        // Update cached user
        localStorage.setItem('user', JSON.stringify(response.data));
      }

      setLoading(false);
    };

    void fetchProfile();
  }, [router]);

  useEffect(() => {
    const fetchDashboardData = async () => {
      if (!isAuthenticated()) return;

      try {
        const [driversRes, vehiclesRes, mechanicsRes] = await Promise.all([
          getDrivers({ is_active: true, page_size: 5 }),
          getVehicles({ is_active: true, page_size: 5 }),
          getMechanics({ is_active: true, page_size: 5 }),
        ]);

        if (driversRes.data) {
          setDrivers(driversRes.data.results || []);
        }

        if (vehiclesRes.data) {
          setVehicles(vehiclesRes.data.results || []);
        }

        if (mechanicsRes.data) {
          setMechanics(mechanicsRes.data.results || []);
        }
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
      } finally {
        setLoadingData(false);
      }
    };

    void fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="container">
        <div className="text-center">
          <div className="spinner" style={{ margin: '0 auto' }}></div>
          <p style={{ marginTop: '20px' }}>Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  const getRoleName = (role: string) => {
    switch (role) {
      case 'fleet_manager':
        return 'Fleet Manager';
      case 'transport_supervisor':
        return 'Transport Supervisor';
      case 'superuser':
        return 'Super User';
      default:
        return role;
    }
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>{getRoleName(user.role)} Dashboard</h1>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(3, 1fr)', 
        gap: '20px', 
        marginTop: '30px' 
      }}>
        {/* Drivers Card */}
        <div 
          onClick={() => router.push('/dashboard/drivers')}
          className="profile-card" 
          style={{ 
            height: '350px', 
            cursor: 'pointer',
            display: 'flex',
            flexDirection: 'column',
            transition: 'transform 0.2s',
          }}
          onMouseOver={(e) => (e.currentTarget.style.transform = 'translateY(-2px)')}
          onMouseOut={(e) => (e.currentTarget.style.transform = 'translateY(0)')}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
            <h2 style={{ margin: 0 }}>Drivers</h2>
          </div>
          {loadingData ? (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', flex: 1 }}>
              <div className="spinner"></div>
            </div>
          ) : drivers.length === 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', flex: 1, color: '#000' }}>
              <span className="material-icons" style={{ fontSize: '48px', marginBottom: '10px' }}>person_off</span>
              <p>No active drivers</p>
            </div>
          ) : (
            <div style={{ flex: 1, overflowY: 'auto' }}>
              {drivers.map((driver) => (
                <div 
                  key={driver.id} 
                  style={{ 
                    padding: '12px', 
                    borderBottom: '1px solid #eee',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                  }}
                >
                  <div>
                    <div style={{ fontWeight: '500' }}>{driver.full_name}</div>
                    <div style={{ fontSize: '12px', color: '#000' }}>{driver.license_number}</div>
                    {driver.phone_number && (
                      <div style={{ fontSize: '12px', color: '#000' }}>{driver.phone_number}</div>
                    )}
                    {driver.email && (
                      <div style={{ fontSize: '12px', color: '#000' }}>{driver.email}</div>
                    )}
                  </div>
                  <span className={driver.is_active ? 'badge badge-verified' : 'badge badge-unverified'}>
                    {driver.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Vehicles Card */}
        <div 
          onClick={() => router.push('/dashboard/vehicles')}
          className="profile-card" 
          style={{ 
            height: '350px', 
            cursor: 'pointer',
            display: 'flex',
            flexDirection: 'column',
            transition: 'transform 0.2s',
          }}
          onMouseOver={(e) => (e.currentTarget.style.transform = 'translateY(-2px)')}
          onMouseOut={(e) => (e.currentTarget.style.transform = 'translateY(0)')}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
            <h2 style={{ margin: 0 }}>Vehicles</h2>
          </div>
          {loadingData ? (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', flex: 1 }}>
              <div className="spinner"></div>
            </div>
          ) : vehicles.length === 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', flex: 1, color: '#000' }}>
              <span className="material-icons" style={{ fontSize: '48px', marginBottom: '10px' }}>directions_car_off</span>
              <p>No active vehicles</p>
            </div>
          ) : (
            <div style={{ flex: 1, overflowY: 'auto' }}>
              {vehicles.map((vehicle) => (
                <div 
                  key={vehicle.id} 
                  style={{ 
                    padding: '12px', 
                    borderBottom: '1px solid #eee',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                  }}
                >
                  <div>
                    <div style={{ fontWeight: '500' }}>{vehicle.registration_number}</div>
                    <div style={{ fontSize: '12px', color: '#000' }}>{vehicle.vehicle_type}</div>
                    {vehicle.driver_name && (
                      <div style={{ fontSize: '12px', color: '#000' }}>
                        {vehicle.driver_name}
                      </div>
                    )}
                  </div>
                  <span className={vehicle.is_active ? 'badge badge-verified' : 'badge badge-unverified'}>
                    {vehicle.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Mechanics Card */}
        <div 
          onClick={() => router.push('/dashboard/mechanics')}
          className="profile-card" 
          style={{ 
            height: '350px', 
            cursor: 'pointer',
            display: 'flex',
            flexDirection: 'column',
            transition: 'transform 0.2s',
          }}
          onMouseOver={(e) => (e.currentTarget.style.transform = 'translateY(-2px)')}
          onMouseOut={(e) => (e.currentTarget.style.transform = 'translateY(0)')}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
            <h2 style={{ margin: 0 }}>Mechanics</h2>
          </div>
          {loadingData ? (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', flex: 1 }}>
              <div className="spinner"></div>
            </div>
          ) : mechanics.length === 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', flex: 1, color: '#000' }}>
              <span className="material-icons" style={{ fontSize: '48px', marginBottom: '10px' }}>build_circle</span>
              <p>No active mechanics</p>
            </div>
          ) : (
            <div style={{ flex: 1, overflowY: 'auto' }}>
              {mechanics.map((mechanic) => (
                <div 
                  key={mechanic.id} 
                  style={{ 
                    padding: '12px', 
                    borderBottom: '1px solid #eee',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                  }}
                >
                  <div>
                    <div style={{ fontWeight: '500' }}>{mechanic.full_name}</div>
                    <div style={{ fontSize: '12px', color: '#000' }}>{mechanic.specialization}</div>
                    {mechanic.phone_number && (
                      <div style={{ fontSize: '12px', color: '#000' }}>{mechanic.phone_number}</div>
                    )}
                  </div>
                  <span className={mechanic.is_active ? 'badge badge-verified' : 'badge badge-unverified'}>
                    {mechanic.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Inspections Section */}
      <div style={{ marginTop: '30px' }}>
        <h2 style={{ marginBottom: '20px', color: '#000' }}>Inspections Management</h2>
        
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(3, 1fr)', 
          gap: '20px' 
        }}>
          {/* Pre-Trip Inspections */}
          <div 
            className="profile-card" 
            style={{ 
              display: 'flex',
              flexDirection: 'column',
              minHeight: '200px',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
              <h3 style={{ margin: 0, color: '#000' }}>Pre-Trip Checklist</h3>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', flex: 1 }}>
              <span className="material-icons" style={{ fontSize: '48px', marginBottom: '10px', color: '#000' }}>
                checklist
              </span>
              <p style={{ textAlign: 'center', color: '#000', marginBottom: '10px' }}>Driver & Vehicle Inspection</p>
              <p style={{ fontSize: '14px', color: '#666', textAlign: 'center', padding: '0 20px', marginBottom: '20px' }}>
                Complete health checks, documentation, and vehicle inspections before journey
              </p>
              <div style={{ display: 'flex', gap: '10px' }}>
                <button
                  onClick={() => router.push('/dashboard/inspections/new')}
                  className="button-primary"
                  style={{ width: 'auto', fontSize: '14px', padding: '8px 16px', backgroundColor: '#000', borderColor: '#000' }}
                >
                  Create New
                </button>
                <button
                  onClick={() => router.push('/dashboard/inspections')}
                  className="button-secondary"
                  style={{ width: 'auto', fontSize: '14px', padding: '8px 16px' }}
                >
                  View All
                </button>
              </div>
            </div>
          </div>

          {/* Post-Trip Inspections */}
          <div 
            className="profile-card" 
            style={{ 
              display: 'flex',
              flexDirection: 'column',
              minHeight: '200px',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
              <h3 style={{ margin: 0, color: '#000' }}>Post-Trip Checklist</h3>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', flex: 1 }}>
              <span className="material-icons" style={{ fontSize: '48px', marginBottom: '10px', color: '#000' }}>
                assignment_turned_in
              </span>
              <p style={{ textAlign: 'center', color: '#000', marginBottom: '10px' }}>Trip Completion & Evaluation</p>
              <p style={{ fontSize: '14px', color: '#666', textAlign: 'center', padding: '0 20px', marginBottom: '20px' }}>
                Report incidents, evaluate performance, and complete post-trip assessment
              </p>
              <div style={{ display: 'flex', gap: '10px' }}>
                <button
                  onClick={() => router.push('/dashboard/inspections?status=approved')}
                  className="button-primary"
                  style={{ width: 'auto', fontSize: '14px', padding: '8px 16px', backgroundColor: '#000', borderColor: '#000' }}
                >
                  View Approved
                </button>
              </div>
            </div>
          </div>

          {/* Inspection Reports */}
          <div 
            onClick={() => router.push('/dashboard/reports')}
            className="profile-card" 
            style={{ 
              cursor: 'pointer',
              display: 'flex',
              flexDirection: 'column',
              transition: 'transform 0.2s',
              minHeight: '200px',
            }}
            onMouseOver={(e) => (e.currentTarget.style.transform = 'translateY(-2px)')}
            onMouseOut={(e) => (e.currentTarget.style.transform = 'translateY(0)')}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
              <h3 style={{ margin: 0, color: '#000' }}>Reports</h3>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', flex: 1 }}>
              <span className="material-icons" style={{ fontSize: '48px', marginBottom: '10px', color: '#000' }}>
                summarize
              </span>
              <p style={{ textAlign: 'center', color: '#000', marginBottom: '10px' }}>Completed Inspections</p>
              <p style={{ fontSize: '14px', color: '#666', textAlign: 'center', padding: '0 20px' }}>
                View approved reports, download PDFs, and review evaluation scores
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Role Info Section */}
      <div style={{ marginTop: '30px' }}>
        <div className="profile-card">
          <p style={{ color: '#666', margin: '0 0 15px 0' }}>
            Logged in as: <strong style={{ color: '#000' }}>{getRoleName(user.role)}</strong>
          </p>
          <p style={{ color: '#000', margin: '0 0 10px 0', fontWeight: '500' }}>What you can do:</p>
          <ul style={{ color: '#666', margin: 0, paddingLeft: '20px', lineHeight: '1.8' }}>
            {user.role === 'fleet_manager' && (
              <>
                <li>Review and approve submitted pre-trip inspections</li>
                <li>View and download completed inspection reports (PDF)</li>
                <li>Manage drivers, vehicles, and mechanics</li>
                <li>Monitor fleet compliance and safety records</li>
              </>
            )}
            {user.role === 'transport_supervisor' && (
              <>
                <li>Create new pre-trip inspections</li>
                <li>Complete post-trip inspection forms</li>
                <li>Track your submitted inspections</li>
                <li>View inspection history and status</li>
              </>
            )}
            {user.role === 'superuser' && (
              <>
                <li>View and manage all inspections</li>
                <li>Access all system reports and analytics</li>
                <li>Manage users, drivers, vehicles, and mechanics</li>
                <li>Configure system settings</li>
              </>
            )}
          </ul>
        </div>
      </div>
    </div>
  );
}
