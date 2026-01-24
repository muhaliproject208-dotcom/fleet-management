'use client';

import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';
import { logout, getCurrentUser } from '@/lib/api/auth';
import { useState, useEffect, useRef } from 'react';

interface User {
  id?: string;
  email?: string;
  first_name?: string;
  last_name?: string;
  role?: string;
}

export default function Navbar() {
  const router = useRouter();
  const pathname = usePathname();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Use requestAnimationFrame to avoid synchronous setState warning
    const frame = requestAnimationFrame(() => {
      setUser(getCurrentUser());
    });
    return () => cancelAnimationFrame(frame);
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

  const isActive = (path: string) => {
    if (path === '/dashboard') {
      return pathname === path;
    }
    return pathname.startsWith(path);
  };

  const navLinks = [
    { href: '/dashboard', label: 'Dashboard' },
    { href: '/dashboard/inspections', label: 'Inspections' },
    { href: '/dashboard/reports', label: 'Reports' },
    { href: '/dashboard/drivers', label: 'Drivers' },
    { href: '/dashboard/vehicles', label: 'Vehicles' },
    { href: '/dashboard/mechanics', label: 'Mechanics' },
  ];

  return (
    <nav
      suppressHydrationWarning
      style={{
        backgroundColor: '#fff',
        borderBottom: '2px solid #000',
        padding: '0',
        position: 'sticky',
        top: 0,
        zIndex: 100,
      }}
    >
      <div
        style={{
          maxWidth: '1400px',
          margin: '0 auto',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 20px',
          height: '64px',
        }}
      >
        {/* Logo/Brand */}
        <Link
          href="/dashboard"
          style={{
            fontSize: '20px',
            fontWeight: 700,
            color: '#000',
            textDecoration: 'none',
          }}
        >
          Fleet Management
        </Link>

        {/* Navigation Links */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
          }}
        >
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              style={{
                padding: '8px 16px',
                fontSize: '14px',
                fontWeight: 600,
                color: isActive(link.href) ? '#fff' : '#000',
                backgroundColor: isActive(link.href) ? '#000' : 'transparent',
                borderRadius: '6px',
                textDecoration: 'none',
                transition: 'all 0.2s',
                border: isActive(link.href) ? '2px solid #000' : '2px solid transparent',
              }}
              onMouseEnter={(e) => {
                if (!isActive(link.href)) {
                  e.currentTarget.style.backgroundColor = '#f5f5f5';
                }
              }}
              onMouseLeave={(e) => {
                if (!isActive(link.href)) {
                  e.currentTarget.style.backgroundColor = 'transparent';
                }
              }}
            >
              {link.label}
            </Link>
          ))}
        </div>

        {/* User Menu */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{ fontSize: '14px', color: '#666' }}>
            {user?.first_name && user?.last_name 
              ? `${user.first_name} ${user.last_name}` 
              : user?.email}
          </span>
          <div ref={dropdownRef} style={{ position: 'relative' }}>
            <button
              onClick={() => setDropdownOpen(!dropdownOpen)}
              style={{
                padding: '8px 16px',
                fontSize: '14px',
                fontWeight: 600,
                color: '#000',
                backgroundColor: '#fff',
                border: '2px solid #000',
                borderRadius: '6px',
                cursor: 'pointer',
                transition: 'all 0.2s',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#f5f5f5';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#fff';
              }}
            >
              Account
            </button>
            {dropdownOpen && (
              <div
                style={{
                  position: 'absolute',
                  top: 'calc(100% + 8px)',
                  right: 0,
                  backgroundColor: '#fff',
                  border: '2px solid #000',
                  borderRadius: '8px',
                  minWidth: '200px',
                  overflow: 'hidden',
                }}
              >
                <Link
                  href="/dashboard/profile"
                  onClick={() => setDropdownOpen(false)}
                  style={{
                    display: 'block',
                    padding: '12px 16px',
                    fontSize: '14px',
                    fontWeight: 600,
                    color: '#000',
                    textDecoration: 'none',
                    borderBottom: '1px solid #e5e5e5',
                    transition: 'background-color 0.2s',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = '#f5f5f5';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = '#fff';
                  }}
                >
                  Profile
                </Link>
                <Link
                  href="/dashboard/account-settings"
                  onClick={() => setDropdownOpen(false)}
                  style={{
                    display: 'block',
                    padding: '12px 16px',
                    fontSize: '14px',
                    fontWeight: 600,
                    color: '#000',
                    textDecoration: 'none',
                    borderBottom: '1px solid #e5e5e5',
                    transition: 'background-color 0.2s',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = '#f5f5f5';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = '#fff';
                  }}
                >
                  Settings
                </Link>
                <button
                  onClick={handleLogout}
                  style={{
                    display: 'block',
                    width: '100%',
                    padding: '12px 16px',
                    fontSize: '14px',
                    fontWeight: 600,
                    color: '#fff',
                    backgroundColor: '#000',
                    border: 'none',
                    cursor: 'pointer',
                    textAlign: 'left',
                    transition: 'background-color 0.2s',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = '#333';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = '#000';
                  }}
                >
                  Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
