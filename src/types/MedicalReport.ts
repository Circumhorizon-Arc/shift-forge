export type ReportStatus = 'uploaded' | 'processing' | 'analyzed' | 'failed'

export interface MedicalReport {
  id: string
  name: string
  type: string
  uploadedAt: string
  fileSize?: string
  fileType?: string
  status: ReportStatus
  doctorOrLab?: string
  findingsCount?: number
  summaryPreview?: string
}
