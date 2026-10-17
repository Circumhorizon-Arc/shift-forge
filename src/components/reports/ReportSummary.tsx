import React from 'react'
import { Card, CardHeader, CardTitle } from '../ui/Card'
import { Badge } from '../ui/Badge'
import { Sparkles, FileText, CheckCircle2 } from 'lucide-react'

interface ReportSummaryProps {
  summary: string
  extractedFactsCount?: number
  labName?: string
  reportDate?: string
}

export const ReportSummary: React.FC<ReportSummaryProps> = ({
  summary,
  extractedFactsCount,
  labName,
  reportDate,
}) => {
  return (
    <Card className="p-6 border-sky-100 bg-white">
      <CardHeader className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 pb-3 border-b border-slate-100 mb-4">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-sky-50 text-sky-600 flex items-center justify-center">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <CardTitle>Plain-Language Summary</CardTitle>
            <span className="text-[11px] text-slate-500">Overview of extracted laboratory observations</span>
          </div>
        </div>

        <Badge variant="info" size="sm" className="self-start sm:self-auto bg-sky-50 text-sky-700 border-sky-200">
          <Sparkles className="w-3 h-3 text-sky-600" />
          <span>AI-assisted explanation</span>
        </Badge>
      </CardHeader>

      <div className="space-y-4">
        <p className="text-sm sm:text-base text-slate-700 leading-relaxed font-normal">
          {summary}
        </p>

        {/* Report metadata pills */}
        <div className="pt-3 border-t border-slate-100 flex flex-wrap items-center gap-4 text-xs text-slate-500">
          {reportDate && (
            <div className="flex items-center gap-1.5">
              <span className="font-semibold text-slate-700">Date:</span>
              <span>{reportDate}</span>
            </div>
          )}
          {extractedFactsCount !== undefined && (
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              <span className="font-semibold text-slate-700">{extractedFactsCount} Structured Facts Extracted</span>
            </div>
          )}
          {labName && (
            <div className="flex items-center gap-1.5">
              <FileText className="w-3.5 h-3.5 text-slate-400" />
              <span className="truncate max-w-xs">{labName}</span>
            </div>
          )}
        </div>
      </div>
    </Card>
  )
}
