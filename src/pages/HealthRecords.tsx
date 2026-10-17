import React, { useEffect, useState } from 'react'
import {
  Plus,
  RefreshCw,
  Activity,
  Trash2,
  Calendar,
  FileSpreadsheet,
} from 'lucide-react'
import { Button } from '../components/ui/Button'
import { HealthChart } from '../components/health/HealthChart'
import { HealthRecordFormModal } from '../components/health/HealthRecordFormModal'
import { Card, CardHeader, CardTitle } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { EmptyState } from '../components/ui/EmptyState'
import { MedicalDisclaimer } from '../components/reports/MedicalDisclaimer'
import { healthService } from '../services/healthService'
import { HealthRecord, HealthMetricType } from '../types'
import { metricDefinitions } from '../data/mock/mockHealthRecords'
import { useToast } from '../context/ToastContext'

export const HealthRecordsPage: React.FC = () => {
  const [records, setRecords] = useState<HealthRecord[]>([])
  const [activeMetric, setActiveMetric] = useState<HealthMetricType>('heart_rate')
  const [isLoading, setIsLoading] = useState(true)
  const [isAddModalOpen, setIsAddModalOpen] = useState(false)

  const { success, error: toastError } = useToast()

  const loadRecords = async () => {
    setIsLoading(true)
    try {
      const data = await healthService.getHealthRecords()
      setRecords(data)
    } catch {
      toastError('Could not load health records.')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadRecords()
  }, [])

  const handleDeleteRecord = async (id: string) => {
    if (window.confirm('Delete this health measurement?')) {
      try {
        await healthService.deleteHealthRecord(id)
        setRecords((prev) => prev.filter((r) => r.id !== id))
        success('Record deleted.')
      } catch {
        toastError('Failed to delete record.')
      }
    }
  }

  const handleRecordAdded = (newRecord: HealthRecord) => {
    setRecords((prev) => [newRecord, ...prev])
    setActiveMetric(newRecord.metricType)
  }

  const currentRecords = records
    .filter((r) => r.metricType === activeMetric)
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())

  return (
    <div className="space-y-6 animate-fade-in pb-12">
      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-200/80">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Health Records & Biomarkers
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Track and visualize your vital signs and routine health metrics over time.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <Button
            variant="outline"
            size="md"
            onClick={loadRecords}
            leftIcon={<RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />}
          >
            Refresh
          </Button>
          <Button
            variant="primary"
            size="md"
            onClick={() => setIsAddModalOpen(true)}
            leftIcon={<Plus className="w-4 h-4" />}
          >
            + Add Record
          </Button>
        </div>
      </div>

      <MedicalDisclaimer compact />

      {/* Interactive Recharts Trend Visualizer */}
      <HealthChart
        records={records}
        activeMetric={activeMetric}
        onMetricChange={setActiveMetric}
        isLoading={isLoading}
      />

      {/* Historical Entries Table */}
      <Card className="p-6">
        <CardHeader className="flex flex-row items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <CardTitle>Historical Log — {metricDefinitions[activeMetric].label}</CardTitle>
            <Badge variant="neutral" size="sm">
              {currentRecords.length} recorded entries
            </Badge>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsAddModalOpen(true)}
            leftIcon={<Plus className="w-3.5 h-3.5" />}
          >
            Log Entry
          </Button>
        </CardHeader>

        {currentRecords.length === 0 ? (
          <EmptyState
            icon={<FileSpreadsheet className="w-8 h-8" />}
            title="No records logged yet"
            description={`Log your first ${metricDefinitions[activeMetric].label.toLowerCase()} entry to generate a trend graph.`}
            actionLabel="Add Record"
            onAction={() => setIsAddModalOpen(true)}
            className="my-4"
          />
        ) : (
          <div className="overflow-x-auto mt-4">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-slate-200 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  <th className="pb-3 px-3">Date</th>
                  <th className="pb-3 px-3">Measurement</th>
                  <th className="pb-3 px-3">Context / Notes</th>
                  <th className="pb-3 px-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {currentRecords.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3 px-3 font-medium text-slate-800 flex items-center gap-2">
                      <Calendar className="w-3.5 h-3.5 text-slate-400" />
                      <span>{r.date}</span>
                    </td>
                    <td className="py-3 px-3">
                      <span className="font-bold text-slate-900">
                        {r.value}
                        {r.secondaryValue ? `/${r.secondaryValue}` : ''}
                      </span>{' '}
                      <span className="text-xs text-slate-500">{r.unit}</span>
                    </td>
                    <td className="py-3 px-3 text-xs text-slate-600 max-w-xs truncate">
                      {r.notes || '—'}
                    </td>
                    <td className="py-3 px-3 text-right">
                      <button
                        onClick={() => handleDeleteRecord(r.id)}
                        className="p-1 rounded text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors"
                        title="Delete entry"
                        aria-label="Delete entry"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* Add Record Modal */}
      <HealthRecordFormModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        onSuccess={handleRecordAdded}
        defaultMetric={activeMetric}
      />
    </div>
  )
}
