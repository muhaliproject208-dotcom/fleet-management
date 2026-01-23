'use client';

import { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { getProfile, logout, getCurrentUser, isAuthenticated, User } from '@/lib/api/auth';
import { getDrivers, Driver } from '@/lib/api/drivers';
import { getVehicles, Vehicle } from '@/lib/api/vehicles';
import { getMechanics, Mechanic } from '@/lib/api/mechanics';

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

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

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = async () => {
    await logout();
    router.push('/login');
  };

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
        <div>
          <h1>{getRoleName(user.role)} Dashboard</h1>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px', position: 'relative' }}>
          <div ref={dropdownRef} style={{ position: 'relative' }}>
            <button
              onClick={() => setDropdownOpen(!dropdownOpen)}
              className="button-secondary"
              style={{ 
                width: '40px',
                height: '40px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                padding: '0',
                borderRadius: '50%'
              }}
              title="Settings"
            >
              <span className="material-icons" style={{ fontSize: '24px' }}>
                settings
              </span>
            </button>
            {dropdownOpen && (
              <div
                style={{
                  position: 'absolute',
                  top: '100%',
                  right: 0,
                  marginTop: '8px',
                  backgroundColor: 'white',
                  border: '1px solid #ddd',
                  borderRadius: '8px',
                  minWidth: '200px',
                  zIndex: 1000,
                }}
              >
                <Link
                  href="/dashboard/profile"
                  style={{
                    display: 'block',
                    width: '100%',
                    padding: '12px 16px',
                    textAlign: 'left',
                    textDecoration: 'none',
                    color: 'inherit',
                    fontSize: '14px',
                    borderBottom: '1px solid #eee',
                  }}
                >
                  View Profile
                </Link>
                <Link
                  href="/dashboard/account-settings"
                  style={{
                    display: 'block',
                    width: '100%',
                    padding: '12px 16px',
                    textAlign: 'left',
                    textDecoration: 'none',
                    color: 'inherit',
                    fontSize: '14px',
                  }}
                >
                  Account Settings
                </Link>
              </div>
            )}
          </div>
          <button onClick={handleLogout} className="button-secondary" style={{ width: 'auto' }}>
            Logout
          </button>
        </div>
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

      {user.role === 'fleet_manager' && (
        <div className="profile-card" style={{ marginTop: '30px' }}>
          <h2>Fleet Manager Dashboard</h2>
          <p style={{ color: '#000' }}>
            Welcome to your Fleet Manager dashboard. Vehicle and fleet management features will be available here soon.
          </p>
        </div>
      )}

      {user.role === 'transport_supervisor' && (
        <div className="profile-card" style={{ marginTop: '30px' }}>
          <h2>Transport Supervisor Dashboard</h2>
          <p style={{ color: '#000' }}>
            Welcome to your Transport Supervisor dashboard. Trip monitoring and scheduling features will be available here soon.
          </p>
        </div>
      )}
    </div>
  );
}
