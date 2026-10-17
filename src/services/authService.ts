import { apiClient, USE_MOCK_API, handleApiError } from './api'
import { User, AuthResponse } from '../types'

const MOCK_STORAGE_KEY = 'health_sense_user'
const TOKEN_KEY = 'health_sense_token'

const defaultMockUser: User = {
  id: 'usr-101',
  fullName: 'Alex Morgan',
  email: 'alex.morgan@healthsense.dev',
  dateOfBirth: '1992-05-14',
  phone: '+1 (555) 234-5678',
  avatarUrl: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=256&q=80',
  createdAt: '2026-01-10',
}

export const authService = {
  async login(email: string, _password: string): Promise<AuthResponse> {
    if (USE_MOCK_API) {
      await new Promise((res) => setTimeout(res, 600)) // simulated network delay
      const existing = localStorage.getItem(MOCK_STORAGE_KEY)
      const user: User = existing ? JSON.parse(existing) : { ...defaultMockUser, email }
      const token = 'mock-jwt-token-' + Date.now()
      localStorage.setItem(MOCK_STORAGE_KEY, JSON.stringify(user))
      localStorage.setItem(TOKEN_KEY, token)
      return { user, token }
    }

    try {
      const response = await apiClient.post<any>('/auth/login', { email, password: _password })
      const token = response.data.token || response.data.access_token
      const rawUser = response.data.user || response.data
      const user: User = {
        id: String(rawUser.id || rawUser.user_id || 'usr-1'),
        fullName: rawUser.fullName || rawUser.full_name || 'HealthSense User',
        email: rawUser.email || email,
        dateOfBirth: rawUser.dateOfBirth || rawUser.date_of_birth || '',
        phone: rawUser.phone || '',
        createdAt: rawUser.createdAt || rawUser.created_at || new Date().toISOString(),
      }
      if (token) localStorage.setItem(TOKEN_KEY, token)
      localStorage.setItem(MOCK_STORAGE_KEY, JSON.stringify(user))
      return { user, token }
    } catch (error) {
      throw handleApiError(error)
    }
  },

  async register(fullName: string, email: string, _password: string, dateOfBirth?: string): Promise<AuthResponse> {
    if (USE_MOCK_API) {
      await new Promise((res) => setTimeout(res, 700))
      const user: User = {
        id: 'usr-' + Math.floor(Math.random() * 10000),
        fullName,
        email,
        dateOfBirth: dateOfBirth || '1995-01-01',
        createdAt: new Date().toISOString(),
      }
      const token = 'mock-jwt-token-' + Date.now()
      localStorage.setItem(MOCK_STORAGE_KEY, JSON.stringify(user))
      localStorage.setItem(TOKEN_KEY, token)
      return { user, token }
    }

    try {
      const response = await apiClient.post<any>('/auth/register', {
        fullName,
        email,
        password: _password,
        dateOfBirth,
      })
      const token = response.data.token || response.data.access_token
      const rawUser = response.data.user || response.data
      const user: User = {
        id: String(rawUser.id || rawUser.user_id || 'usr-1'),
        fullName: rawUser.fullName || rawUser.full_name || fullName,
        email: rawUser.email || email,
        dateOfBirth: rawUser.dateOfBirth || rawUser.date_of_birth || dateOfBirth || '',
        phone: rawUser.phone || '',
        createdAt: rawUser.createdAt || rawUser.created_at || new Date().toISOString(),
      }
      if (token) localStorage.setItem(TOKEN_KEY, token)
      localStorage.setItem(MOCK_STORAGE_KEY, JSON.stringify(user))
      return { user, token }
    } catch (error) {
      throw handleApiError(error)
    }
  },

  async getCurrentUser(): Promise<User | null> {
    const token = localStorage.getItem(TOKEN_KEY)
    if (!token) return null

    if (USE_MOCK_API) {
      const stored = localStorage.getItem(MOCK_STORAGE_KEY)
      return stored ? JSON.parse(stored) : defaultMockUser
    }

    try {
      const response = await apiClient.get<any>('/auth/me')
      const rawUser = response.data.user || response.data
      const user: User = {
        id: String(rawUser.id || rawUser.user_id || 'usr-1'),
        fullName: rawUser.fullName || rawUser.full_name || 'HealthSense User',
        email: rawUser.email || '',
        dateOfBirth: rawUser.dateOfBirth || rawUser.date_of_birth || '',
        phone: rawUser.phone || '',
        createdAt: rawUser.createdAt || rawUser.created_at || '',
      }
      localStorage.setItem(MOCK_STORAGE_KEY, JSON.stringify(user))
      return user
    } catch {
      return null
    }
  },

  async updateProfile(updates: Partial<User>): Promise<User> {
    if (USE_MOCK_API) {
      await new Promise((res) => setTimeout(res, 400))
      const current = await this.getCurrentUser()
      const updated: User = { ...(current || defaultMockUser), ...updates }
      localStorage.setItem(MOCK_STORAGE_KEY, JSON.stringify(updated))
      return updated
    }

    try {
      const response = await apiClient.put<any>('/auth/profile', updates)
      const rawUser = response.data.user || response.data
      const user: User = {
        id: String(rawUser.id || rawUser.user_id || 'usr-1'),
        fullName: rawUser.fullName || rawUser.full_name || '',
        email: rawUser.email || '',
        dateOfBirth: rawUser.dateOfBirth || rawUser.date_of_birth || '',
        phone: rawUser.phone || '',
        createdAt: rawUser.createdAt || rawUser.created_at || '',
      }
      localStorage.setItem(MOCK_STORAGE_KEY, JSON.stringify(user))
      return user
    } catch (error) {
      throw handleApiError(error)
    }
  },

  logout(): void {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(MOCK_STORAGE_KEY)
  },
}
