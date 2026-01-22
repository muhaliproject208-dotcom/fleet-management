'use client';

import { useState, FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { register } from '@/lib/api/auth';

interface PasswordStrength {
  hasMinLength: boolean;
  hasUppercase: boolean;
  hasLowercase: boolean;
  hasNumber: boolean;
  hasSpecialChar: boolean;
}

export default function RegisterPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    phone_number: '',
    role: 'fleet_manager' as 'fleet_manager' | 'transport_supervisor',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState<PasswordStrength>({
    hasMinLength: false,
    hasUppercase: false,
    hasLowercase: false,
    hasNumber: false,
    hasSpecialChar: false,
  });

  const validatePassword = (password: string): PasswordStrength => {
    return {
      hasMinLength: password.length >= 8,
      hasUppercase: /[A-Z]/.test(password),
      hasLowercase: /[a-z]/.test(password),
      hasNumber: /[0-9]/.test(password),
      hasSpecialChar: /[!@#$%^&*(),.?":{}|<>]/.test(password),
    };
  };

  const handlePasswordChange = (password: string) => {
    setFormData({ ...formData, password });
    setPasswordStrength(validatePassword(password));
  };

  const isPasswordValid = (): boolean => {
    return Object.values(passwordStrength).every(Boolean);
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Validation
    if (!formData.email || !formData.password || !formData.first_name || !formData.last_name) {
      setError('Please fill in all required fields');
      setLoading(false);
      return;
    }

    if (!isPasswordValid()) {
      setError('Password does not meet all requirements');
      setLoading(false);
      return;
    }

    const response = await register(formData);

    if (response.error) {
      setError(response.error);
      setLoading(false);
    } else {
      // Store email for OTP verification
      localStorage.setItem('verification_email', formData.email);
      router.push('/verify-otp');
    }
  };

  return (
    <div className="container">
      <div className="card">
        <h1>Create Account</h1>
        <p>Join our fleet management system</p>

        {error && <div className="alert alert-error">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email">Email Address *</label>
            <input
              type="email"
              id="email"
              placeholder="you@company.com"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password *</label>
            <input
              type={showPassword ? 'text' : 'password'}
              id="password"
              placeholder="Min. 8 characters with uppercase, number & special char"
              value={formData.password}
              onChange={(e) => handlePasswordChange(e.target.value)}
              required
            />
            <button
              type="button"
              className="password-toggle"
              onClick={() => setShowPassword(!showPassword)}
              style={{
                background: 'none',
                border: 'none',
                padding: '4px 0',
                color: '#000',
                fontSize: '14px',
                marginTop: '4px',
              }}
            >
              {showPassword ? 'Hide Password' : 'Show Password'}
            </button>
            {formData.password && (
              <div style={{ marginTop: '10px', fontSize: '14px' }}>
                <div style={{ color: passwordStrength.hasMinLength ? '#22c55e' : '#ef4444' }}>
                  {passwordStrength.hasMinLength ? '✓' : '✗'} At least 8 characters
                </div>
                <div style={{ color: passwordStrength.hasUppercase ? '#22c55e' : '#ef4444' }}>
                  {passwordStrength.hasUppercase ? '✓' : '✗'} One uppercase letter
                </div>
                <div style={{ color: passwordStrength.hasLowercase ? '#22c55e' : '#ef4444' }}>
                  {passwordStrength.hasLowercase ? '✓' : '✗'} One lowercase letter
                </div>
                <div style={{ color: passwordStrength.hasNumber ? '#22c55e' : '#ef4444' }}>
                  {passwordStrength.hasNumber ? '✓' : '✗'} One number
                </div>
                <div style={{ color: passwordStrength.hasSpecialChar ? '#22c55e' : '#ef4444' }}>
                  {passwordStrength.hasSpecialChar ? '✓' : '✗'} One special character (!@#$%^&*...)
                </div>
              </div>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="first_name">First Name *</label>
            <input
              type="text"
              id="first_name"
              placeholder="John"
              value={formData.first_name}
              onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="last_name">Last Name *</label>
            <input
              type="text"
              id="last_name"
              placeholder="Doe"
              value={formData.last_name}
              onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="phone_number">Phone Number</label>
            <input
              type="tel"
              id="phone_number"
              placeholder="+1234567890"
              value={formData.phone_number}
              onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
            />
          </div>

          <div className="form-group">
            <label>Role *</label>
            <div className="radio-group">
              <div className="radio-option">
                <input
                  type="radio"
                  id="fleet_manager"
                  name="role"
                  value="fleet_manager"
                  checked={formData.role === 'fleet_manager'}
                  onChange={(e) => setFormData({ ...formData, role: e.target.value as 'fleet_manager' })}
                />
                <label htmlFor="fleet_manager">Fleet Manager</label>
              </div>
              <div className="radio-option">
                <input
                  type="radio"
                  id="transport_supervisor"
                  name="role"
                  value="transport_supervisor"
                  checked={formData.role === 'transport_supervisor'}
                  onChange={(e) => setFormData({ ...formData, role: e.target.value as 'transport_supervisor' })}
                />
                <label htmlFor="transport_supervisor">Transport Supervisor</label>
              </div>
            </div>
          </div>

          <button type="submit" disabled={loading}>
            {loading ? (
              <>
                <span className="spinner"></span>
                Creating Account...
              </>
            ) : (
              'Create Account'
            )}
          </button>
        </form>

        <p className="text-center mt-20">
          Already have an account?{' '}
          <Link href="/login" className="link">
            Sign In
          </Link>
        </p>
      </div>
    </div>
  );
}
