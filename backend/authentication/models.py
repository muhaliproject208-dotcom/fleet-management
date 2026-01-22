from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
import uuid


class UserRole(models.TextChoices):
    """User role choices"""
    SUPERUSER = 'superuser', 'Super User'
    FLEET_MANAGER = 'fleet_manager', 'Fleet Manager'
    TRANSPORT_SUPERVISOR = 'transport_supervisor', 'Transport Supervisor'


class CustomUserManager(BaseUserManager):
    """Custom user manager for email-based authentication"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', UserRole.SUPERUSER)
        extra_fields.setdefault('email_verified', True)  # Auto-verify superuser emails
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model that integrates with Supabase Auth.
    
    This model stores user metadata locally while Supabase handles
    all authentication logic including:
    - Login/Logout
    - Password reset
    - Email verification via OTP
    - Session management
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, max_length=255)
    supabase_uid = models.CharField(max_length=255, unique=True, null=True, blank=True, 
                                   help_text="Supabase Auth User ID")
    
    # User profile fields
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    
    # Role and permissions
    role = models.CharField(
        max_length=50,
        choices=UserRole.choices,
        default=UserRole.TRANSPORT_SUPERVISOR,
        help_text="User role in the fleet management system"
    )
    
    # Status fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False, 
                                        help_text="Verified via Supabase email OTP")
    
    # Timestamps
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """Return the full name of the user"""
        return f"{self.first_name} {self.last_name}".strip() or self.email
    
    def get_short_name(self):
        """Return the short name of the user"""
        return self.first_name or self.email
    
    @property
    def is_superuser_role(self):
        """Check if user has superuser role"""
        return self.role == UserRole.SUPERUSER
    
    @property
    def is_fleet_manager_role(self):
        """Check if user has fleet manager role"""
        return self.role == UserRole.FLEET_MANAGER
    
    @property
    def is_transport_supervisor_role(self):
        """Check if user has transport supervisor role"""
        return self.role == UserRole.TRANSPORT_SUPERVISOR


class SupabaseAuthSession(models.Model):
    """
    Track Supabase auth sessions for API requests.
    This model stores access tokens returned by Supabase.
    """
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auth_sessions')
    access_token = models.TextField(help_text="Supabase access token (JWT)")
    refresh_token = models.TextField(help_text="Supabase refresh token")
    token_type = models.CharField(max_length=50, default='bearer')
    expires_at = models.DateTimeField(help_text="Token expiration time")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'supabase_auth_sessions'
        verbose_name = 'Supabase Auth Session'
        verbose_name_plural = 'Supabase Auth Sessions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Session for {self.user.email}"
    
    @property
    def is_expired(self):
        """Check if the token is expired"""
        return timezone.now() >= self.expires_at
