import { apiClient, USE_MOCK_API, handleApiError } from './api'
import { Reminder } from '../types'
import { initialMockReminders } from '../data/mock/mockReminders'

const STORAGE_REMINDERS_KEY = 'health_sense_reminders'

function getStoredReminders(): Reminder[] {
  const data = localStorage.getItem(STORAGE_REMINDERS_KEY)
  if (!data) {
    localStorage.setItem(STORAGE_REMINDERS_KEY, JSON.stringify(initialMockReminders))
    return initialMockReminders
  }
  try {
    return JSON.parse(data)
  } catch {
    return initialMockReminders
  }
}

export const reminderService = {
  async getReminders(): Promise<Reminder[]> {
    if (USE_MOCK_API) {
      await new Promise((res) => setTimeout(res, 250))
      return getStoredReminders()
    }

    try {
      const response = await apiClient.get<Reminder[]>('/reminders')
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  },

  async createReminder(reminderData: Omit<Reminder, 'id'>): Promise<Reminder> {
    if (USE_MOCK_API) {
      await new Promise((res) => setTimeout(res, 300))
      const newReminder: Reminder = {
        ...reminderData,
        id: 'rem-' + Date.now().toString().slice(-6),
        createdAt: new Date().toISOString(),
      }
      const existing = getStoredReminders()
      const updated = [newReminder, ...existing]
      localStorage.setItem(STORAGE_REMINDERS_KEY, JSON.stringify(updated))
      return newReminder
    }

    try {
      const response = await apiClient.post<Reminder>('/reminders', reminderData)
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  },

  async completeReminder(id: string, completed: boolean = true): Promise<Reminder> {
    if (USE_MOCK_API) {
      await new Promise((res) => setTimeout(res, 200))
      const existing = getStoredReminders()
      let updatedReminder: Reminder | null = null
      const updated = existing.map((r) => {
        if (r.id === id) {
          updatedReminder = { ...r, completed }
          return updatedReminder
        }
        return r
      })
      localStorage.setItem(STORAGE_REMINDERS_KEY, JSON.stringify(updated))
      if (!updatedReminder) throw new Error('Reminder not found')
      return updatedReminder
    }

    try {
      const response = await apiClient.patch<Reminder>(`/reminders/${id}/complete`, { completed })
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  },

  async deleteReminder(id: string): Promise<boolean> {
    if (USE_MOCK_API) {
      await new Promise((res) => setTimeout(res, 200))
      const existing = getStoredReminders()
      const updated = existing.filter((r) => r.id !== id)
      localStorage.setItem(STORAGE_REMINDERS_KEY, JSON.stringify(updated))
      return true
    }

    try {
      await apiClient.delete(`/reminders/${id}`)
      return true
    } catch (error) {
      throw handleApiError(error)
    }
  },
}
