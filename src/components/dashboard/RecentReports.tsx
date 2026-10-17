import React from 'react'
import { Link } from 'react-router-dom'
import { FileText, ArrowRight, Sparkles } from 'lucide-react'
import { Card, CardHeader, CardTitle } from '../ui/Card'
import { Badge } from '../ui/Badge'
import { MedicalReport } from '../../types'

interface RecentReportsProps {
  reports: MedicalReport[]
  isLoading?: boolean
}

export const RecentReports: React.FC<RecentReportsProps> = ({ reports, isLoading = false }) => {
  const displayReports = reports.slice(0, 3)

  return (
    <Card className="p-6">
      <CardHeader className="flex flex-row items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <CardTitle>Recent Medical Reports</CardTitle>
          <Badge variant="info" size="sm">
            AI-Analyzed
          </Badge>
        </div>
        <Link
          to="/reports"
          className="text-xs font-semibold text-sky-600 hover:text-sky-700 flex items-center gap-1"
        >
          <span>View All ({reports.length})</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </CardHeader>

      <div className="space-y-3 mt-3">
        {isLoading ? (
          <div className="space-y-2 py-4">
            <div className="h-14 bg-slate-100 rounded-xl animate-pulse" />
            <div className="h-14 bg-slate-100 rounded-xl animate-pulse" />
          </div>
        ) : displayReports.length === 0 ? (
          <div className="text-center py-6 text-slate-500 text-sm">
            No medical reports uploaded yet.
          </div>
        ) : (
          displayReports.map((report) => (
            <div
              key={report.id}
              className="p-4 rounded-xl border border-slate-200/80 bg-white hover:border-sky-300 hover:shadow-xs transition-all duration-150 flex flex-col sm:flex-row sm:items-center justify-between gap-3"
            >
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-xl bg-sky-50 text-sky-600 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <FileText className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-slate-900 leading-snug">{report.name}</h4>
                  <div className="flex flex-wrap items-center gap-2 mt-1 text-xs text-slate-500">
                    <span>{report.uploadedAt}</span>
                    <span>•</span>
                    <span>{report.type}</span>
                    {report.doctorOrLab && (
                      <>
                        <span>•</span>
                        <span className="truncate max-w-[150px] sm:max-w-[200px]">{report.doctorOrLab}</span>
                      </>
                    )}
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between sm:justify-end gap-3 self-stretch sm:self-auto pt-2 sm:pt-0 border-t sm:border-t-0 border-slate-100">
                <Badge variant={report.status === 'analyzed' ? 'success' : 'neutral'} size="sm">
                  {report.status === 'analyzed' ? 'Analyzed' : report.status}
                </Badge>
                <Link
                  to={`/reports/${report.id}/analysis`}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-sky-700 bg-sky-50 hover:bg-sky-100 transition-colors"
                >
                  <Sparkles className="w-3.5 h-3.5 text-sky-600" />
                  <span>View Explanation</span>
                </Link>
              </div>
            </div>
          ))
        )}
      </div>
    </Card>
  )
}
