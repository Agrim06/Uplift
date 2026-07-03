import axios from "axios";

// 2. Standardized ApiError Class
export class ApiError extends Error {
  constructor(message, status, code, details = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;     // HTTP status code (e.g. 400, 401, 500) or null
    this.code = code;         // Standardized error code (e.g. 'TIMEOUT', 'NETWORK_ERROR', 'UNAUTHORIZED')
    this.details = details;   // Validation error details or nested structure
    
    // Ensure correct prototype chain
    Object.setPrototypeOf(this, ApiError.prototype);
  }
}

// Helpers for localStorage token management
export const getAccessToken = () => localStorage.getItem('access_token') || localStorage.getItem('token');
export const getRefreshToken = () => localStorage.getItem('refresh_token');
export const setTokens = (accessToken, refreshToken) => {
  if (accessToken) {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('token', accessToken); // Backward compatibility
  }
  if (refreshToken) localStorage.setItem('refresh_token', refreshToken);
};
export const clearTokens = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('token');
  localStorage.removeItem('refresh_token');
};

// 1. Axios Instance Configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
  timeout: 10000, // 10 seconds default timeout
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Variables to handle refreshing queue
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

// Mock function for refreshing authentication token
// In production, hook this up to POST /api/v1/auth/refresh or your authentication provider
const refreshAuthToken = async () => {
  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    throw new ApiError('No refresh token available', 401, 'UNAUTHORIZED');
  }

  // To support future backend auth, we use axios (not the 'api' instance to prevent infinite loops)
  // to fetch a new token:
  try {
    const response = await axios.post(
      `${import.meta.env.VITE_API_URL || '/api/v1'}/auth/refresh/`,
      { refresh_token: refreshToken },
      { headers: { 'Content-Type': 'application/json' } }
    );
    
    const { access_token, refresh_token } = response.data;
    setTokens(access_token, refresh_token);
    return access_token;
  } catch (err) {
    clearTokens();
    throw err;
  }
};

// 5. Request Interceptor (Future support for authentication)
api.interceptors.request.use(
  (config) => {
    const token = getAccessToken();
    if (token && !config.headers.Authorization) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(new ApiError(error.message, null, 'REQUEST_SETUP_ERROR'));
  }
);

// 4. Response Normalization & 2. Error Handling Strategy Interceptor
api.interceptors.response.use(
  (response) => {
    // Response normalization: strip wrapper and return response.data directly or nested data
    const resData = response.data;
    if (resData && typeof resData === 'object') {
      // If the backend wraps the actual resource in a 'data' field, normalize it
      if ('data' in resData && Object.keys(resData).length <= 2 && ('status' in resData || 'message' in resData)) {
        return resData.data;
      }
    }
    return resData;
  },
  async (error) => {
    const originalRequest = error.config;

    // Check if error response is 401 and request hasn't been retried yet
    const isAuthRequest = originalRequest.url.includes('/auth/');
    
    if (error.response?.status === 401 && !originalRequest._retry && !isAuthRequest) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({
            resolve: (token) => {
              originalRequest.headers.Authorization = `Bearer ${token}`;
              resolve(api(originalRequest));
            },
            reject: (err) => {
              reject(err);
            },
          });
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const newAccessToken = await refreshAuthToken();
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        processQueue(null, newAccessToken);
        return api(originalRequest);
      } catch (refreshErr) {
        processQueue(refreshErr, null);
        if (typeof window !== 'undefined') {
          window.dispatchEvent(new CustomEvent('auth:unauthorized'));
        }
        return Promise.reject(
          new ApiError(
            'Session expired. Please log in again.',
            401,
            'UNAUTHORIZED',
            refreshErr.response?.data
          )
        );
      } finally {
        isRefreshing = false;
      }
    }

    // 2. Error Handling Strategy: Parse errors into ApiError instances
    if (error.response) {
      const status = error.response.status;
      const data = error.response.data;
      const serverMessage = data?.message || data?.detail || error.response.statusText || 'An error occurred';
      
      let errorCode = 'BAD_REQUEST';
      if (status === 401) errorCode = 'UNAUTHORIZED';
      else if (status === 403) errorCode = 'FORBIDDEN';
      else if (status === 404) errorCode = 'NOT_FOUND';
      else if (status === 408) errorCode = 'TIMEOUT';
      else if (status >= 500) errorCode = 'SERVER_ERROR';

      const details = data?.errors || data?.details || null;

      return Promise.reject(new ApiError(serverMessage, status, errorCode, details));
    } else if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      return Promise.reject(
        new ApiError(
          'Request timed out. Please check your network connection and try again.',
          408,
          'TIMEOUT'
        )
      );
    } else if (error.request) {
      return Promise.reject(
        new ApiError(
          'No response from server. Please check your internet connection.',
          null,
          'NETWORK_ERROR'
        )
      );
    } else {
      return Promise.reject(new ApiError(error.message, null, 'REQUEST_SETUP_ERROR'));
    }
  }
);

export default api;