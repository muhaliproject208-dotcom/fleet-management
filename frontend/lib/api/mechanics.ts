import { API_URL } from './index';

export type CertificationStatus = 'certified' | 'not_certified';

export interface Mechanic {
  id: string;
  mechanic_id: string;
  full_name: string;
  specialization: string;
  phone_number: string;
  is_active: boolean;
  certification_status?: CertificationStatus;
  created_at?: string;
  updated_at?: string;
}

export interface CreateMechanicData {
  full_name: string;
  specialization: string;
  phone_number: string;
  certification_status?: CertificationStatus;
}

export interface UpdateMechanicData extends Partial<CreateMechanicData> {
  is_active?: boolean;
}

export const getMechanics = async (params?: {
  is_active?: boolean | 'all';
  page?: number;
  page_size?: number;
  search?: string;
}) => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      return { error: 'No authentication token found' };
    }

    const queryParams = new URLSearchParams();
    if (params?.is_active !== undefined) {
      queryParams.append('is_active', params.is_active.toString());
    }
    if (params?.page) {
      queryParams.append('page', params.page.toString());
    }
    if (params?.page_size) {
      queryParams.append('page_size', params.page_size.toString());
    }
    if (params?.search) {
      queryParams.append('search', params.search);
    }

    const url = `${API_URL}/mechanics/${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    const response = await fetch(url, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      return { error: errorData.detail || 'Failed to fetch mechanics' };
    }

    const data = await response.json();
    return { data };
  } catch (error) {
    return { error: error instanceof Error ? error.message : 'Failed to fetch mechanics' };
  }
};

export const getMechanic = async (id: string) => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      return { error: 'No authentication token found' };
    }

    const response = await fetch(`${API_URL}/mechanics/${id}/`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      return { error: errorData.detail || 'Failed to fetch mechanic' };
    }

    const data = await response.json();
    return { data };
  } catch (error) {
    return { error: error instanceof Error ? error.message : 'Failed to fetch mechanic' };
  }
};

export const createMechanic = async (mechanicData: CreateMechanicData) => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      return { error: 'No authentication token found' };
    }

    const response = await fetch(`${API_URL}/mechanics/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(mechanicData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      return { error: errorData.detail || JSON.stringify(errorData) || 'Failed to create mechanic' };
    }

    const data = await response.json();
    return { data };
  } catch (error) {
    return { error: error instanceof Error ? error.message : 'Failed to create mechanic' };
  }
};

export const updateMechanic = async (id: string, mechanicData: UpdateMechanicData) => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      return { error: 'No authentication token found' };
    }

    const response = await fetch(`${API_URL}/mechanics/${id}/`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(mechanicData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      return { error: errorData.detail || 'Failed to update mechanic' };
    }

    const data = await response.json();
    return { data };
  } catch (error) {
    return { error: error instanceof Error ? error.message : 'Failed to update mechanic' };
  }
};

export const deleteMechanic = async (id: string) => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      return { error: 'No authentication token found' };
    }

    const response = await fetch(`${API_URL}/mechanics/${id}/`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      return { error: errorData.detail || 'Failed to delete mechanic' };
    }

    return { data: { success: true } };
  } catch (error) {
    return { error: error instanceof Error ? error.message : 'Failed to delete mechanic' };
  }
};
