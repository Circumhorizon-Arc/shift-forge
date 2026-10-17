import { HealthRecord, MetricSummary, HealthMetricType } from '../../types'

export const initialMockHealthRecords: HealthRecord[] = [
  // Heart Rate (bpm)
  { id: 'hr-1', metricType: 'heart_rate', value: 72, unit: 'bpm', date: '2026-10-10', notes: 'Resting pulse upon waking' },
  { id: 'hr-2', metricType: 'heart_rate', value: 75, unit: 'bpm', date: '2026-10-11', notes: 'Post light walk' },
  { id: 'hr-3', metricType: 'heart_rate', value: 70, unit: 'bpm', date: '2026-10-12', notes: 'Midday rest' },
  { id: 'hr-4', metricType: 'heart_rate', value: 74, unit: 'bpm', date: '2026-10-13', notes: 'Evening check' },
  { id: 'hr-5', metricType: 'heart_rate', value: 71, unit: 'bpm', date: '2026-10-14', notes: 'Morning rest' },
  { id: 'hr-6', metricType: 'heart_rate', value: 73, unit: 'bpm', date: '2026-10-15', notes: 'Regular check' },
  { id: 'hr-7', metricType: 'heart_rate', value: 74, unit: 'bpm', date: '2026-10-16', notes: 'Resting heart rate' },

  // Blood Pressure (mmHg) - systolic stored in value, diastolic in secondaryValue
  { id: 'bp-1', metricType: 'blood_pressure', value: 122, secondaryValue: 80, unit: 'mmHg', date: '2026-10-10', notes: 'Morning sitting' },
  { id: 'bp-2', metricType: 'blood_pressure', value: 120, secondaryValue: 78, unit: 'mmHg', date: '2026-10-12', notes: 'Home cuff measurement' },
  { id: 'bp-3', metricType: 'blood_pressure', value: 118, secondaryValue: 79, unit: 'mmHg', date: '2026-10-14', notes: 'Post relaxed breathing' },
  { id: 'bp-4', metricType: 'blood_pressure', value: 121, secondaryValue: 81, unit: 'mmHg', date: '2026-10-16', notes: 'Routine check' },

  // Blood Glucose (mg/dL)
  { id: 'bg-1', metricType: 'blood_glucose', value: 104, unit: 'mg/dL', date: '2026-10-10', notes: 'Fasting 10 hours' },
  { id: 'bg-2', metricType: 'blood_glucose', value: 108, unit: 'mg/dL', date: '2026-10-12', notes: 'Fasting morning' },
  { id: 'bg-3', metricType: 'blood_glucose', value: 102, unit: 'mg/dL', date: '2026-10-14', notes: 'Fasting morning' },
  { id: 'bg-4', metricType: 'blood_glucose', value: 106, unit: 'mg/dL', date: '2026-10-16', notes: 'Fasting morning' },

  // Weight (lbs or kg)
  { id: 'wt-1', metricType: 'weight', value: 168.4, unit: 'lbs', date: '2026-10-01', notes: 'Weekly weigh-in' },
  { id: 'wt-2', metricType: 'weight', value: 167.8, unit: 'lbs', date: '2026-10-08', notes: 'Weekly weigh-in' },
  { id: 'wt-3', metricType: 'weight', value: 167.2, unit: 'lbs', date: '2026-10-15', notes: 'Weekly weigh-in' },

  // Temperature (°F)
  { id: 'temp-1', metricType: 'temperature', value: 98.4, unit: '°F', date: '2026-10-12', notes: 'Oral digital thermometer' },
  { id: 'temp-2', metricType: 'temperature', value: 98.6, unit: '°F', date: '2026-10-14', notes: 'Normal afternoon' },
  { id: 'temp-3', metricType: 'temperature', value: 98.5, unit: '°F', date: '2026-10-16', notes: 'Normal resting' },
]

export const metricDefinitions: Record<HealthMetricType, { label: string; unit: string; description: string }> = {
  heart_rate: {
    label: 'Heart Rate',
    unit: 'bpm',
    description: 'Resting pulse rate tracked over time.',
  },
  blood_pressure: {
    label: 'Blood Pressure',
    unit: 'mmHg',
    description: 'Systolic and diastolic pressures (e.g. 120/80 mmHg).',
  },
  blood_glucose: {
    label: 'Blood Glucose',
    unit: 'mg/dL',
    description: 'Fasting capillary or serum glucose measurements.',
  },
  weight: {
    label: 'Weight',
    unit: 'lbs',
    description: 'Body mass measurements recorded regularly.',
  },
  temperature: {
    label: 'Body Temperature',
    unit: '°F',
    description: 'Oral or tympanic body temperature records.',
  },
}

export function computeMetricSummary(records: HealthRecord[], metricType: HealthMetricType): MetricSummary {
  const filtered = records
    .filter((r) => r.metricType === metricType)
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())

  const def = metricDefinitions[metricType]

  if (filtered.length === 0) {
    return {
      metricType,
      label: def.label,
      latestValue: '—',
      averageValue: '—',
      unit: def.unit,
      trend: 'stable',
      trendDescription: 'No records available yet',
    }
  }

  const latest = filtered[filtered.length - 1]
  const sum = filtered.reduce((acc, curr) => acc + curr.value, 0)
  const avg = (sum / filtered.length).toFixed(1)

  let latestStr = `${latest.value}`
  if (latest.secondaryValue) {
    latestStr = `${latest.value}/${latest.secondaryValue}`
  }

  return {
    metricType,
    label: def.label,
    latestValue: `${latestStr} ${def.unit}`,
    averageValue: `${avg} ${def.unit}`,
    unit: def.unit,
    trend: 'stable',
    trendDescription: 'Consistently within expected personal baseline',
  }
}
