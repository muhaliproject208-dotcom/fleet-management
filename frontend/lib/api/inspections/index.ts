// Main Inspections API
import { API_URL } from '../index';
import type {
  PreTripInspection,
  PreTripInspectionFull,
  CreateInspectionData,
  UpdateInspectionData,
  InspectionStatus,
  PaginatedResponse,
  APIResponse,
} from './types';

export const getInspections = async (params?: {
  status?: InspectionStatus;
  inspection_date_from?: string;
  inspection_date_to?: string;
  driver?: string;
  vehicle?: string;
  search?: string;
  page?: number;
  page_size?: number;
}): Promise<APIResponse<PaginatedResponse<PreTripInspection>>> => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      return { error: 'No authentication token found' };
    }

    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, value.toString());
        }
      });
    }

    const response = await fetch(
      `${API_URL}/inspections/?${queryParams.toString()}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (!response.ok) {
      const errorData = await response.json();
      return { error: errorData.detail || 'Failed to fetch inspections' };
    }

    const data: PaginatedResponse<PreTripInspection> = await response.json();
    return { data };
  } catch (error) {
    return {
      error: error instanceof Error ? error.message : 'Failed to fetch inspections',
    };
  }
};

export const getInspection = async (id: string): Promise<APIResponse<PreTripInspectionFull>> => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      return { error: 'No authentication token found' };
    }

    const response = await fetch(`${API_URL}/inspections/${id}/`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      return { error: errorData.detail || 'Failed to fetch inspection' };
    }

    const data: PreTripInspectionFull = await response.json();
    return { data };
  } catch (error) {
    return {
      error: error instanceof Error ? error.message : 'Failed to fetch inspection',
    };
  }
};

export const createInspection = async (
  inspectionData: CreateInspectionData
): Promise<APIResponse<PreTripInspection>> => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      return { error: 'No authentication token found' };
    }

    const response = await fetch(`${API_URL}/inspections/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(inspectionData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      return {
        error: errorData.detail || errorData.message || 'Failed to create inspection',
      };
    }

    const data: PreTripInspection = await response.json();
    return { data };
  } catch (error) {
    return {
      error: error instanceof Error ? error.message : 'Failed to create inspection',
    };
  }
};

export const updateInspection = async (
  id: string,
  inspectionData: UpdateInspectionData
): Promise<APIResponse<PreTripInspection>> => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      return { error: 'No authentication token found' };
    }

    const response = await fetch(`${API_URL}/inspections/${id}/`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(inspectionData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      return {
        error: errorData.detail || errorData.message || 'Failed to update inspection',
      };
    }

    const data: PreTripInspection = await response.json();
    return { data };
  } catch (error) {
    return {
      error: error instanceof Error ? error.message : 'Failed to update inspection',
    };
  }
};

export const submitInspection = async (id: string): Promise<APIResponse<PreTripInspection>> => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      return { error: 'No authentication token found' };
    }

    const response = await fetch(`${API_URL}/inspections/${id}/submit/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      return { error: errorData.error || 'Failed to submit inspection' };
    }

    const data = await response.json();
    return { data };
  } catch (error) {
    return {
      error: error instanceof Error ? error.message : 'Failed to submit inspection',
    };
  }
};

export const approveInspection = async (id: string): Promise<APIResponse<PreTripInspection>> => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      return { error: 'No authentication token found' };
    }

    const response = await fetch(`${API_URL}/inspections/${id}/approve/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      return { error: errorData.error || 'Failed to approve inspection' };
    }

    const data = await response.json();
    return { data };
  } catch (error) {
    return {
      error: error instanceof Error ? error.message : 'Failed to approve inspection',
    };
  }
};

export const rejectInspection = async (
  id: string,
  reason: string
): Promise<APIResponse<PreTripInspection>> => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      return { error: 'No authentication token found' };
    }

    const response = await fetch(`${API_URL}/inspections/${id}/reject/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ reason }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      return { error: errorData.error || 'Failed to reject inspection' };
    }

    const data = await response.json();
    return { data };
  } catch (error) {
    return {
      error: error instanceof Error ? error.message : 'Failed to reject inspection',
    };
  }
};

export interface PrechecklistPDFResponse {
  error?: string;
  requires_approval?: boolean;
  can_approve?: boolean;
  message?: string;
}

export const downloadPrechecklistPDF = async (
  id: string, 
  inspectionId?: string,
  approveFirst?: boolean
): Promise<APIResponse<boolean> & { requires_approval?: boolean; can_approve?: boolean; message?: string }> => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      return { error: 'No authentication token found' };
    }

    const url = approveFirst 
      ? `${API_URL}/inspections/${id}/download_prechecklist_pdf/?approve=true`
      : `${API_URL}/inspections/${id}/download_prechecklist_pdf/`;
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const errorData: PrechecklistPDFResponse = await response.json().catch(() => ({}));
      return { 
        error: errorData.error || 'Failed to generate pre-checklist PDF',
        requires_approval: errorData.requires_approval,
        can_approve: errorData.can_approve,
        message: errorData.message,
      };
    }

    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = downloadUrl;
    a.download = `prechecklist-${inspectionId || id}.pdf`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(downloadUrl);
    document.body.removeChild(a);

    return { data: true };
  } catch (error) {
    return {
      error: error instanceof Error ? error.message : 'Failed to download pre-checklist PDF',
    };
  }
};

export const downloadInspectionPDF = async (id: string): Promise<APIResponse<boolean>> => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      return { error: 'No authentication token found' };
    }

    const response = await fetch(`${API_URL}/inspections/${id}/pdf/`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      return { error: 'Failed to generate PDF' };
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `inspection-${id}.pdf`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);

    return { data: true };
  } catch (error) {
    return {
      error: error instanceof Error ? error.message : 'Failed to download PDF',
    };
  }
};
