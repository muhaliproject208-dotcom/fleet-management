"""
Custom exception handler for consistent API error responses.
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error response format.
    
    Standard error response format:
    {
        "error": {
            "code": "ERROR_CODE",
            "message": "Human-readable error message",
            "details": {
                "field_name": ["Error messages"]
            }
        }
    }
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # DRF handled the exception, format the response
        error_data = {
            'error': {
                'code': get_error_code(exc),
                'message': get_error_message(exc),
                'details': response.data if isinstance(response.data, dict) else {'detail': response.data}
            }
        }
        response.data = error_data
        return response
    
    # Handle Django ValidationError
    if isinstance(exc, DjangoValidationError):
        error_data = {
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Validation failed',
                'details': exc.message_dict if hasattr(exc, 'message_dict') else {'detail': exc.messages}
            }
        }
        return Response(error_data, status=status.HTTP_400_BAD_REQUEST)
    
    # Handle other exceptions
    error_data = {
        'error': {
            'code': 'INTERNAL_SERVER_ERROR',
            'message': 'An unexpected error occurred',
            'details': {'detail': str(exc)}
        }
    }
    return Response(error_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_error_code(exc):
    """Get appropriate error code based on exception type"""
    from rest_framework.exceptions import (
        ValidationError,
        PermissionDenied,
        NotAuthenticated,
        NotFound,
        MethodNotAllowed,
        Throttled,
    )
    
    if isinstance(exc, ValidationError):
        return 'VALIDATION_ERROR'
    elif isinstance(exc, PermissionDenied):
        return 'PERMISSION_DENIED'
    elif isinstance(exc, NotAuthenticated):
        return 'NOT_AUTHENTICATED'
    elif isinstance(exc, NotFound):
        return 'NOT_FOUND'
    elif isinstance(exc, MethodNotAllowed):
        return 'METHOD_NOT_ALLOWED'
    elif isinstance(exc, Throttled):
        return 'THROTTLED'
    else:
        return 'ERROR'


def get_error_message(exc):
    """Get human-readable error message"""
    from rest_framework.exceptions import (
        ValidationError,
        PermissionDenied,
        NotAuthenticated,
        NotFound,
        MethodNotAllowed,
        Throttled,
    )
    
    if isinstance(exc, ValidationError):
        return 'Validation failed. Please check your input.'
    elif isinstance(exc, PermissionDenied):
        return 'You do not have permission to perform this action.'
    elif isinstance(exc, NotAuthenticated):
        return 'Authentication credentials were not provided or are invalid.'
    elif isinstance(exc, NotFound):
        return 'The requested resource was not found.'
    elif isinstance(exc, MethodNotAllowed):
        return f'Method {exc.detail.code.upper()} is not allowed for this endpoint.'
    elif isinstance(exc, Throttled):
        return 'Request was throttled. Please try again later.'
    else:
        return str(exc.detail) if hasattr(exc, 'detail') else str(exc)
