export type FindingInterpretation = 'within-range' | 'outside-range' | 'unknown'

export interface ReportFinding {
  id: string
  testName: string
  value: string
  unit: string
  referenceRange?: string
  interpretation: FindingInterpretation
  flag?: 'normal' | 'low' | 'high' | 'borderline' | 'abnormal'
  category?: string
  confidenceScore?: number // e.g. OCR/extraction confidence
}
