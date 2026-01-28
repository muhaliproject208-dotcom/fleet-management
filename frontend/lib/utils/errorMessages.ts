/**
 * Error Message Utility
 * Converts raw API error messages to user-friendly messages
 */

// Map of raw error patterns to user-friendly messages
const errorMessageMap: Record<string, string> = {
  // Authentication Errors
  'invalid_credentials': 'The email or password you entered is incorrect. Please try again.',
  'invalid credentials': 'The email or password you entered is incorrect. Please try again.',
  'Invalid credentials': 'The email or password you entered is incorrect. Please try again.',
  'user not found': 'No account found with this email address. Please check your email or register.',
  'User not found': 'No account found with this email address. Please check your email or register.',
  'email not verified': 'Please verify your email address before logging in.',
  'Email not verified': 'Please verify your email address before logging in.',
  'account disabled': 'Your account has been disabled. Please contact support.',
  'Account disabled': 'Your account has been disabled. Please contact support.',
  'token expired': 'Your session has expired. Please log in again.',
  'Token expired': 'Your session has expired. Please log in again.',
  'invalid token': 'Invalid authentication. Please log in again.',
  'Invalid token': 'Invalid authentication. Please log in again.',
  'Authentication expired': 'Your session has expired. Please log in again.',
  
  // Registration Errors
  'email already exists': 'An account with this email already exists. Please log in or use a different email.',
  'Email already exists': 'An account with this email already exists. Please log in or use a different email.',
  'user already exists': 'An account with this email already exists. Please log in or use a different email.',
  'User already exists': 'An account with this email already exists. Please log in or use a different email.',
  'password too weak': 'Please choose a stronger password with at least 8 characters, including uppercase, lowercase, numbers, and special characters.',
  'Password too weak': 'Please choose a stronger password with at least 8 characters, including uppercase, lowercase, numbers, and special characters.',
  'invalid email format': 'Please enter a valid email address.',
  'Invalid email format': 'Please enter a valid email address.',
  
  // OTP/Verification Errors
  'invalid otp': 'The verification code you entered is incorrect. Please try again.',
  'Invalid OTP': 'The verification code you entered is incorrect. Please try again.',
  'otp expired': 'The verification code has expired. Please request a new one.',
  'OTP expired': 'The verification code has expired. Please request a new one.',
  'too many attempts': 'Too many failed attempts. Please wait a few minutes before trying again.',
  'Too many attempts': 'Too many failed attempts. Please wait a few minutes before trying again.',
  
  // Password Reset Errors
  'password mismatch': 'The passwords you entered do not match.',
  'Password mismatch': 'The passwords you entered do not match.',
  'same as old password': 'Your new password cannot be the same as your old password.',
  'Same as old password': 'Your new password cannot be the same as your old password.',
  
  // Permission Errors
  'permission denied': 'You do not have permission to perform this action.',
  'Permission denied': 'You do not have permission to perform this action.',
  'not authorized': 'You are not authorized to access this resource.',
  'Not authorized': 'You are not authorized to access this resource.',
  'Only fleet managers': 'This action requires Fleet Manager permissions.',
  'only fleet managers': 'This action requires Fleet Manager permissions.',
  
  // Inspection Errors
  'inspection not found': 'The inspection you are looking for could not be found.',
  'Inspection not found': 'The inspection you are looking for could not be found.',
  'cannot create checks': 'Unable to add checks to this inspection. It may be in a status that does not allow modifications.',
  'Cannot create checks': 'Unable to add checks to this inspection. It may be in a status that does not allow modifications.',
  'cannot modify': 'This inspection cannot be modified in its current status.',
  'Cannot modify': 'This inspection cannot be modified in its current status.',
  'already approved': 'This inspection has already been approved.',
  'Already approved': 'This inspection has already been approved.',
  'already rejected': 'This inspection has already been rejected.',
  'Already rejected': 'This inspection has already been rejected.',
  'draft inspections': 'Draft inspections cannot be used for this action. Please submit the inspection first.',
  'Draft inspections': 'Draft inspections cannot be used for this action. Please submit the inspection first.',
  
  // Driver Errors
  'driver not found': 'The driver you are looking for could not be found.',
  'Driver not found': 'The driver you are looking for could not be found.',
  'driver already exists': 'A driver with this information already exists.',
  'Driver already exists': 'A driver with this information already exists.',
  
  // Vehicle Errors
  'vehicle not found': 'The vehicle you are looking for could not be found.',
  'Vehicle not found': 'The vehicle you are looking for could not be found.',
  'vehicle already exists': 'A vehicle with this registration number already exists.',
  'Vehicle already exists': 'A vehicle with this registration number already exists.',
  
  // Mechanic Errors
  'mechanic not found': 'The mechanic you are looking for could not be found.',
  'Mechanic not found': 'The mechanic you are looking for could not be found.',
  
  // Network/Server Errors
  'network error': 'Unable to connect to the server. Please check your internet connection and try again.',
  'Network error': 'Unable to connect to the server. Please check your internet connection and try again.',
  'server error': 'Something went wrong on our end. Please try again later.',
  'Server error': 'Something went wrong on our end. Please try again later.',
  'internal server error': 'Something went wrong on our end. Please try again later.',
  'Internal server error': 'Something went wrong on our end. Please try again later.',
  'timeout': 'The request took too long. Please try again.',
  'Timeout': 'The request took too long. Please try again.',
  'Failed to fetch': 'Unable to connect to the server. Please check your internet connection.',
  
  // PDF Errors
  'Failed to generate PDF': 'Unable to generate the PDF. Please try again.',
  'Failed to download PDF': 'Unable to download the PDF. Please try again.',
  'requires_approval': 'This inspection must be approved before the PDF can be generated.',
  
  // Validation Errors
  'required field': 'This field is required.',
  'Required field': 'This field is required.',
  'invalid format': 'The value you entered is in an invalid format.',
  'Invalid format': 'The value you entered is in an invalid format.',
  'too long': 'The value you entered is too long.',
  'Too long': 'The value you entered is too long.',
  'too short': 'The value you entered is too short.',
  'Too short': 'The value you entered is too short.',
};

