from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime
import logging

from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    OTPVerificationSerializer,
    ResendOTPSerializer,
    PasswordResetRequestSerializer,
    PasswordResetOTPVerifySerializer,
    PasswordResetConfirmSerializer,
    TokenRefreshSerializer,
    UserSerializer,
    UserProfileSerializer
)
from .supabase_auth import supabase_auth
from .models import SupabaseAuthSession

logger = logging.getLogger(__name__)
User = get_user_model()


class RegisterView(APIView):
    """
    API endpoint for user registration.
    Supabase handles the actual registration and sends OTP.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Registration validation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Extract data
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        user_metadata = {
            'first_name': serializer.validated_data.get('first_name', ''),
            'last_name': serializer.validated_data.get('last_name', ''),
            'phone_number': serializer.validated_data.get('phone_number', ''),
            'role': serializer.validated_data.get('role'),
        }
        
        # Sign up via Supabase
        result = supabase_auth.sign_up(email, password, user_metadata)
        
        if not result.get('success'):
            return Response(
                {'error': result.get('error', 'Registration failed')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create local user record
        user = User.objects.create_user(
            email=email,
            password=password,
            supabase_uid=result['user'].id if result.get('user') else None,
            first_name=user_metadata.get('first_name', ''),
            last_name=user_metadata.get('last_name', ''),
            phone_number=user_metadata.get('phone_number', ''),
            role=user_metadata.get('role'),
        )
        
        # Immediately request OTP to be sent
        otp_result = supabase_auth.resend_otp(email, 'signup')
        
        return Response({
            'message': 'Registration successful! A 6-digit verification code has been sent to your email.',
            'user': UserSerializer(user).data,
            'email_verification_required': True,
            'otp_sent': otp_result.get('success', False)
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    API endpoint for user login.
    Authentication is handled by Supabase.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        # Sign in via Supabase
        result = supabase_auth.sign_in(email, password)
        
        if not result.get('success'):
            return Response(
                {'error': result.get('error', 'Invalid credentials')},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Get or update local user and sync with Supabase
        try:
            user = User.objects.get(email=email)
            user.supabase_uid = result['user'].id
            user.last_login = timezone.now()
            # Sync email verification status from Supabase
            user.email_verified = result['user'].email_confirmed_at is not None
            
            # Update user metadata from Supabase if available
            user_metadata = result['user'].user_metadata or {}
            if user_metadata.get('first_name'):
                user.first_name = user_metadata.get('first_name', user.first_name)
            if user_metadata.get('last_name'):
                user.last_name = user_metadata.get('last_name', user.last_name)
            if user_metadata.get('phone_number'):
                user.phone_number = user_metadata.get('phone_number', user.phone_number)
            
            user.save()
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found. Please register first.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Store session
        SupabaseAuthSession.objects.create(
            user=user,
            access_token=result['access_token'],
            refresh_token=result['refresh_token'],
            expires_at=result['expires_at']
        )
        
        return Response({
            'message': 'Login successful',
            'user': UserSerializer(user).data,
            'access_token': result['access_token'],
            'refresh_token': result['refresh_token'],
            'token_type': 'Bearer',
            'expires_at': result['expires_at'].isoformat()
        }, status=status.HTTP_200_OK)


class VerifyOTPView(APIView):
    """
    API endpoint for OTP verification.
    Supabase handles OTP verification.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        token = serializer.validated_data['token']
        otp_type = serializer.validated_data.get('type', 'email')
        
        # Verify OTP via Supabase
        result = supabase_auth.verify_otp(email, token, otp_type)
        
        if not result.get('success'):
            return Response(
                {'error': result.get('error', 'OTP verification failed')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update local user
        try:
            user = User.objects.get(email=email)
            user.email_verified = True
            user.save()
        except User.DoesNotExist:
            pass
        
        return Response({
            'message': result.get('message'),
            'verified': True
        }, status=status.HTTP_200_OK)


class ResendOTPView(APIView):
    """
    API endpoint to resend OTP.
    Supabase handles OTP resending.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        otp_type = serializer.validated_data.get('type', 'signup')
        
        # Resend OTP via Supabase
        result = supabase_auth.resend_otp(email, otp_type)
        
        if not result.get('success'):
            return Response(
                {'error': result.get('error', 'Failed to resend OTP')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'message': result.get('message')
        }, status=status.HTTP_200_OK)


class PasswordResetRequestView(APIView):
    """
    API endpoint to request password reset.
    Sends OTP code to user's email.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        
        # Check if user exists
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal if user exists or not for security
            return Response({
                'message': 'If an account with this email exists, a password reset code has been sent.'
            }, status=status.HTTP_200_OK)
        
        # Request password reset OTP via Supabase
        result = supabase_auth.reset_password_email(email)
        
        if not result.get('success'):
            return Response(
                {'error': result.get('error', 'Failed to send password reset code')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'message': 'A 6-digit password reset code has been sent to your email.',
            'email': email
        }, status=status.HTTP_200_OK)


class PasswordResetOTPVerifyView(APIView):
    """
    API endpoint to verify password reset OTP.
    Returns access token for password update.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = PasswordResetOTPVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        token = serializer.validated_data['token']
        
        # Verify OTP via Supabase
        result = supabase_auth.verify_otp_and_get_session(email, token, 'recovery')
        
        if not result.get('success'):
            return Response(
                {'error': result.get('error', 'Invalid or expired OTP')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'message': result.get('message'),
            'access_token': result['access_token'],
            'note': 'Use this access_token to reset your password'
        }, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    """
    API endpoint to confirm password reset.
    Updates password using access token from OTP verification.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        access_token = serializer.validated_data['access_token']
        new_password = serializer.validated_data['new_password']
        
        # Update password via Supabase
        result = supabase_auth.update_password(access_token, new_password)
        
        if not result.get('success'):
            return Response(
                {'error': result.get('error', 'Password reset failed')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'message': 'Password has been reset successfully. You can now login with your new password.'
        }, status=status.HTTP_200_OK)


class TokenRefreshView(APIView):
    """
    API endpoint to refresh access token.
    Supabase handles token refresh.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = TokenRefreshSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        refresh_token = serializer.validated_data['refresh_token']
        
        # Refresh token via Supabase
        result = supabase_auth.refresh_session(refresh_token)
        
        if not result.get('success'):
            return Response(
                {'error': result.get('error', 'Token refresh failed')},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        return Response({
            'access_token': result['access_token'],
            'refresh_token': result['refresh_token'],
            'token_type': 'Bearer',
            'expires_at': result['expires_at'].isoformat()
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    API endpoint for user logout.
    Supabase handles session invalidation.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        access_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not access_token:
            return Response(
                {'error': 'Access token required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Sign out via Supabase
        result = supabase_auth.sign_out(access_token)
        
        # Delete local session
        SupabaseAuthSession.objects.filter(access_token=access_token).delete()
        
        return Response({
            'message': 'Logged out successfully'
        }, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    """
    API endpoint to get user profile.
    Requires authentication.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request):
        user = request.user
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
