import React from 'react'
import { ReportFinding } from '../../types'
import { Badge } from '../ui/Badge'
import { CheckCircle2, AlertCircle, HelpCircle } from 'lucide-react'

interface FindingCardProps {
  finding: ReportFinding
}

export const FindingCard: React.FC<FindingCardProps> = ({ finding }) => {
  const isWithinRange = finding.interpretation === 'within-range'
  const isOutsideRange = finding.interpretation === 'outside-range'

  // Safety compliant status labels
  const statusLabel = isWithinRange
    ? 'Within reported reference range'
    : isOutsideRange
    ? "Outside the laboratory's stated reference range"
    : 'Reference status unknown'

  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 p-5 shadow-xs hover:border-slate-300 transition-all duration-150 flex flex-col justify-between">
      <div>
        {/* Top: Category + Status Badge */}
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="min-w-0">
            {finding.category && (
              <span className="text-[10px] font-bold tracking-wider uppercase text-slate-600 block mb-1">
                {finding.category}
              </span>
            )}
            <h4 className="text-base font-bold text-slate-900 leading-snug tracking-tight">
              {finding.testName}
            </h4>
          </div>

          <Badge
            variant={isWithinRange ? 'success' : isOutsideRange ? 'warning' : 'neutral'}
            size="sm"
            className="flex-shrink-0"
          >
            {isWithinRange ? (
              <CheckCircle2 className="w-3 h-3 text-emerald-600" />
            ) : isOutsideRange ? (
              <AlertCircle className="w-3 h-3 text-amber-600" />
            ) : (
              <HelpCircle className="w-3 h-3 text-slate-500" />
            )}
            <span>{isWithinRange ? 'In Range' : isOutsideRange ? 'Outside Range' : 'Unknown'}</span>
          </Badge>
        </div>

        {/* Fact Value */}
        <div className="my-3 p-3.5 bg-slate-50/80 rounded-xl border border-slate-100 flex items-baseline justify-between">
          <div>
            <span className="text-2xl font-extrabold text-slate-900 tracking-tight">
              {finding.value}
            </span>
            <span className="text-xs font-semibold text-slate-500 ml-1.5">{finding.unit}</span>
          </div>

          {finding.referenceRange && (
            <div className="text-right">
              <span className="text-[10px] font-semibold text-slate-600 uppercase tracking-wider block">
                Lab Reference Interval
              </span>
              <span className="text-xs font-semibold text-slate-700 mt-0.5 block">
                {finding.referenceRange}
              </span>
            </div>
          )}
        </div>

        {/* Visual reference representation */}
        {finding.referenceRange && (
          <div className="mt-3">
            <div className="flex justify-between text-[11px] text-slate-600 mb-1">
              <span>Lower Bound</span>
              <span>Laboratory Target</span>
              <span>Upper Bound</span>
            </div>
            <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden flex">
              <div
                className={`h-full transition-all duration-300 ${
                  isWithinRange
                    ? 'bg-emerald-500 w-3/4 mx-auto rounded-full'
                    : finding.flag === 'low'
                    ? 'bg-amber-400 w-1/4 rounded-l-full'
                    : 'bg-amber-400 w-1/4 ml-auto rounded-r-full'
                }`}
              />
            </div>
          </div>
        )}
      </div>

      {/* Safety compliant descriptive status footer */}
      <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
        <span className="font-semibold text-slate-600">Extracted Status:</span>
        <span
          className={`font-semibold text-right ${
            isWithinRange ? 'text-emerald-700' : isOutsideRange ? 'text-amber-800' : 'text-slate-600'
          }`}
        >
          {statusLabel}
        </span>
      </div>
    </div>
  )
}