// Field-specific error messages
const fieldErrorMap: Record<string, Record<string, string>> = {
  email: {
    required: 'Please enter your email address.',
    invalid: 'Please enter a valid email address.',
    exists: 'An account with this email already exists.',
    'not found': 'No account found with this email address.',
    format: 'Please enter a valid email address (e.g., name@company.com).',
  },
  password: {
    required: 'Please enter your password.',
    weak: 'Password must be at least 8 characters with uppercase, lowercase, number, and special character.',
    mismatch: 'Passwords do not match.',
    incorrect: 'The password you entered is incorrect.',
    same: 'New password cannot be the same as the current password.',
  },
  first_name: {
    required: 'Please enter your first name.',
    invalid: 'First name can only contain letters.',
    'too long': 'First name is too long (maximum 50 characters).',
  },
  last_name: {
    required: 'Please enter your last name.',
    invalid: 'Last name can only contain letters.',
    'too long': 'Last name is too long (maximum 50 characters).',
  },
  phone_number: {
    required: 'Please enter your phone number.',
    invalid: 'Please enter a valid phone number.',
    format: 'Phone number should be in format: +260XXXXXXXXX',
  },
  driver: {
    required: 'Please select a driver.',
    'not found': 'The selected driver could not be found.',
  },
  vehicle: {
    required: 'Please select a vehicle.',
    'not found': 'The selected vehicle could not be found.',
  },
  route: {
    required: 'Please enter the route.',
    invalid: 'Please enter a valid route (e.g., Lusaka - Ndola).',
  },
  inspection_date: {
    required: 'Please select an inspection date.',
    invalid: 'Please select a valid date.',
    past: 'Inspection date cannot be in the past.',
  },
  otp: {
    required: 'Please enter the verification code.',
    invalid: 'The verification code is incorrect.',
    expired: 'The verification code has expired. Please request a new one.',
    incomplete: 'Please enter the complete verification code.',
  },
};

/**
 * Get a user-friendly error message from an API error response
 */
