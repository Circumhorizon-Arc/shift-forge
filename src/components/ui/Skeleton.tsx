import React from 'react'
import { cn } from '../../utils/cn'

export interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'text' | 'rectangular' | 'circular'
}

export const Skeleton: React.FC<SkeletonProps> = ({
  className,
  variant = 'rectangular',
  ...props
}) => {
  return (
    <div
      className={cn(
        'animate-pulse bg-slate-200/80',
        variant === 'circular' && 'rounded-full',
        variant === 'text' && 'h-4 rounded-md',
        variant === 'rectangular' && 'rounded-xl',
        className
      )}
      {...props}
    />
  )
}
