'use client';

import { useState, FormEvent, useRef, KeyboardEvent } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { requestPasswordReset, verifyPasswordResetOTP, confirmPasswordReset } from '@/lib/api/auth';

export default function PasswordResetPage() {
  const router = useRouter();
  const [step, setStep] = useState<'request' | 'verify' | 'reset'>('request');
  const [email, setEmail] = useState('');
  const [otp, setOtp] = useState(['', '', '', '', '', '', '', '']);
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [resetToken, setResetToken] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  const handleRequestReset = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    if (!email) {
      setError('Please enter your email address');
      setLoading(false);
      return;
    }

    const response = await requestPasswordReset(email);

    if (response.error) {
      setError(response.error);
      setLoading(false);
    } else {
      setSuccess('Reset code sent to your email!');
      setTimeout(() => {
        setStep('verify');
        setSuccess('');
      }, 1500);
      setLoading(false);
    }
  };

  const handleOtpChange = (index: number, value: string) => {
    if (value.length > 1) return;
    if (!/^\d*$/.test(value)) return;

    const newOtp = [...otp];
    newOtp[index] = value;
    setOtp(newOtp);

    if (value && index < 7) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleOtpKeyDown = (index: number, e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handleVerifyOTP = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    const otpCode = otp.join('');

    if (otpCode.length !== 8) {
      setError('Please enter the complete 8-digit code');
      setLoading(false);
      return;
    }

    const response = await verifyPasswordResetOTP(email, otpCode);

    if (response.error) {
      setError(response.error);
      setLoading(false);
    } else {
      setSuccess('Code verified!');
      setResetToken(response.data?.access_token || '');
      setTimeout(() => {
        setStep('reset');
        setSuccess('');
      }, 1000);
      setLoading(false);
    }
  };

  const handleResetPassword = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    if (newPassword.length < 8) {
      setError('Password must be at least 8 characters');
      setLoading(false);
      return;
    }

    if (newPassword !== confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    const response = await confirmPasswordReset(resetToken, newPassword);

    if (response.error) {
      setError(response.error);
      setLoading(false);
    } else {
      setSuccess('Password reset successful!');
      setTimeout(() => {
        router.push('/login');
      }, 1500);
    }
  };

  return (
    <div className="container">
      <div className="card">
        {step === 'request' && (
          <>
            <h1>Reset Password</h1>
            <p>Enter your email to receive a password reset code</p>

            {error && <div className="alert alert-error">{error}</div>}
            {success && <div className="alert alert-success">{success}</div>}

            <form onSubmit={handleRequestReset}>
              <div className="form-group">
                <label htmlFor="email">Email Address</label>
                <input
                  type="email"
                  id="email"
                  placeholder="you@company.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>

              <button type="submit" disabled={loading}>
                {loading ? (
                  <>
                    <span className="spinner"></span>
                    Sending Code...
                  </>
                ) : (
                  'Send Reset Code'
                )}
              </button>
            </form>

            <p className="text-center mt-20">
              Remember your password?{' '}
              <Link href="/login" className="link">
                Sign In
              </Link>
            </p>
          </>
        )}

        {step === 'verify' && (
          <>
            <h1>Verify Code</h1>
            <p>
              Enter the 8-digit code sent to <strong>{email}</strong>
            </p>

            {error && <div className="alert alert-error">{error}</div>}
            {success && <div className="alert alert-success">{success}</div>}

            <form onSubmit={handleVerifyOTP}>
              <div className="otp-input-group">
                {otp.map((digit, index) => (
                  <input
                    key={index}
                    ref={(el) => {
                      inputRefs.current[index] = el;
                    }}
                    type="text"
                    maxLength={1}
                    className="otp-input"
                    value={digit}
                    onChange={(e) => handleOtpChange(index, e.target.value)}
                    onKeyDown={(e) => handleOtpKeyDown(index, e)}
                    autoFocus={index === 0}
                  />
                ))}
              </div>

              <button type="submit" disabled={loading}>
                {loading ? (
                  <>
                    <span className="spinner"></span>
                    Verifying...
                  </>
                ) : (
                  'Verify Code'
                )}
              </button>
            </form>

            <p className="text-center mt-20">
              <button
                type="button"
                className="link"
                onClick={() => setStep('request')}
                style={{
                  background: 'none',
                  border: 'none',
                  padding: 0,
                  width: 'auto',
                  display: 'inline',
                }}
              >
                Back to Email Entry
              </button>
            </p>
          </>
        )}

        {step === 'reset' && (
          <>
            <h1>Set New Password</h1>
            <p>Enter your new password below</p>

            {error && <div className="alert alert-error">{error}</div>}
            {success && <div className="alert alert-success">{success}</div>}

            <form onSubmit={handleResetPassword}>
              <div className="form-group">
                <label htmlFor="new_password">New Password</label>
                <input
                  type={showNewPassword ? 'text' : 'password'}
                  id="new_password"
                  placeholder="Min. 8 characters with uppercase, number & special char"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  required
                />
                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowNewPassword(!showNewPassword)}
                  style={{
                    background: 'none',
                    border: 'none',
                    padding: '4px 0',
                    color: '#000',
                    fontSize: '14px',
                    marginTop: '4px',
                  }}
                >
                  {showNewPassword ? 'Hide Password' : 'Show Password'}
                </button>
              </div>

              <div className="form-group">
                <label htmlFor="confirm_password">Confirm Password</label>
                <input
                  type={showConfirmPassword ? 'text' : 'password'}
                  id="confirm_password"
                  placeholder="Re-enter your new password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                />
                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  style={{
                    background: 'none',
                    border: 'none',
                    padding: '4px 0',
                    color: '#000',
                    fontSize: '14px',
                    marginTop: '4px',
                  }}
                >
                  {showConfirmPassword ? 'Hide Password' : 'Show Password'}
                </button>
              </div>

              <button type="submit" disabled={loading}>
                {loading ? (
                  <>
                    <span className="spinner"></span>
                    Resetting Password...
                  </>
                ) : (
                  'Reset Password'
                )}
              </button>
            </form>
          </>
        )}
      </div>
    </div>
  );
}
