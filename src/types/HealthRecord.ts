export type HealthMetricType = 'heart_rate' | 'blood_pressure' | 'weight' | 'blood_glucose' | 'temperature'

export interface HealthRecord {
  id: string
  metricType: HealthMetricType
  value: number
  secondaryValue?: number // e.g. diastolic for blood pressure
  unit: string
  date: string
  notes?: string
}

export interface MetricSummary {
  metricType: HealthMetricType
  label: string
  latestValue: string
  averageValue: string
  unit: string
  trend: 'stable' | 'improving' | 'monitoring' | 'elevated'
  trendDescription: string
}
