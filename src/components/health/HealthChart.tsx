import React from 'react'
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts'
import { Card, CardHeader, CardTitle, CardDescription } from '../ui/Card'
import { Badge } from '../ui/Badge'
import { HealthRecord, HealthMetricType } from '../../types'
import { metricDefinitions } from '../../data/mock/mockHealthRecords'
import { Activity } from 'lucide-react'

interface HealthChartProps {
  records: HealthRecord[]
  activeMetric: HealthMetricType
  onMetricChange: (metric: HealthMetricType) => void
  isLoading?: boolean
}

export const HealthChart: React.FC<HealthChartProps> = ({
  records,
  activeMetric,
  onMetricChange,
  isLoading = false,
}) => {
  const currentDef = metricDefinitions[activeMetric]

  const filteredRecords = records
    .filter((r) => r.metricType === activeMetric)
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())

  const chartData = filteredRecords.map((r) => ({
    date: new Date(r.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    value: r.value,
    secondaryValue: r.secondaryValue,
    fullDate: r.date,
    notes: r.notes,
  }))

  const metrics: { type: HealthMetricType; label: string }[] = [
    { type: 'heart_rate', label: 'Heart Rate' },
    { type: 'blood_pressure', label: 'Blood Pressure' },
    { type: 'blood_glucose', label: 'Blood Glucose' },
    { type: 'weight', label: 'Weight' },
    { type: 'temperature', label: 'Temperature' },
  ]

  const latestRecord = filteredRecords.length > 0 ? filteredRecords[filteredRecords.length - 1] : null
  const averageValue =
    filteredRecords.length > 0
      ? (filteredRecords.reduce((sum, r) => sum + r.value, 0) / filteredRecords.length).toFixed(1)
      : '—'

  return (
    <Card className="p-6">
      <CardHeader className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-4">
        <div>
          <div className="flex items-center gap-2">
            <CardTitle>{currentDef.label} Trend</CardTitle>
            <Badge variant="info" size="sm">
              <Activity className="w-3 h-3 text-sky-600" />
              <span>Time-Series View</span>
            </Badge>
          </div>
          <CardDescription className="mt-1">{currentDef.description}</CardDescription>
        </div>

        {/* Metric Selector Pills */}
        <div className="flex flex-wrap items-center gap-1.5 p-1 bg-slate-100/80 rounded-xl border border-slate-200/80 self-start lg:self-auto">
          {metrics.map((m) => (
            <button
              key={m.type}
              onClick={() => onMetricChange(m.type)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all duration-150 select-none ${
                activeMetric === m.type
                  ? 'bg-white text-sky-700 shadow-xs font-bold'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              {m.label}
            </button>
          ))}
        </div>
      </CardHeader>

      {/* Summary Stat Tiles */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 my-4">
        <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-100">
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">Latest Reading</span>
          <span className="text-xl font-bold text-slate-900 mt-0.5 block">
            {latestRecord
              ? `${latestRecord.value}${latestRecord.secondaryValue ? `/${latestRecord.secondaryValue}` : ''} ${currentDef.unit}`
              : '—'}
          </span>
        </div>

        <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-100">
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">Average</span>
          <span className="text-xl font-bold text-slate-900 mt-0.5 block">
            {averageValue !== '—' ? `${averageValue} ${currentDef.unit}` : '—'}
          </span>
        </div>

        <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-100 col-span-2 sm:col-span-1">
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">Observation Trend</span>
          <span className="text-sm font-semibold text-teal-700 mt-1 flex items-center gap-1">
            Consistent Baseline
          </span>
        </div>
      </div>

      {/* Line Chart */}
      <div className="h-72 w-full mt-4">
        {isLoading ? (
          <div className="w-full h-full flex items-center justify-center text-slate-400 text-sm">
            Loading chart telemetry...
          </div>
        ) : chartData.length === 0 ? (
          <div className="w-full h-full flex flex-col items-center justify-center text-slate-400 text-sm">
            <span>No data points recorded for this metric yet.</span>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 15, right: 15, left: -15, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 12, fill: '#64748b' }}
                axisLine={{ stroke: '#cbd5e1' }}
                tickLine={false}
              />
              <YAxis
                domain={['auto', 'auto']}
                tick={{ fontSize: 12, fill: '#64748b' }}
                axisLine={{ stroke: '#cbd5e1' }}
                tickLine={false}
              />
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload
                    return (
                      <div className="bg-white p-3 rounded-xl shadow-lg border border-slate-200 text-xs space-y-1">
                        <p className="font-semibold text-slate-700">{data.fullDate}</p>
                        <p className="text-sky-600 font-bold text-sm">
                          {data.value}
                          {data.secondaryValue ? ` / ${data.secondaryValue}` : ''} {currentDef.unit}
                        </p>
                        {data.notes && <p className="text-slate-500 text-[11px] italic">{data.notes}</p>}
                      </div>
                    )
                  }
                  return null
                }}
              />
              <Line
                type="monotone"
                dataKey="value"
                name={currentDef.label}
                stroke="#0284c7"
                strokeWidth={2.5}
                dot={{ r: 4, fill: '#0284c7' }}
                activeDot={{ r: 6, fill: '#0284c7', stroke: '#fff', strokeWidth: 2 }}
              />
              {activeMetric === 'blood_pressure' && (
                <Line
                  type="monotone"
                  dataKey="secondaryValue"
                  name="Diastolic"
                  stroke="#0d9488"
                  strokeWidth={2}
                  strokeDasharray="4 4"
                  dot={{ r: 3, fill: '#0d9488' }}
                />
              )}
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </Card>
  )
}
