import React, { useEffect, useState } from 'react'
import {
  Calendar,
  Clock,
  MapPin,
  User,
  Plus,
  RefreshCw,
  Video,
  CheckCircle2,
  CalendarDays,
} from 'lucide-react'
import { Button } from '../components/ui/Button'
import { Card, CardHeader, CardTitle } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { Modal } from '../components/ui/Modal'
import { Input } from '../components/ui/Input'
import { Select } from '../components/ui/Select'
import { EmptyState } from '../components/ui/EmptyState'
import { Skeleton } from '../components/ui/Skeleton'
import { appointmentService } from '../services/appointmentService'
import { Appointment } from '../types'
import { useToast } from '../context/ToastContext'

export const AppointmentsPage: React.FC = () => {
  const [appointments, setAppointments] = useState<Appointment[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'upcoming' | 'completed'>('upcoming')
  const [isBookModalOpen, setIsBookModalOpen] = useState(false)
  const [selectedAppointment, setSelectedAppointment] = useState<Appointment | null>(null)

  // Form states
  const [doctorName, setDoctorName] = useState('')
  const [specialty, setSpecialty] = useState('')
  const [date, setDate] = useState('')
  const [time, setTime] = useState('')
  const [clinicOrHospital, setClinicOrHospital] = useState('')
  const [type, setType] = useState<'in-person' | 'telehealth'>('in-person')
  const [notes, setNotes] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const { success, error: toastError } = useToast()

  const loadAppointments = async () => {
    setIsLoading(true)
    try {
      const data = await appointmentService.getAppointments()
      setAppointments(data)
    } catch {
      toastError('Could not load appointments.')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadAppointments()
  }, [])

  const handleBookAppointment = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!doctorName || !date || !time) {
      toastError('Please fill in doctor name, date, and time.')
      return
    }

    setIsSubmitting(true)
    try {
      const newApt = await appointmentService.createAppointment({
        doctorName: doctorName.startsWith('Dr.') ? doctorName : `Dr. ${doctorName}`,
        specialty: specialty || 'General Medicine',
        date,
        time,
        clinicOrHospital: clinicOrHospital || 'City Health Medical Center',
        type,
        status: 'upcoming',
        notes: notes.trim() || undefined,
      })

      setAppointments((prev) => [newApt, ...prev])
      success('Appointment booked successfully.')
      setIsBookModalOpen(false)

      // Reset form
      setDoctorName('')
      setSpecialty('')
      setDate('')
      setTime('')
      setClinicOrHospital('')
      setNotes('')
    } catch {
      toastError('Failed to schedule appointment.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const upcoming = appointments.filter((a) => a.status === 'upcoming')
  const completed = appointments.filter((a) => a.status === 'completed' || a.status === 'cancelled')
  const displayed = activeTab === 'upcoming' ? upcoming : completed

  return (
    <div className="space-y-6 animate-fade-in pb-12">
      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-200/80">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Appointments & Consultations
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Manage your scheduled physician discussions, specialist reviews, and telehealth calls.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <Button
            variant="outline"
            size="md"
            onClick={loadAppointments}
            leftIcon={<RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />}
          >
            Refresh
          </Button>
          <Button
            variant="primary"
            size="md"
            onClick={() => setIsBookModalOpen(true)}
            leftIcon={<Plus className="w-4 h-4" />}
          >
            + Book Appointment
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-200">
        <button
          onClick={() => setActiveTab('upcoming')}
          className={`pb-3 px-4 text-sm font-semibold transition-colors border-b-2 -mb-px flex items-center gap-2 ${
            activeTab === 'upcoming'
              ? 'border-sky-600 text-sky-700'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <span>Upcoming ({upcoming.length})</span>
        </button>
        <button
          onClick={() => setActiveTab('completed')}
          className={`pb-3 px-4 text-sm font-semibold transition-colors border-b-2 -mb-px flex items-center gap-2 ${
            activeTab === 'completed'
              ? 'border-sky-600 text-sky-700'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <span>Past Consultations ({completed.length})</span>
        </button>
      </div>

      {/* Appointments List */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Skeleton className="h-44 rounded-2xl" />
          <Skeleton className="h-44 rounded-2xl" />
        </div>
      ) : displayed.length === 0 ? (
        <EmptyState
          icon={<CalendarDays className="w-8 h-8" />}
          title={activeTab === 'upcoming' ? 'No upcoming appointments' : 'No past appointments logged'}
          description={
            activeTab === 'upcoming'
              ? 'Schedule your next clinical review or follow-up with your physician.'
              : 'Completed consultations will appear here once archived.'
          }
          actionLabel={activeTab === 'upcoming' ? 'Book Appointment' : undefined}
          onAction={activeTab === 'upcoming' ? () => setIsBookModalOpen(true) : undefined}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {displayed.map((apt) => (
            <Card key={apt.id} hoverEffect className="p-5 flex flex-col justify-between">
              <div>
                <div className="flex items-start justify-between gap-3 mb-3">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-sky-50 text-sky-600 flex items-center justify-center flex-shrink-0">
                      <User className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="text-base font-bold text-slate-900 leading-snug">{apt.doctorName}</h3>
                      <p className="text-xs text-slate-500">{apt.specialty}</p>
                    </div>
                  </div>

                  <Badge variant={apt.status === 'upcoming' ? 'info' : 'neutral'} size="sm">
                    {apt.status === 'upcoming' ? 'Upcoming' : 'Completed'}
                  </Badge>
                </div>

                <div className="space-y-2 mt-4 pt-3 border-t border-slate-100 text-xs text-slate-600">
                  <div className="flex items-center gap-2">
                    <Calendar className="w-3.5 h-3.5 text-sky-600 flex-shrink-0" />
                    <span className="font-semibold text-slate-800">
                      {apt.date === '2026-10-17' ? 'Today' : apt.date}
                    </span>
                    <span>•</span>
                    <Clock className="w-3.5 h-3.5 text-sky-600 flex-shrink-0" />
                    <span>{apt.time}</span>
                  </div>

                  <div className="flex items-center gap-2">
                    {apt.type === 'telehealth' ? (
                      <>
                        <Video className="w-3.5 h-3.5 text-teal-600 flex-shrink-0" />
                        <span className="text-teal-700 font-medium">Telehealth Video Session</span>
                      </>
                    ) : (
                      <>
                        <MapPin className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
                        <span className="truncate">{apt.clinicOrHospital}</span>
                      </>
                    )}
                  </div>

                  {apt.notes && (
                    <div className="p-2.5 bg-slate-50 rounded-lg text-slate-600 mt-2 italic text-[11px] leading-relaxed">
                      "{apt.notes}"
                    </div>
                  )}
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
                <span className="text-[11px] font-medium text-slate-400">ID: {apt.id}</span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setSelectedAppointment(apt)}
                >
                  View Details
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Book Appointment Modal */}
      <Modal
        isOpen={isBookModalOpen}
        onClose={() => setIsBookModalOpen(false)}
        title="Book Doctor Appointment"
        description="Schedule a follow-up consultation or annual health checkup."
      >
        <form onSubmit={handleBookAppointment} className="space-y-4">
          <Input
            label="Doctor Name"
            placeholder="e.g. Dr. Sarah Sharma"
            value={doctorName}
            onChange={(e) => setDoctorName(e.target.value)}
            required
          />

          <Input
            label="Specialty / Field"
            placeholder="e.g. Internal Medicine, Cardiology, Primary Care"
            value={specialty}
            onChange={(e) => setSpecialty(e.target.value)}
          />

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <Input
              label="Date"
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              required
            />
            <Input
              label="Time"
              type="time"
              value={time}
              onChange={(e) => setTime(e.target.value)}
              required
            />
          </div>

          <Select
            label="Consultation Format"
            value={type}
            onChange={(e) => setType(e.target.value as 'in-person' | 'telehealth')}
            options={[
              { value: 'in-person', label: 'In-Person Clinic Visit' },
              { value: 'telehealth', label: 'Telehealth Video Consultation' },
            ]}
          />

          <Input
            label="Clinic / Facility Location"
            placeholder="e.g. City General Wellness Pavilion, Suite 402"
            value={clinicOrHospital}
            onChange={(e) => setClinicOrHospital(e.target.value)}
          />

          <div>
            <label className="block text-xs font-semibold text-slate-700 tracking-wide uppercase mb-1.5">
              Consultation Goals & Notes
            </label>
            <textarea
              rows={2}
              className="w-full bg-white text-slate-900 placeholder:text-slate-400 text-sm rounded-xl border border-slate-200 px-3.5 py-2.5 focus:outline-none focus:ring-2 focus:ring-sky-500/20 focus:border-sky-500"
              placeholder="e.g. Discuss recent metabolic panel and fasting glucose"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
            />
          </div>

          <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
            <Button type="button" variant="outline" size="md" onClick={() => setIsBookModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" size="md" isLoading={isSubmitting}>
              Confirm Booking
            </Button>
          </div>
        </form>
      </Modal>

      {/* View Details Modal */}
      {selectedAppointment && (
        <Modal
          isOpen={!!selectedAppointment}
          onClose={() => setSelectedAppointment(null)}
          title="Appointment Details"
          description="Clinical consultation scheduling overview"
        >
          <div className="space-y-4 text-sm text-slate-700">
            <div className="p-4 bg-sky-50/70 rounded-xl border border-sky-100">
              <h4 className="text-base font-bold text-slate-900">{selectedAppointment.doctorName}</h4>
              <p className="text-xs text-slate-600">{selectedAppointment.specialty}</p>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="font-semibold text-slate-500">Date:</span>
                <span className="font-medium text-slate-900">{selectedAppointment.date}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="font-semibold text-slate-500">Time:</span>
                <span className="font-medium text-slate-900">{selectedAppointment.time}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="font-semibold text-slate-500">Type:</span>
                <span className="font-medium text-slate-900 capitalize">{selectedAppointment.type}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="font-semibold text-slate-500">Location:</span>
                <span className="font-medium text-slate-900">{selectedAppointment.clinicOrHospital}</span>
              </div>
              {selectedAppointment.notes && (
                <div className="pt-2">
                  <span className="font-semibold text-slate-500 block mb-1">Appointment Purpose:</span>
                  <p className="p-2.5 bg-slate-50 rounded-lg text-slate-700">{selectedAppointment.notes}</p>
                </div>
              )}
            </div>

            <div className="pt-3 border-t border-slate-100 flex justify-end">
              <Button variant="primary" size="md" onClick={() => setSelectedAppointment(null)}>
                Done
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  )
}
