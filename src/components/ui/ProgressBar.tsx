import React from 'react'
import { cn } from '../../utils/cn'

export interface ProgressBarProps {
  progress: number // 0 to 100
  color?: 'sky' | 'teal' | 'emerald' | 'amber'
  height?: 'sm' | 'md' | 'lg'
  showLabel?: boolean
  className?: string
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  progress,
  color = 'sky',
  height = 'md',
  showLabel = false,
  className,
}) => {
  const clamped = Math.min(100, Math.max(0, progress))

  const heightStyles = {
    sm: 'h-1.5',
    md: 'h-2.5',
    lg: 'h-4',
  }

  const colorStyles = {
    sky: 'bg-sky-600',
    teal: 'bg-teal-600',
    emerald: 'bg-emerald-600',
    amber: 'bg-amber-500',
  }

  return (
    <div className={cn('w-full', className)}>
      {showLabel && (
        <div className="flex justify-between items-center text-xs font-semibold text-slate-600 mb-1.5">
          <span>Progress</span>
          <span>{clamped}%</span>
        </div>
      )}
      <div className={cn('w-full bg-slate-100 rounded-full overflow-hidden', heightStyles[height])}>
        <div
          className={cn('h-full transition-all duration-300 ease-out rounded-full', colorStyles[color])}
          style={{ width: `${clamped}%` }}
        />
      </div>
    </div>
  )
}
