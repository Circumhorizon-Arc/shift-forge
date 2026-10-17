import { apiClient, USE_MOCK_API, handleApiError } from './api'
import { HealthRecord, HealthMetricType, MetricSummary } from '../types'
import { initialMockHealthRecords, computeMetricSummary } from '../data/mock/mockHealthRecords'

const STORAGE_HEALTH_KEY = 'health_sense_records'

function getStoredHealthRecords(): HealthRecord[] {
  const data = localStorage.getItem(STORAGE_HEALTH_KEY)
  if (!data) {
    localStorage.setItem(STORAGE_HEALTH_KEY, JSON.stringify(initialMockHealthRecords))
    return initialMockHealthRecords
  }
  try {
    return JSON.parse(data)
  } catch {
    return initialMockHealthRecords
  }
}

export const healthService = {
  async getHealthRecords(metricType?: HealthMetricType): Promise<HealthRecord[]> {
    if (USE_MOCK_API) {
      await new Promise((res) => setTimeout(res, 350))
      const all = getStoredHealthRecords()
      if (metricType) {
        return all.filter((r) => r.metricType === metricType)
      }
      return all
    }

    try {
      const response = await apiClient.get<HealthRecord[]>('/health/records', {
        params: metricType ? { metricType } : undefined,
      })
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  },

  async createHealthRecord(recordData: Omit<HealthRecord, 'id'>): Promise<HealthRecord> {
    if (USE_MOCK_API) {
      await new Promise((res) => setTimeout(res, 400))
      const newRecord: HealthRecord = {
        ...recordData,
        id: 'rec-' + Date.now().toString().slice(-6),
      }
      const existing = getStoredHealthRecords()
      const updated = [newRecord, ...existing]
      localStorage.setItem(STORAGE_HEALTH_KEY, JSON.stringify(updated))
      return newRecord
    }

    try {
      const response = await apiClient.post<HealthRecord>('/health/records', recordData)
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  },

  async deleteHealthRecord(id: string): Promise<boolean> {
    if (USE_MOCK_API) {
      await new Promise((res) => setTimeout(res, 250))
      const existing = getStoredHealthRecords()
      const updated = existing.filter((r) => r.id !== id)
      localStorage.setItem(STORAGE_HEALTH_KEY, JSON.stringify(updated))
      return true
    }

    try {
      await apiClient.delete(`/health/records/${id}`)
      return true
    } catch (error) {
      throw handleApiError(error)
    }
  },

  async getMetricSummary(metricType: HealthMetricType): Promise<MetricSummary> {
    if (USE_MOCK_API) {
      await new Promise((res) => setTimeout(res, 200))
      const records = getStoredHealthRecords()
      return computeMetricSummary(records, metricType)
    }

    try {
      const response = await apiClient.get<MetricSummary>(`/health/summary/${metricType}`)
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  },
}
