import React from 'react'
import { Badge } from '../ui/Badge'
import { ReportStatus } from '../../types'
import { CheckCircle2, Clock, AlertTriangle, FileUp } from 'lucide-react'

export const ReportStatusBadge: React.FC<{ status: ReportStatus }> = ({ status }) => {
  switch (status) {
    case 'analyzed':
      return (
        <Badge variant="success" size="sm">
          <CheckCircle2 className="w-3 h-3 text-emerald-600" />
          <span>Analyzed</span>
        </Badge>
      )
    case 'processing':
      return (
        <Badge variant="warning" size="sm">
          <Clock className="w-3 h-3 text-amber-600 animate-spin" />
          <span>Processing...</span>
        </Badge>
      )
    case 'uploaded':
      return (
        <Badge variant="info" size="sm">
          <FileUp className="w-3 h-3 text-sky-600" />
          <span>Uploaded</span>
        </Badge>
      )
    case 'failed':
      return (
        <Badge variant="danger" size="sm">
          <AlertTriangle className="w-3 h-3 text-rose-600" />
          <span>Failed</span>
        </Badge>
      )
    default:
      return <Badge variant="neutral" size="sm">{status}</Badge>
  }
}
