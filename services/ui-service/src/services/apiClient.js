import axios from 'axios';

// Use environment variable for API URL, fallback to localhost for development
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout
});

// Add request interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error status
      console.error('API Error:', error.response.status, error.response.data);
      return Promise.reject(error);
    } else if (error.request) {
      // Request made but no response received
      console.error('Network Error: No response from server');
      return Promise.reject(new Error('Network error: Unable to reach the server'));
    } else {
      // Something else happened
      console.error('Error:', error.message);
      return Promise.reject(error);
    }
  }
);

export const getTopDevices = async () => {
  try {
    const response = await apiClient.get('/analytics/top-devices');
    return response.data;
  } catch (error) {
    console.error('Error fetching top devices:', error);
    throw error;
  }
};

export const getWeakDevices = async () => {
  try {
    const response = await apiClient.get('/analytics/weak-devices');
    return response.data;
  } catch (error) {
    console.error('Error fetching weak devices:', error);
    throw error;
  }
};

export const getGatewayStats = async () => {
  try {
    const response = await apiClient.get('/analytics/gateway-stats');
    return response.data;
  } catch (error) {
    console.error('Error fetching gateway stats:', error);
    throw error;
  }
};

export const getDuplicateDevices = async () => {
  try {
    const response = await apiClient.get('/analytics/duplicates');
    return response.data;
  } catch (error) {
    console.error('Error fetching duplicate devices:', error);
    throw error;
  }
};

export const getHighTemperatureAlerts = async () => {
  try {
    const response = await apiClient.get('/analytics/high-temperature');
    return response.data;
  } catch (error) {
    console.error('Error fetching high temperature alerts:', error);
    throw error;
  }
};
