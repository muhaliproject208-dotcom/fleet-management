"""
Supabase Authentication Service

This module handles all authentication operations through Supabase.
All auth logic is managed by Supabase including:
- Sign up with email verification (OTP)
- Sign in
- Password reset
- Email verification
- Token refresh
"""

from gotrue import SyncGoTrueClient
from decouple import config
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class SupabaseAuthService:
    """
    Service class for Supabase authentication operations.
    This wraps Supabase's GoTrue client for authentication.
    """
    
    def __init__(self):
        self.supabase_url = config('SUPABASE_URL')
        self.supabase_key = config('SUPABASE_KEY')
        self.auth_client = SyncGoTrueClient(
            url=f"{self.supabase_url}/auth/v1",
            headers={
                "apiKey": self.supabase_key,
                "Authorization": f"Bearer {self.supabase_key}"
            }
        )
    
    def sign_up(self, email: str, password: str, user_metadata: Optional[Dict] = None) -> Dict:
        """
        Sign up a new user with Supabase.
        Supabase will automatically send an email verification OTP.
        
        Args:
            email: User's email address
            password: User's password
            user_metadata: Additional user metadata (first_name, last_name, role, etc.)
        
        Returns:
            Dictionary with user data and session info
        """
        try:
            options = {
                'email_redirect_to': None,  # Disable confirmation link, use OTP only
            }
            if user_metadata:
                options['data'] = user_metadata
            
            # Supabase handles email verification automatically
            response = self.auth_client.sign_up({
                'email': email,
                'password': password,
                'options': options
            })
            
            return {
                'success': True,
                'user': response.user,
                'session': response.session,
                'message': 'Sign up successful. Please check your email for verification OTP (6-digit code).'
            }
        except Exception as e:
            logger.error(f"Sign up error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def sign_in(self, email: str, password: str) -> Dict:
        """
        Sign in a user with email and password via Supabase.
        
        Args:
            email: User's email address
            password: User's password
        
        Returns:
            Dictionary with session and user data
        """
        try:
            response = self.auth_client.sign_in_with_password({
                'email': email,
                'password': password
            })
            
            if not response.session:
                return {
                    'success': False,
                    'error': 'Invalid credentials'
                }
            
            return {
                'success': True,
                'user': response.user,
                'session': response.session,
                'access_token': response.session.access_token,
                'refresh_token': response.session.refresh_token,
                'expires_at': self._calculate_expiry(response.session.expires_in)
            }
        except Exception as e:
            logger.error(f"Sign in error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_otp(self, email: str, token: str, type: str = 'email') -> Dict:
        """
        Verify email using OTP sent by Supabase.
        
        Args:
            email: User's email address
            token: OTP token received via email
            type: Type of verification (default: 'email')
        
        Returns:
            Dictionary with verification result
        """
        try:
            response = self.auth_client.verify_otp({
                'email': email,
                'token': token,
                'type': type
            })
            
            return {
                'success': True,
                'user': response.user,
                'session': response.session,
                'message': 'Email verified successfully'
            }
        except Exception as e:
            logger.error(f"OTP verification error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def resend_otp(self, email: str, type: str = 'signup') -> Dict:
        """
        Resend OTP for email verification.
        
        Args:
            email: User's email address
            type: Type of OTP (signup, email_change, etc.)
        
        Returns:
            Dictionary with result
        """
        try:
            self.auth_client.resend({
                'email': email,
                'type': type
            })
            
            return {
                'success': True,
                'message': 'OTP resent successfully. Please check your email.'
            }
        except Exception as e:
            logger.error(f"Resend OTP error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def reset_password_email(self, email: str) -> Dict:
        """
        Send password reset OTP via Supabase.
        
        Args:
            email: User's email address
        
        Returns:
            Dictionary with result
        """
        try:
            # Request OTP for password reset
            self.auth_client.reset_password_email(email)
            
            return {
                'success': True,
                'message': 'Password reset code sent to your email. Please check your inbox.'
            }
        except Exception as e:
            logger.error(f"Password reset error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_otp_and_get_session(self, email: str, token: str, type: str = 'recovery') -> Dict:
        """
        Verify OTP and get session for password reset.
        
        Args:
            email: User's email address
            token: OTP token
            type: Type of OTP verification (default: 'recovery' for password reset)
        
        Returns:
            Dictionary with session data
        """
        try:
            response = self.auth_client.verify_otp({
                'email': email,
                'token': token,
                'type': type
            })
            
            if not response.session:
                return {
                    'success': False,
                    'error': 'Invalid or expired OTP'
                }
            
            return {
                'success': True,
                'session': response.session,
                'access_token': response.session.access_token,
                'user': response.user,
                'message': 'OTP verified successfully. You can now reset your password.'
            }
        except Exception as e:
            logger.error(f"OTP verification error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_password(self, access_token: str, new_password: str) -> Dict:
        """
        Update user's password.
        
        Args:
            access_token: User's current access token
            new_password: New password
        
        Returns:
            Dictionary with result
        """
        try:
            # Set the session with the access token
            self.auth_client.set_session(access_token, '')
            
            response = self.auth_client.update_user({
                'password': new_password
            })
            
            return {
                'success': True,
                'user': response.user,
                'message': 'Password updated successfully'
            }
        except Exception as e:
            logger.error(f"Password update error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def refresh_session(self, refresh_token: str) -> Dict:
        """
        Refresh user session using refresh token.
        
        Args:
            refresh_token: Refresh token
        
        Returns:
            Dictionary with new session data
        """
        try:
            response = self.auth_client.refresh_session(refresh_token)
            
            return {
                'success': True,
                'session': response.session,
                'access_token': response.session.access_token,
                'refresh_token': response.session.refresh_token,
                'expires_at': self._calculate_expiry(response.session.expires_in)
            }
        except Exception as e:
            logger.error(f"Refresh session error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def sign_out(self, access_token: str) -> Dict:
        """
        Sign out user from Supabase.
        
        Args:
            access_token: User's access token
        
        Returns:
            Dictionary with result
        """
        try:
            self.auth_client.set_session(access_token, '')
            self.auth_client.sign_out()
            
            return {
                'success': True,
                'message': 'Signed out successfully'
            }
        except Exception as e:
            logger.error(f"Sign out error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_user(self, access_token: str) -> Dict:
        """
        Get user information from access token.
        
        Args:
            access_token: User's access token
        
        Returns:
            Dictionary with user data
        """
        try:
            self.auth_client.set_session(access_token, '')
            user = self.auth_client.get_user()
            
            return {
                'success': True,
                'user': user
            }
        except Exception as e:
            logger.error(f"Get user error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def _calculate_expiry(expires_in: int) -> datetime:
        """Calculate token expiry datetime from expires_in seconds"""
        return datetime.now() + timedelta(seconds=expires_in)


# Singleton instance
supabase_auth = SupabaseAuthService()
