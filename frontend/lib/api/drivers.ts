import { API_URL } from './index';

export interface Driver {
  id: string;
  driver_id: string;
  full_name: string;
  license_number: string;
  phone_number: string;
  email?: string;
  is_active: boolean;
  average_risk_score?: number | null;
  risk_level?: string;
  created_at?: string;
  updated_at?: string;
}

export interface CreateDriverData {
  full_name: string;
  license_number: string;
  phone_number: string;
  email?: string;
}

export interface UpdateDriverData extends Partial<CreateDriverData> {
  is_active?: boolean;
}

export const getDrivers = async (params?: {
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

    const url = `${API_URL}/drivers/${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    const response = await fetch(url, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      return { error: errorData.detail || 'Failed to fetch drivers' };
    }

    const data = await response.json();
    return { data };
  } catch (error) {
    return { error: error instanceof Error ? error.message : 'Failed to fetch drivers' };
  }
};

export const getDriver = async (id: string) => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      return { error: 'No authentication token found' };
    }

    const response = await fetch(`${API_URL}/drivers/${id}/`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      return { error: errorData.detail || 'Failed to fetch driver' };
    }

    const data = await response.json();
    return { data };
  } catch (error) {
    return { error: error instanceof Error ? error.message : 'Failed to fetch driver' };
  }
};

export const createDriver = async (driverData: CreateDriverData) => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      return { error: 'No authentication token found' };
    }

    const response = await fetch(`${API_URL}/drivers/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(driverData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      return { error: errorData.detail || JSON.stringify(errorData) || 'Failed to create driver' };
    }

    const data = await response.json();
    return { data };
  } catch (error) {
    return { error: error instanceof Error ? error.message : 'Failed to create driver' };
  }
};

export const updateDriver = async (id: string, driverData: UpdateDriverData) => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      return { error: 'No authentication token found' };
    }

    const response = await fetch(`${API_URL}/drivers/${id}/`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(driverData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      return { error: errorData.detail || 'Failed to update driver' };
    }

    const data = await response.json();
    return { data };
  } catch (error) {
    return { error: error instanceof Error ? error.message : 'Failed to update driver' };
  }
};

export const deleteDriver = async (id: string) => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      return { error: 'No authentication token found' };
    }

    const response = await fetch(`${API_URL}/drivers/${id}/`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      return { error: errorData.detail || 'Failed to delete driver' };
    }

    return { data: { success: true } };
  } catch (error) {
    return { error: error instanceof Error ? error.message : 'Failed to delete driver' };
  }
};
