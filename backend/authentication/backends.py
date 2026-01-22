"""
Supabase Authentication Backend

This module provides Django authentication backend that integrates with Supabase.
"""

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from .supabase_auth import supabase_auth
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class SupabaseAuthBackend(BaseBackend):
    """
    Authentication backend that uses Supabase for authentication
    while maintaining Django user records.
    """
    
    def authenticate(self, request, email=None, password=None, **kwargs):
        """
        Authenticate user via Supabase and return Django user instance.
        
        Args:
            request: The HTTP request
            email: User's email
            password: User's password
        
        Returns:
            User instance if authentication successful, None otherwise
        """
        if email is None or password is None:
            return None
        
        # Authenticate with Supabase
        result = supabase_auth.sign_in(email, password)
        
        if not result.get('success'):
            logger.warning(f"Authentication failed for {email}")
            return None
        
        # Get or create Django user
        try:
            user = User.objects.get(email=email)
            # Update Supabase UID if not set
            if not user.supabase_uid and result.get('user'):
                user.supabase_uid = result['user'].id
                user.save()
        except User.DoesNotExist:
            logger.error(f"User {email} authenticated in Supabase but not found in Django")
            return None
        
        return user
    
    def get_user(self, user_id):
        """
        Get user by ID for session authentication.
        
        Args:
            user_id: User's primary key
        
        Returns:
            User instance or None
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class SupabaseJWTAuthentication:
    """
    Custom JWT authentication that validates Supabase tokens.
    This can be used as a REST framework authentication class.
    """
    
    def authenticate(self, request):
        """
        Authenticate the request using Supabase JWT token.
        
        Args:
            request: DRF request object
        
        Returns:
            Tuple of (user, token) if successful, None otherwise
        """
        from rest_framework import authentication
        from rest_framework import exceptions
        
        # Get token from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.replace('Bearer ', '')
        
        # Verify token with Supabase
        result = supabase_auth.get_user(token)
        
        if not result.get('success'):
            raise exceptions.AuthenticationFailed('Invalid or expired token')
        
        supabase_user = result.get('user')
        
        if not supabase_user:
            raise exceptions.AuthenticationFailed('User not found')
        
        # Get Django user
        try:
            user = User.objects.get(supabase_uid=supabase_user.id)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=supabase_user.email)
                user.supabase_uid = supabase_user.id
                user.save()
            except User.DoesNotExist:
                raise exceptions.AuthenticationFailed('User not found in database')
        
        return (user, token)
    
    def authenticate_header(self, request):
        """
        Return authentication header for 401 responses.
        """
        return 'Bearer realm="api"'
