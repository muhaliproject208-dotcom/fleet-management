from rest_framework import serializers
from .models import User, UserRole


class UserRegistrationSerializer(serializers.Serializer):
    """Serializer for user registration via Supabase"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True, 
        min_length=8, 
        required=True,
        help_text="Minimum 8 characters with uppercase, lowercase, number and special character"
    )
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    phone_number = serializers.CharField(max_length=20, required=False)
    role = serializers.ChoiceField(
        choices=UserRole.choices,
        default=UserRole.TRANSPORT_SUPERVISOR
    )
    
    def validate_email(self, value):
        """Check if email already exists"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists")
        return value
    
    def validate_password(self, value):
        """Validate password strength to match Supabase requirements"""
        import re
        
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
        
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter")
        
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter")
        
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain at least one number")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("Password must contain at least one special character (!@#$%^&*)")
        
        return value


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)


class OTPVerificationSerializer(serializers.Serializer):
    """Serializer for OTP verification"""
    email = serializers.EmailField(required=True)
    token = serializers.CharField(required=True, min_length=8, max_length=8, help_text="8 digit OTP code")
    type = serializers.CharField(default='email')


class ResendOTPSerializer(serializers.Serializer):
    """Serializer for resending OTP"""
    email = serializers.EmailField(required=True)
    type = serializers.CharField(default='signup')


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request"""
    email = serializers.EmailField(required=True)


class PasswordResetOTPVerifySerializer(serializers.Serializer):
    """Serializer for password reset OTP verification"""
    email = serializers.EmailField(required=True)
    token = serializers.CharField(required=True, min_length=8, max_length=8, help_text="8 digit OTP code")


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation"""
    access_token = serializers.CharField(required=True)
    new_password = serializers.CharField(
        write_only=True, 
        min_length=8, 
        required=True,
        help_text="Minimum 8 characters with uppercase, lowercase, number and special character"
    )
    
    def validate_new_password(self, value):
        """Validate password strength"""
        import re
        
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
        
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter")
        
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter")
        
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain at least one number")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("Password must contain at least one special character (!@#$%^&*)")
        
        return value


class TokenRefreshSerializer(serializers.Serializer):
    """Serializer for token refresh"""
    refresh_token = serializers.CharField(required=True)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 
            'phone_number', 'role', 'is_active', 'email_verified',
            'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'email', 'date_joined', 'last_login']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile with more details"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'supabase_uid', 'first_name', 'last_name',
            'full_name', 'phone_number', 'role', 'is_active',
            'email_verified', 'date_joined', 'last_login', 'updated_at'
        ]
        read_only_fields = [
            'id', 'email', 'supabase_uid', 'email_verified',
            'date_joined', 'last_login', 'updated_at'
        ]
