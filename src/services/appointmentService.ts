import { apiClient, USE_MOCK_API, handleApiError } from './api'
import { Appointment } from '../types'
import { initialMockAppointments } from '../data/mock/mockAppointments'

const STORAGE_APPOINTMENTS_KEY = 'health_sense_appointments'

function getStoredAppointments(): Appointment[] {
  const data = localStorage.getItem(STORAGE_APPOINTMENTS_KEY)
  if (!data) {
    localStorage.setItem(STORAGE_APPOINTMENTS_KEY, JSON.stringify(initialMockAppointments))
    return initialMockAppointments
  }
  try {
    return JSON.parse(data)
  } catch {
    return initialMockAppointments
  }
}

export const appointmentService = {
  async getAppointments(): Promise<Appointment[]> {
    if (USE_MOCK_API) {
      await new Promise((res) => setTimeout(res, 300))
      return getStoredAppointments()
    }

    try {
      const response = await apiClient.get<Appointment[]>('/appointments')
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  },

  async createAppointment(appointmentData: Omit<Appointment, 'id'>): Promise<Appointment> {
    if (USE_MOCK_API) {
      await new Promise((res) => setTimeout(res, 450))
      const newAppointment: Appointment = {
        ...appointmentData,
        id: 'apt-' + Date.now().toString().slice(-6),
      }
      const existing = getStoredAppointments()
      const updated = [newAppointment, ...existing]
      localStorage.setItem(STORAGE_APPOINTMENTS_KEY, JSON.stringify(updated))
      return newAppointment
    }

    try {
      const response = await apiClient.post<Appointment>('/appointments', appointmentData)
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  },

  async cancelAppointment(id: string): Promise<boolean> {
    if (USE_MOCK_API) {
      await new Promise((res) => setTimeout(res, 250))
      const existing = getStoredAppointments()
      const updated = existing.map((a) => (a.id === id ? { ...a, status: 'cancelled' as const } : a))
      localStorage.setItem(STORAGE_APPOINTMENTS_KEY, JSON.stringify(updated))
      return true
    }

    try {
      await apiClient.patch(`/appointments/${id}/cancel`)
      return true
    } catch (error) {
      throw handleApiError(error)
    }
  },
}