export function getFriendlyErrorMessage(error: string | undefined | null): string {
  if (!error) {
    return 'An unexpected error occurred. Please try again.';
  }

  // Check for exact matches first
  if (errorMessageMap[error]) {
    return errorMessageMap[error];
  }

  // Check for partial matches (case-insensitive)
  const lowerError = error.toLowerCase();
  for (const [pattern, message] of Object.entries(errorMessageMap)) {
    if (lowerError.includes(pattern.toLowerCase())) {
      return message;
    }
  }

  // Handle Django REST Framework style errors
  if (error.includes('This field')) {
    return error.replace('This field', 'This value');
  }

  // Handle array-style errors from DRF
  if (error.startsWith('[') && error.endsWith(']')) {
    try {
      const parsed = JSON.parse(error);
      if (Array.isArray(parsed) && parsed.length > 0) {
        return getFriendlyErrorMessage(parsed[0]);
      }
    } catch {
      // Not valid JSON, continue
    }
  }

  // Handle object-style errors from DRF
  if (error.startsWith('{') && error.endsWith('}')) {
    try {
      const parsed = JSON.parse(error);
      const firstKey = Object.keys(parsed)[0];
      if (firstKey) {
        const fieldError = parsed[firstKey];
        return getFieldErrorMessage(firstKey, Array.isArray(fieldError) ? fieldError[0] : fieldError);
      }
    } catch {
      // Not valid JSON, continue
    }
  }

  // Clean up technical error messages
  const cleanedError = cleanTechnicalError(error);
  
  return cleanedError;
}

/**
 * Get a field-specific error message
 */
export function getFieldErrorMessage(fieldName: string, errorType: string): string {
  const fieldErrors = fieldErrorMap[fieldName];
  if (fieldErrors) {
    // Check exact match
    if (fieldErrors[errorType]) {
      return fieldErrors[errorType];
    }
    // Check partial match
    for (const [type, message] of Object.entries(fieldErrors)) {
      if (errorType.toLowerCase().includes(type.toLowerCase())) {
        return message;
      }
    }
  }

  // Fall back to generic field error
  const fieldLabel = fieldName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  
  if (errorType.toLowerCase().includes('required') || errorType.toLowerCase().includes('blank')) {
    return `Please enter ${fieldLabel.toLowerCase()}.`;
  }
  if (errorType.toLowerCase().includes('invalid') || errorType.toLowerCase().includes('format')) {
    return `Please enter a valid ${fieldLabel.toLowerCase()}.`;
  }
  if (errorType.toLowerCase().includes('exists') || errorType.toLowerCase().includes('unique')) {
    return `This ${fieldLabel.toLowerCase()} is already in use.`;
  }

  return `${fieldLabel}: ${errorType}`;
}

/**
 * Clean up technical error messages to be more user-friendly
 */
function cleanTechnicalError(error: string): string {
  // Remove technical prefixes
  let cleaned = error
    .replace(/^Error:\s*/i, '')
    .replace(/^Exception:\s*/i, '')
    .replace(/^\[.*?\]\s*/, '')
    .replace(/^{\s*".*?":\s*"?/, '')
    .replace(/"?\s*}$/, '');

  // Capitalize first letter
  cleaned = cleaned.charAt(0).toUpperCase() + cleaned.slice(1);

  // Add period if missing
  if (cleaned && !cleaned.endsWith('.') && !cleaned.endsWith('!') && !cleaned.endsWith('?')) {
    cleaned += '.';
  }

  return cleaned;
}

/**
 * Parse and format validation errors from API response
 */
export function parseValidationErrors(errors: Record<string, string[]> | string): Record<string, string> {
  const result: Record<string, string> = {};

  if (typeof errors === 'string') {
    result.general = getFriendlyErrorMessage(errors);
    return result;
  }

  for (const [field, fieldErrors] of Object.entries(errors)) {
    if (Array.isArray(fieldErrors) && fieldErrors.length > 0) {
      result[field] = getFieldErrorMessage(field, fieldErrors[0]);
    } else if (typeof fieldErrors === 'string') {
      result[field] = getFieldErrorMessage(field, fieldErrors);
    }
  }

  return result;
}

/**
 * Get error messages for multiple fields
 */
export function getFormErrors(errors: Record<string, string | string[]>): string[] {
  const messages: string[] = [];

  for (const [field, error] of Object.entries(errors)) {
    const errorStr = Array.isArray(error) ? error[0] : error;
    messages.push(getFieldErrorMessage(field, errorStr));
  }

  return messages;
}

const errorUtils = {
  getFriendlyErrorMessage,
  getFieldErrorMessage,
  parseValidationErrors,
  getFormErrors,
};

export default errorUtils;
