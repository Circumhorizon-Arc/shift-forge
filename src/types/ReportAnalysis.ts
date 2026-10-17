import { ReportFinding } from './ReportFinding'

export interface ReportAnalysis {
  reportId: string
  reportName: string
  reportDate: string
  labName?: string
  status: 'analyzed' | 'processing' | 'failed'
  summary: string
  findings: ReportFinding[]
  explanations: string[]
  doctorQuestions: string[]
  disclaimer: string
  analyzedAt?: string
  extractedFactsCount?: number
}
