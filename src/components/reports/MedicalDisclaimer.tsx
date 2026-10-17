import React from 'react'
import { ShieldAlert, AlertCircle } from 'lucide-react'
import { cn } from '../../utils/cn'

interface MedicalDisclaimerProps {
  className?: string
  compact?: boolean
}

export const MedicalDisclaimer: React.FC<MedicalDisclaimerProps> = ({ className, compact = false }) => {
  if (compact) {
    return (
      <div
        className={cn(
          'flex items-center gap-2 p-3 rounded-xl bg-amber-50/90 border border-amber-200/80 text-amber-900 text-xs leading-relaxed',
          className
        )}
      >
        <AlertCircle className="w-4 h-4 text-amber-600 flex-shrink-0" />
        <p>
          <strong>Notice:</strong> Educational information only. Health Sense does not provide medical diagnoses or replace doctor consultations.
        </p>
      </div>
    )
  }

  return (
    <aside
      aria-label="Medical safety disclaimer"
      className={cn(
        'p-5 sm:p-6 rounded-2xl bg-gradient-to-r from-amber-50/90 via-amber-50/60 to-sky-50/60 border border-amber-200/80 shadow-xs',
        className
      )}
    >
      <div className="flex items-start gap-4">
        <div className="w-10 h-10 rounded-xl bg-amber-100/80 text-amber-700 flex items-center justify-center flex-shrink-0 shadow-2xs">
          <ShieldAlert className="w-5 h-5" />
        </div>
        <div className="space-y-1.5 flex-1">
          <div className="flex items-center gap-2">
            <h4 className="text-sm font-bold text-amber-950 uppercase tracking-wide">
              Important Healthcare Safety Notice
            </h4>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-200/70 text-amber-900">
              Non-Diagnostic
            </span>
          </div>
          <p className="text-xs sm:text-sm text-amber-900/90 leading-relaxed font-normal">
            Health Sense provides educational explanations of uploaded health information. It does not diagnose medical conditions, prescribe medication, or replace professional medical advice. Please discuss your results with a qualified healthcare professional.
          </p>
        </div>
      </div>
    </aside>
  )
}
