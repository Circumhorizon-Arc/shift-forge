import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
export const USE_MOCK_API = import.meta.env.VITE_USE_MOCK_API === 'true'

export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
})

// Attach auth token if available
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('health_sense_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Standardize error messaging
export interface AppApiError {
  message: string
  status?: number
  details?: unknown
}

export function handleApiError(error: unknown): AppApiError {
  if (axios.isAxiosError(error)) {
    const axiosErr = error as AxiosError<{ message?: string; detail?: string }>
    if (!axiosErr.response) {
      return {
        message: 'Unable to reach the Health Sense server. Please check your network connection.',
        status: 0,
      }
    }
    const serverMessage =
      axiosErr.response.data?.message ||
      axiosErr.response.data?.detail ||
      'An unexpected server error occurred. Please try again.'

    return {
      message: serverMessage,
      status: axiosErr.response.status,
      details: axiosErr.response.data,
    }
  }

  return {
    message: error instanceof Error ? error.message : 'An unexpected error occurred.',
  }
}
