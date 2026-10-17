import { apiClient, USE_MOCK_API, handleApiError } from './api'
import { MedicalReport, ReportAnalysis } from '../types'
import { initialMockReports } from '../data/mock/mockReports'
import { mockReportAnalyses } from '../data/mock/mockAnalyses'

const STORAGE_REPORTS_KEY = 'health_sense_reports'
const STORAGE_ANALYSES_KEY = 'health_sense_analyses'

function getStoredReports(): MedicalReport[] {
  const data = localStorage.getItem(STORAGE_REPORTS_KEY)
  if (!data) {
    localStorage.setItem(STORAGE_REPORTS_KEY, JSON.stringify(initialMockReports))
    return initialMockReports
  }
  try {
    return JSON.parse(data)
  } catch {
    return initialMockReports
  }
}

function getStoredAnalyses(): Record<string, ReportAnalysis> {
  const data = localStorage.getItem(STORAGE_ANALYSES_KEY)
  if (!data) {
    localStorage.setItem(STORAGE_ANALYSES_KEY, JSON.stringify(mockReportAnalyses))
    return mockReportAnalyses
  }
  try {
    return JSON.parse(data)
  } catch {
    return mockReportAnalyses
  }
}

export const reportService = {
  async getReports(): Promise<MedicalReport[]> {
    if (USE_MOCK_API) {
      await new Promise((res) => setTimeout(res, 450))
      return getStoredReports()
    }

    try {
      const response = await apiClient.get<MedicalReport[]>('/reports')
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  },

  async getReportById(id: string): Promise<MedicalReport | null> {
    if (USE_MOCK_API) {
      await new Promise((res) => setTimeout(res, 250))
      const reports = getStoredReports()
      return reports.find((r) => r.id === id) || null
    }

    try {
      const response = await apiClient.get<MedicalReport>(`/reports/${id}`)
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  },

  async uploadReport(
    file: File,
    onProgress?: (percent: number) => void
  ): Promise<{ report: MedicalReport; analysis: ReportAnalysis }> {
    if (USE_MOCK_API) {
      // Simulate realistic upload progress
      if (onProgress) {
        for (let p = 15; p <= 95; p += 20) {
          onProgress(p)
          await new Promise((r) => setTimeout(r, 120))
        }
        onProgress(100)
      }

      await new Promise((r) => setTimeout(r, 400)) // processing simulation

      const newId = 'rep-' + Date.now().toString().slice(-6)
      const dateStr = new Date().toISOString().split('T')[0]
      const sizeStr = (file.size / (1024 * 1024)).toFixed(1) + ' MB'

      const newReport: MedicalReport = {
        id: newId,
        name: file.name.replace(/\.[^/.]+$/, '').replace(/[-_]/g, ' ') || 'Diagnostic Health Report',
        type: 'Clinical Diagnostic Report',
        uploadedAt: dateStr,
        fileSize: sizeStr,
        fileType: file.type || 'application/pdf',
        status: 'analyzed',
        doctorOrLab: 'Laboratory Diagnostics Services',
        findingsCount: 5,
        summaryPreview: 'Extracted key biochemical and hematology metrics. 4 values within range, 1 value flagged for professional doctor discussion.',
      }

      const newAnalysis: ReportAnalysis = {
        reportId: newId,
        reportName: newReport.name,
        reportDate: new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }),
        labName: 'Central Clinical Health Laboratory',
        status: 'analyzed',
        analyzedAt: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        extractedFactsCount: 5,
        summary:
          'This uploaded document was parsed for common diagnostic markers. 4 measured values align with laboratory reference boundaries, while 1 parameter (Serum Ferritin) is outside the laboratory’s stated reference range.',
        findings: [
          {
            id: 'nf-1',
            testName: 'Hemoglobin',
            value: '13.9',
            unit: 'g/dL',
            referenceRange: '12.0 – 16.0 g/dL',
            interpretation: 'within-range',
            flag: 'normal',
            category: 'Hematology',
            confidenceScore: 0.98,
          },
          {
            id: 'nf-2',
            testName: 'Serum Ferritin',
            value: '18',
            unit: 'ng/mL',
            referenceRange: '24 – 336 ng/mL',
            interpretation: 'outside-range',
            flag: 'low',
            category: 'Iron Stores',
            confidenceScore: 0.97,
          },
          {
            id: 'nf-3',
            testName: 'Total Iron Binding Capacity (TIBC)',
            value: '340',
            unit: 'µg/dL',
            referenceRange: '250 – 450 µg/dL',
            interpretation: 'within-range',
            flag: 'normal',
            category: 'Iron Stores',
            confidenceScore: 0.95,
          },
          {
            id: 'nf-4',
            testName: 'White Blood Cell Count',
            value: '5.9',
            unit: 'x10³/µL',
            referenceRange: '4.5 – 11.0 x10³/µL',
            interpretation: 'within-range',
            flag: 'normal',
            category: 'Hematology',
            confidenceScore: 0.99,
          },
          {
            id: 'nf-5',
            testName: 'Platelets',
            value: '228',
            unit: 'x10³/µL',
            referenceRange: '150 – 450 x10³/µL',
            interpretation: 'within-range',
            flag: 'normal',
            category: 'Hematology',
            confidenceScore: 0.96,
          },
        ],
        explanations: [
          'Serum Ferritin indicates stored iron reserves in tissue cells. A measured value of 18 ng/mL sits below this laboratory’s 24 ng/mL cutoff.',
          'Hemoglobin remains within standard bounds (13.9 g/dL), indicating normal circulating red cell oxygen capacity at this current time.',
          'Results can be influenced by diet, recent physical training, blood donation, or mild digestive factors. Discuss these findings with your physician.',
        ],
        doctorQuestions: [
          'Does this ferritin reading suggest an evaluation of my dietary iron intake or gastrointestinal absorption?',
          'Is any dietary adjustment or supplement warranted, or should we monitor again in 3 months?',
          'Are there any symptoms I should pay attention to before our next checkup?',
        ],
        disclaimer:
          'Health Sense provides educational explanations of uploaded health information. It does not diagnose medical conditions or replace professional medical advice. Please discuss your results with a qualified healthcare professional.',
      }

      // Store in mock persistence
      const currentReports = getStoredReports()
      localStorage.setItem(STORAGE_REPORTS_KEY, JSON.stringify([newReport, ...currentReports]))

      const currentAnalyses = getStoredAnalyses()
      currentAnalyses[newId] = newAnalysis
      localStorage.setItem(STORAGE_ANALYSES_KEY, JSON.stringify(currentAnalyses))

      return { report: newReport, analysis: newAnalysis }
    }

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await apiClient.post<{ report: MedicalReport; analysis: ReportAnalysis }>(
        '/reports/upload',
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' },
          onUploadProgress: (evt) => {
            if (evt.total && onProgress) {
              const percent = Math.round((evt.loaded * 100) / evt.total)
              onProgress(percent)
            }
          },
        }
      )
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  },

  async getReportAnalysis(reportId: string): Promise<ReportAnalysis | null> {
    if (USE_MOCK_API) {
      await new Promise((res) => setTimeout(res, 350))
      const analyses = getStoredAnalyses()
      return analyses[reportId] || mockReportAnalyses['rep-001'] || null
    }

    try {
      const response = await apiClient.get<ReportAnalysis>(`/reports/${reportId}/analysis`)
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  },

  async deleteReport(id: string): Promise<boolean> {
    if (USE_MOCK_API) {
      await new Promise((res) => setTimeout(res, 300))
      const reports = getStoredReports().filter((r) => r.id !== id)
      localStorage.setItem(STORAGE_REPORTS_KEY, JSON.stringify(reports))
      return true
    }

    try {
      await apiClient.delete(`/reports/${id}`)
      return true
    } catch (error) {
      throw handleApiError(error)
    }
  },
}
