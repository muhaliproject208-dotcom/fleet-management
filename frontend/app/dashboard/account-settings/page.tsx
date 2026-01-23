'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { getProfile, getCurrentUser, isAuthenticated, User, logout } from '@/lib/api/auth';

export default function AccountSettingsPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const [email, setEmail] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const [savingEmail, setSavingEmail] = useState(false);
  const [savingPassword, setSavingPassword] = useState(false);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }

    const fetchProfile = async () => {
      const cachedUser = getCurrentUser();
      if (cachedUser) {
        setUser(cachedUser);
        setEmail(cachedUser.email || '');
        setPhoneNumber(cachedUser.phone_number || '');
      }

      const response = await getProfile();

      if (response.error) {
        setError(response.error);
        if (response.error.includes('token') || response.error.includes('auth')) {
          await logout();
          router.push('/login');
        }
      } else if (response.data) {
        setUser(response.data);
        setEmail(response.data.email || '');
        setPhoneNumber(response.data.phone_number || '');
        localStorage.setItem('user', JSON.stringify(response.data));
      }

      setLoading(false);
    };

    void fetchProfile();
  }, [router]);

  const handleUpdateEmailPhone = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingEmail(true);
    setError('');
    setSuccessMessage('');

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/profile/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          email,
          phone_number: phoneNumber,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to update account');
      }

      setUser(data);
      localStorage.setItem('user', JSON.stringify(data));
      setSuccessMessage('Email and phone updated successfully');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update account');
    } finally {
      setSavingEmail(false);
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingPassword(true);
    setError('');
    setSuccessMessage('');

    if (newPassword !== confirmPassword) {
      setError('New passwords do not match');
      setSavingPassword(false);
      return;
    }

    if (newPassword.length < 8) {
      setError('Password must be at least 8 characters long');
      setSavingPassword(false);
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/change-password/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || data.error || 'Failed to change password');
      }

      setSuccessMessage('Password changed successfully');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to change password');
    } finally {
      setSavingPassword(false);
    }
  };

  const handleResetPassword = () => {
    router.push('/password-reset');
  };

  if (loading) {
    return (
      <div className="container">
        <div className="text-center">
          <div className="spinner" style={{ margin: '0 auto' }}></div>
          <p style={{ marginTop: '20px' }}>Loading account settings...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <div>
          <h1>Account Settings</h1>
        </div>
        <button onClick={() => router.push('/dashboard')} className="button-secondary" style={{ width: 'auto' }}>
          Back to Dashboard
        </button>
      </div>

      {error && <div className="alert alert-error">{error}</div>}
      {successMessage && <div className="alert alert-success">{successMessage}</div>}

      <div className="profile-card">
        <h2>Email & Phone</h2>
        <form onSubmit={handleUpdateEmailPhone}>
          <div style={{ marginBottom: '20px' }}>
            <label className="label">Email Address</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="input"
              required
            />
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label className="label">Phone Number</label>
            <input
              type="tel"
              value={phoneNumber}
              onChange={(e) => setPhoneNumber(e.target.value)}
              className="input"
            />
          </div>

          <button
            type="submit"
            disabled={savingEmail}
            className="button-primary"
            style={{ width: 'auto', padding: '10px 20px' }}
          >
            {savingEmail ? 'Saving...' : 'Update Email & Phone'}
          </button>
        </form>
      </div>

      <div className="profile-card" style={{ marginTop: '30px' }}>
        <h2>Change Password</h2>
        <form onSubmit={handleChangePassword}>
          <div style={{ marginBottom: '20px' }}>
            <label className="label">Current Password</label>
            <input
              type="password"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              className="input"
              required
            />
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label className="label">New Password</label>
            <input
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              className="input"
              required
            />
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label className="label">Confirm New Password</label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="input"
              required
            />
          </div>

          <div style={{ display: 'flex', gap: '10px' }}>
            <button
              type="submit"
              disabled={savingPassword}
              className="button-primary"
              style={{ width: 'auto', padding: '10px 20px' }}
            >
              {savingPassword ? 'Changing...' : 'Change Password'}
            </button>
            <button
              type="button"
              onClick={handleResetPassword}
              className="button-secondary"
              style={{ width: 'auto', padding: '10px 20px' }}
            >
              Reset Password via Email
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
