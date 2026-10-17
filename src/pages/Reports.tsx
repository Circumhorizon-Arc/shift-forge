import React, { useEffect, useState, useMemo } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  Upload,
  Search,
  FileText,
  Filter,
  ArrowUpDown,
  RefreshCw,
} from 'lucide-react'
import { Button } from '../components/ui/Button'
import { ReportCard } from '../components/reports/ReportCard'
import { EmptyState } from '../components/ui/EmptyState'
import { Skeleton } from '../components/ui/Skeleton'
import { reportService } from '../services/reportService'
import { MedicalReport, ReportStatus } from '../types'
import { useToast } from '../context/ToastContext'

export const ReportsPage: React.FC = () => {
  const [reports, setReports] = useState<MedicalReport[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<'all' | ReportStatus>('all')
  const [sortOrder, setSortOrder] = useState<'newest' | 'oldest'>('newest')

  const navigate = useNavigate()
  const { success, error: toastError } = useToast()

  const loadReports = async () => {
    setIsLoading(true)
    try {
      const data = await reportService.getReports()
      setReports(data)
    } catch {
      toastError('Could not retrieve medical reports.')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadReports()
  }, [])

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to remove this medical report?')) {
      try {
        await reportService.deleteReport(id)
        setReports((prev) => prev.filter((r) => r.id !== id))
        success('Report removed successfully.')
      } catch {
        toastError('Failed to remove report.')
      }
    }
  }

  // Filtered and sorted reports
  const filteredReports = useMemo(() => {
    return reports
      .filter((r) => {
        const matchesQuery =
          r.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          r.type.toLowerCase().includes(searchQuery.toLowerCase()) ||
          (r.doctorOrLab && r.doctorOrLab.toLowerCase().includes(searchQuery.toLowerCase()))

        const matchesStatus = statusFilter === 'all' || r.status === statusFilter
        return matchesQuery && matchesStatus
      })
      .sort((a, b) => {
        const dateA = new Date(a.uploadedAt).getTime()
        const dateB = new Date(b.uploadedAt).getTime()
        return sortOrder === 'newest' ? dateB - dateA : dateA - dateB
      })
  }, [reports, searchQuery, statusFilter, sortOrder])

  return (
    <div className="space-y-6 animate-fade-in pb-12">
      {/* Header and Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-200/80">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Medical Reports
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Upload and understand your clinical laboratory documents.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <Button
            variant="outline"
            size="md"
            onClick={loadReports}
            leftIcon={<RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />}
            title="Refresh reports"
          >
            Refresh
          </Button>
          <Button
            variant="primary"
            size="md"
            onClick={() => navigate('/reports/upload')}
            leftIcon={<Upload className="w-4 h-4" />}
          >
            + Upload Report
          </Button>
        </div>
      </div>

      {/* Search and Filters Bar */}
      <div className="flex flex-col sm:flex-row items-center gap-3 bg-white p-3.5 rounded-2xl border border-slate-200/80 shadow-2xs">
        {/* Search Input */}
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search reports by test name, category, or lab..."
            className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-500/20 focus:border-sky-500"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="flex items-center gap-2.5 w-full sm:w-auto">
          {/* Status Filter */}
          <div className="flex items-center gap-1.5 w-full sm:w-auto">
            <Filter className="w-3.5 h-3.5 text-slate-400 hidden sm:block" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as 'all' | ReportStatus)}
              className="bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-700 rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-sky-500/20 w-full sm:w-auto cursor-pointer"
            >
              <option value="all">All Statuses</option>
              <option value="analyzed">Analyzed</option>
              <option value="processing">Processing</option>
              <option value="uploaded">Uploaded</option>
            </select>
          </div>

          {/* Sort Order */}
          <div className="flex items-center gap-1.5 w-full sm:w-auto">
            <ArrowUpDown className="w-3.5 h-3.5 text-slate-400 hidden sm:block" />
            <select
              value={sortOrder}
              onChange={(e) => setSortOrder(e.target.value as 'newest' | 'oldest')}
              className="bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-700 rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-sky-500/20 w-full sm:w-auto cursor-pointer"
            >
              <option value="newest">Newest First</option>
              <option value="oldest">Oldest First</option>
            </select>
          </div>
        </div>
      </div>

      {/* Reports Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="p-5 rounded-2xl bg-white border border-slate-200 space-y-3">
              <Skeleton className="h-6 w-1/3 rounded-md" />
              <Skeleton className="h-5 w-3/4 rounded-md" />
              <Skeleton className="h-16 w-full rounded-xl" />
              <Skeleton className="h-4 w-1/2 rounded-md" />
            </div>
          ))}
        </div>
      ) : filteredReports.length === 0 ? (
        <EmptyState
          icon={<FileText className="w-8 h-8" />}
          title={searchQuery ? 'No matching reports' : 'No medical reports yet'}
          description={
            searchQuery
              ? `No reports matched your query "${searchQuery}". Try adjusting your filters.`
              : 'Upload your first diagnostic report to begin receiving plain-language explanations.'
          }
          actionLabel={searchQuery ? 'Clear Filters' : 'Upload Report'}
          onAction={
            searchQuery
              ? () => {
                  setSearchQuery('')
                  setStatusFilter('all')
                }
              : () => navigate('/reports/upload')
          }
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredReports.map((report) => (
            <ReportCard key={report.id} report={report} onDelete={handleDelete} />
          ))}
        </div>
      )}
    </div>
  )
}
