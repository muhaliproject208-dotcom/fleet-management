import { API_URL } from './index';

export interface Vehicle {
  id: string;
  vehicle_id: string;
  registration_number: string;
  vehicle_type: string;
  driver_name?: string;
  is_active: boolean;
  last_vehicle_maintenance_date?: string;
  last_full_service_date?: string;
  last_partial_service_date?: string;
  created_at?: string;
  updated_at?: string;
}

export interface CreateVehicleData {
  registration_number: string;
  vehicle_type: string;
  driver_id?: string;
  last_vehicle_maintenance_date?: string;
  last_full_service_date?: string;
  last_partial_service_date?: string;
}

export interface UpdateVehicleData extends Partial<CreateVehicleData> {
  is_active?: boolean;
}

export const getVehicles = async (params?: {
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

    const url = `${API_URL}/vehicles/${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    const response = await fetch(url, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      return { error: errorData.detail || 'Failed to fetch vehicles' };
    }

    const data = await response.json();
    return { data };
  } catch (error) {
    return { error: error instanceof Error ? error.message : 'Failed to fetch vehicles' };
  }
};

export const getVehicle = async (id: string) => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      return { error: 'No authentication token found' };
    }

    const response = await fetch(`${API_URL}/vehicles/${id}/`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      return { error: errorData.detail || 'Failed to fetch vehicle' };
    }

    const data = await response.json();
    return { data };
  } catch (error) {
    return { error: error instanceof Error ? error.message : 'Failed to fetch vehicle' };
  }
};

export const createVehicle = async (vehicleData: CreateVehicleData) => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      return { error: 'No authentication token found' };
    }

    const response = await fetch(`${API_URL}/vehicles/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(vehicleData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      return { error: errorData.detail || JSON.stringify(errorData) || 'Failed to create vehicle' };
    }

    const data = await response.json();
    return { data };
  } catch (error) {
    return { error: error instanceof Error ? error.message : 'Failed to create vehicle' };
  }
};

export const updateVehicle = async (id: string, vehicleData: UpdateVehicleData) => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      return { error: 'No authentication token found' };
    }

    const response = await fetch(`${API_URL}/vehicles/${id}/`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(vehicleData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      return { error: errorData.detail || 'Failed to update vehicle' };
    }

    const data = await response.json();
    return { data };
  } catch (error) {
    return { error: error instanceof Error ? error.message : 'Failed to update vehicle' };
  }
};

export const deleteVehicle = async (id: string) => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      return { error: 'No authentication token found' };
    }

    const response = await fetch(`${API_URL}/vehicles/${id}/`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      return { error: errorData.detail || 'Failed to delete vehicle' };
    }

    return { data: { success: true } };
  } catch (error) {
    return { error: error instanceof Error ? error.message : 'Failed to delete vehicle' };
  }
};
