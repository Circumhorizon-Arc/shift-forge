import React from 'react'
import { Card } from '../ui/Card'
import { cn } from '../../utils/cn'

interface StatCardProps {
  title: string
  value: string
  subtitle?: string
  icon: React.ReactNode
  color?: 'sky' | 'teal' | 'emerald' | 'amber'
  actionText?: string
  onAction?: () => void
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  color = 'sky',
  actionText,
  onAction,
}) => {
  const colorStyles = {
    sky: 'bg-sky-50 text-sky-600 border-sky-100',
    teal: 'bg-teal-50 text-teal-600 border-teal-100',
    emerald: 'bg-emerald-50 text-emerald-600 border-emerald-100',
    amber: 'bg-amber-50 text-amber-600 border-amber-100',
  }

  return (
    <Card hoverEffect className="p-5 flex flex-col justify-between">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{title}</p>
          <h3 className="text-2xl font-bold text-slate-900 mt-1 tracking-tight">{value}</h3>
          {subtitle && <p className="text-xs text-slate-500 mt-1 font-medium">{subtitle}</p>}
        </div>
        <div className={cn('p-3 rounded-xl border flex-shrink-0', colorStyles[color])}>
          {icon}
        </div>
      </div>

      {actionText && onAction && (
        <div className="mt-4 pt-3 border-t border-slate-100">
          <button
            onClick={onAction}
            className="text-xs font-semibold text-sky-600 hover:text-sky-700 hover:underline flex items-center gap-1"
          >
            {actionText} →
          </button>
        </div>
      )}
    </Card>
  )
}
