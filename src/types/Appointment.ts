export interface Appointment {
  id: string
  doctorName: string
  specialty: string
  date: string
  time: string
  clinicOrHospital: string
  status: 'upcoming' | 'completed' | 'cancelled'
  type: 'in-person' | 'telehealth'
  notes?: string
}
