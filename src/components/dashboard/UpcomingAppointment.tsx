import React from 'react'
import { Link } from 'react-router-dom'
import { Calendar, Clock, MapPin, User, ArrowRight } from 'lucide-react'
import { Card, CardHeader, CardTitle } from '../ui/Card'
import { Appointment } from '../../types'

interface UpcomingAppointmentProps {
  appointment?: Appointment | null
  isLoading?: boolean
}

export const UpcomingAppointment: React.FC<UpcomingAppointmentProps> = ({
  appointment,
  isLoading = false,
}) => {
  return (
    <Card className="p-6">
      <CardHeader className="flex flex-row items-center justify-between mb-2">
        <CardTitle>Next Consultation</CardTitle>
        <Link
          to="/appointments"
          className="text-xs font-semibold text-sky-600 hover:text-sky-700 flex items-center gap-1"
        >
          <span>Appointments</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </CardHeader>

      {isLoading ? (
        <div className="h-24 bg-slate-100 rounded-xl animate-pulse mt-2" />
      ) : appointment ? (
        <div className="mt-3 p-4 rounded-xl bg-gradient-to-br from-sky-50/70 to-teal-50/50 border border-sky-100">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 rounded-xl bg-sky-600 text-white flex items-center justify-center flex-shrink-0">
              <User className="w-5 h-5" />
            </div>
            <div className="flex-1 min-w-0">
              <h4 className="text-sm font-bold text-slate-900 leading-snug">{appointment.doctorName}</h4>
              <p className="text-xs text-slate-600 mt-0.5">{appointment.specialty}</p>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-3 pt-3 border-t border-sky-100/80 text-xs text-slate-700">
                <div className="flex items-center gap-1.5 font-medium">
                  <Calendar className="w-3.5 h-3.5 text-sky-600" />
                  <span>{appointment.date === '2026-10-17' ? 'Today' : appointment.date}</span>
                </div>
                <div className="flex items-center gap-1.5 font-medium">
                  <Clock className="w-3.5 h-3.5 text-sky-600" />
                  <span>{appointment.time}</span>
                </div>
                <div className="flex items-center gap-1.5 text-slate-500 sm:col-span-2">
                  <MapPin className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
                  <span className="truncate">{appointment.clinicOrHospital}</span>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-sky-100 flex justify-end">
            <Link
              to="/appointments"
              className="text-xs font-semibold text-sky-700 hover:text-sky-800"
            >
              View Appointment Details →
            </Link>
          </div>
        </div>
      ) : (
        <div className="text-center py-6 text-slate-500 text-sm">
          No upcoming appointments scheduled.
        </div>
      )}
    </Card>
  )
}
