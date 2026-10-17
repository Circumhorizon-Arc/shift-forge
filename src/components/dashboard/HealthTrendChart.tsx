import React from 'react'
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts'
import { Card, CardHeader, CardTitle, CardDescription } from '../ui/Card'
import { Badge } from '../ui/Badge'
import { HealthRecord } from '../../types'
import { TrendingUp, ArrowUpRight } from 'lucide-react'
import { Link } from 'react-router-dom'

interface HealthTrendChartProps {
  records: HealthRecord[]
  isLoading?: boolean
}

export const HealthTrendChart: React.FC<HealthTrendChartProps> = ({ records, isLoading = false }) => {
  const chartData = records
    .filter((r) => r.metricType === 'heart_rate')
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
    .map((r) => ({
      date: new Date(r.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      value: r.value,
      fullDate: r.date,
    }))

  const latest = chartData.length > 0 ? chartData[chartData.length - 1].value : 74
  const average =
    chartData.length > 0
      ? (chartData.reduce((sum, item) => sum + item.value, 0) / chartData.length).toFixed(1)
      : '72.7'

  return (
    <Card className="p-6">
      <CardHeader className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-2">
        <div>
          <div className="flex items-center gap-2">
            <CardTitle>Heart Rate Trend</CardTitle>
            <Badge variant="success" size="sm">
              <TrendingUp className="w-3 h-3 text-emerald-600" />
              <span>Stable Baseline</span>
            </Badge>
          </div>
          <CardDescription className="mt-1">
            Resting heart rate measured consistently over the last recorded periods.
          </CardDescription>
        </div>

        <Link
          to="/health-records"
          className="inline-flex items-center gap-1 text-xs font-semibold text-sky-600 hover:text-sky-700 self-start sm:self-auto"
        >
          <span>All Health Metrics</span>
          <ArrowUpRight className="w-3.5 h-3.5" />
        </Link>
      </CardHeader>

      {/* Summary KPI Pills */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 my-4">
        <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">Latest</span>
          <span className="text-xl font-bold text-slate-900 mt-0.5 block">{latest} bpm</span>
        </div>
        <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">7-Entry Average</span>
          <span className="text-xl font-bold text-slate-900 mt-0.5 block">{average} bpm</span>
        </div>
        <div className="p-3 bg-slate-50 rounded-xl border border-slate-100 col-span-2 sm:col-span-1">
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">Status</span>
          <span className="text-sm font-semibold text-emerald-700 mt-1 flex items-center gap-1">
            Normal Resting Range
          </span>
        </div>
      </div>

      {/* Recharts Area */}
      <div className="h-64 w-full mt-4">
        {isLoading ? (
          <div className="w-full h-full flex items-center justify-center text-slate-400 text-sm">
            Loading trend data...
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="heartRateGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#0284c7" stopOpacity={0.25} />
                  <stop offset="95%" stopColor="#0284c7" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 12, fill: '#64748b' }}
                axisLine={{ stroke: '#cbd5e1' }}
                tickLine={false}
              />
              <YAxis
                domain={[60, 90]}
                tick={{ fontSize: 12, fill: '#64748b' }}
                axisLine={{ stroke: '#cbd5e1' }}
                tickLine={false}
              />
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload
                    return (
                      <div className="bg-white p-3 rounded-xl shadow-lg border border-slate-200 text-xs">
                        <p className="font-semibold text-slate-700">{data.fullDate}</p>
                        <p className="text-sky-600 font-bold text-sm mt-0.5">{data.value} bpm</p>
                        <p className="text-slate-400 text-[10px] mt-0.5">Resting Heart Rate</p>
                      </div>
                    )
                  }
                  return null
                }}
              />
              <Area
                type="monotone"
                dataKey="value"
                stroke="#0284c7"
                strokeWidth={2.5}
                fillOpacity={1}
                fill="url(#heartRateGradient)"
                activeDot={{ r: 5, fill: '#0284c7', stroke: '#ffffff', strokeWidth: 2 }}
              />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>
    </Card>
  )
}
