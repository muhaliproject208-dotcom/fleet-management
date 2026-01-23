"""
Audit logging model for tracking all actions in the fleet management system.
"""

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from authentication.models import User


class AuditAction(models.TextChoices):
    """Audit action choices"""
    CREATE = 'create', 'Create'
    UPDATE = 'update', 'Update'
    DELETE = 'delete', 'Delete'
    APPROVE = 'approve', 'Approve'
    REJECT = 'reject', 'Reject'
    SUBMIT = 'submit', 'Submit'
    VIEW = 'view', 'View'
    EXPORT = 'export', 'Export'


class AuditLog(models.Model):
    """
    Audit log for tracking all actions in the system.
    Uses generic foreign key to track changes to any model.
    """
    
    # Who performed the action
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs',
        help_text="User who performed the action"
    )
    
    # What action was performed
    action = models.CharField(
        max_length=20,
        choices=AuditAction.choices,
        help_text="Type of action performed"
    )
    
    # Which object was affected (generic foreign key)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        help_text="Type of object affected"
    )
    object_id = models.PositiveIntegerField(
        help_text="ID of the object affected"
    )
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Details about the changes
    changes = models.JSONField(
        null=True,
        blank=True,
        help_text="JSON representation of changes made"
    )
    
    # Additional context
    description = models.TextField(
        blank=True,
        help_text="Human-readable description of the action"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the user"
    )
    user_agent = models.CharField(
        max_length=255,
        blank=True,
        help_text="User agent string"
    )
    
    # Timestamp
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When the action occurred"
    )
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
        ]
    
    def __str__(self):
        user_name = self.user.get_full_name() if self.user else 'System'
        return f"{user_name} - {self.action} - {self.content_type} #{self.object_id} - {self.timestamp}"
    
    @classmethod
    def log_action(cls, user, action, obj, changes=None, description='', request=None):
        """
        Convenience method to create an audit log entry.
        
        Args:
            user: User who performed the action
            action: Action type (from AuditAction)
            obj: The object affected
            changes: Dictionary of changes (before/after)
            description: Human-readable description
            request: HTTP request object (for IP and user agent)
        """
        ip_address = None
        user_agent = ''
        
        if request:
            # Get IP address
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')
            
            # Get user agent
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]
        
        return cls.objects.create(
            user=user,
            action=action,
            content_object=obj,
            changes=changes,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent
        )
