import React, { useState } from 'react'
import { Modal } from '../ui/Modal'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import { Select } from '../ui/Select'
import { HealthMetricType, HealthRecord } from '../../types'
import { metricDefinitions } from '../../data/mock/mockHealthRecords'
import { healthService } from '../../services/healthService'
import { useToast } from '../../context/ToastContext'

interface HealthRecordFormModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: (record: HealthRecord) => void
  defaultMetric?: HealthMetricType
}

export const HealthRecordFormModal: React.FC<HealthRecordFormModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  defaultMetric = 'heart_rate',
}) => {
  const [metricType, setMetricType] = useState<HealthMetricType>(defaultMetric)
  const [value, setValue] = useState('')
  const [secondaryValue, setSecondaryValue] = useState('')
  const [date, setDate] = useState(new Date().toISOString().split('T')[0])
  const [notes, setNotes] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [errors, setErrors] = useState<{ value?: string; secondaryValue?: string }>({})

  const { success, error: toastError } = useToast()

  const metricOptions = [
    { value: 'heart_rate', label: 'Heart Rate (bpm)' },
    { value: 'blood_pressure', label: 'Blood Pressure (mmHg)' },
    { value: 'blood_glucose', label: 'Blood Glucose (mg/dL)' },
    { value: 'weight', label: 'Weight (lbs)' },
    { value: 'temperature', label: 'Temperature (°F)' },
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const errs: { value?: string; secondaryValue?: string } = {}

    const numVal = parseFloat(value)
    if (isNaN(numVal) || numVal <= 0) {
      errs.value = 'Please enter a valid numeric measurement'
    }

    if (metricType === 'blood_pressure') {
      const secVal = parseFloat(secondaryValue)
      if (isNaN(secVal) || secVal <= 0) {
        errs.secondaryValue = 'Please enter diastolic pressure'
      }
    }

    if (Object.keys(errs).length > 0) {
      setErrors(errs)
      return
    }

    setIsSubmitting(true)
    setErrors({})

    try {
      const def = metricDefinitions[metricType]
      const newRecord = await healthService.createHealthRecord({
        metricType,
        value: numVal,
        secondaryValue: metricType === 'blood_pressure' ? parseFloat(secondaryValue) : undefined,
        unit: def.unit,
        date,
        notes: notes.trim() || undefined,
      })

      success(`${def.label} record logged successfully.`)
      onSuccess(newRecord)
      onClose()
      setValue('')
      setSecondaryValue('')
      setNotes('')
    } catch {
      toastError('Failed to record health measurement.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Add Health Measurement"
      description="Record a biomarker or vital sign to track your personal trend line."
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <Select
          label="Measurement Type"
          value={metricType}
          onChange={(e) => setMetricType(e.target.value as HealthMetricType)}
          options={metricOptions}
        />

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <Input
            label={metricType === 'blood_pressure' ? 'Systolic (mmHg)' : `Value (${metricDefinitions[metricType].unit})`}
            type="number"
            step="any"
            placeholder={metricType === 'blood_pressure' ? '120' : '72'}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            error={errors.value}
            required
          />

          {metricType === 'blood_pressure' && (
            <Input
              label="Diastolic (mmHg)"
              type="number"
              step="any"
              placeholder="80"
              value={secondaryValue}
              onChange={(e) => setSecondaryValue(e.target.value)}
              error={errors.secondaryValue}
              required
            />
          )}

          <div className={metricType === 'blood_pressure' ? 'sm:col-span-2' : ''}>
            <Input
              label="Date Recorded"
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              required
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 tracking-wide uppercase mb-1.5">
            Context Notes (Optional)
          </label>
          <textarea
            rows={2}
            className="w-full bg-white text-slate-900 placeholder:text-slate-400 text-sm rounded-xl border border-slate-200 px-3.5 py-2.5 focus:outline-none focus:ring-2 focus:ring-sky-500/20 focus:border-sky-500"
            placeholder="e.g. Resting morning measurement, fasting for 8 hours"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          />
        </div>

        <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
          <Button type="button" variant="outline" size="md" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" variant="primary" size="md" isLoading={isSubmitting}>
            Save Record
          </Button>
        </div>
      </form>
    </Modal>
  )
}
