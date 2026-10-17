import React from 'react'
import { Link } from 'react-router-dom'
import { FileText, Sparkles, Calendar, Building, HardDrive, Trash2 } from 'lucide-react'
import { Card } from '../ui/Card'
import { ReportStatusBadge } from './ReportStatusBadge'
import { MedicalReport } from '../../types'

interface ReportCardProps {
  report: MedicalReport
  onDelete?: (id: string) => void
}

export const ReportCard: React.FC<ReportCardProps> = ({ report, onDelete }) => {
  return (
    <Card hoverEffect className="p-5 flex flex-col justify-between">
      <div>
        {/* Top: Icon + Status */}
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="w-10 h-10 rounded-xl bg-sky-50 text-sky-600 flex items-center justify-center flex-shrink-0">
            <FileText className="w-5 h-5" />
          </div>
          <ReportStatusBadge status={report.status} />
        </div>

        {/* Title and Lab */}
        <h3 className="text-base font-bold text-slate-900 leading-snug tracking-tight mb-1">
          {report.name}
        </h3>
        {report.doctorOrLab && (
          <p className="text-xs text-slate-500 flex items-center gap-1.5 mb-3">
            <Building className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
            <span className="truncate">{report.doctorOrLab}</span>
          </p>
        )}

        {report.summaryPreview && (
          <p className="text-xs text-slate-600 line-clamp-2 leading-relaxed bg-slate-50/80 p-2.5 rounded-lg border border-slate-100 mb-3">
            {report.summaryPreview}
          </p>
        )}

        {/* Metadata info */}
        <div className="flex flex-wrap items-center gap-3 text-xs text-slate-600 pt-2 border-t border-slate-100">
          <div className="flex items-center gap-1">
            <Calendar className="w-3.5 h-3.5 text-slate-500" />
            <span>{report.uploadedAt}</span>
          </div>
          <span>•</span>
          <span className="font-medium text-slate-700">{report.type}</span>
          {report.fileSize && (
            <>
              <span>•</span>
              <div className="flex items-center gap-1 text-slate-600">
                <HardDrive className="w-3 h-3" />
                <span>{report.fileSize}</span>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Action Footer */}
      <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
        {onDelete && (
          <button
            onClick={() => onDelete(report.id)}
            className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors"
            title="Remove report"
            aria-label="Delete report"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        )}

        <Link
          to={`/reports/${report.id}/analysis`}
          className="ml-auto inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold text-sky-700 bg-sky-50 hover:bg-sky-100 border border-sky-100 transition-colors shadow-2xs"
        >
          <Sparkles className="w-3.5 h-3.5 text-sky-600" />
          <span>View AI Explanation</span>
        </Link>
      </div>
    </Card>
  )
}
