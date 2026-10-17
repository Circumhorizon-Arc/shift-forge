import React, { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  FileText,
  Activity,
  Calendar,
  BellRing,
  Upload,
  Plus,
} from 'lucide-react'
import { Button } from '../components/ui/Button'
import { StatCard } from '../components/dashboard/StatCard'
import { HealthTrendChart } from '../components/dashboard/HealthTrendChart'
import { RecentReports } from '../components/dashboard/RecentReports'
import { UpcomingAppointment } from '../components/dashboard/UpcomingAppointment'
import { MedicalDisclaimer } from '../components/reports/MedicalDisclaimer'
import { useAuth } from '../context/AuthContext'
import { reportService } from '../services/reportService'
import { healthService } from '../services/healthService'
import { appointmentService } from '../services/appointmentService'
import { reminderService } from '../services/reminderService'
import { MedicalReport, HealthRecord, Appointment, Reminder } from '../types'

export const DashboardPage: React.FC = () => {
  const { user } = useAuth()
  const navigate = useNavigate()

  const [reports, setReports] = useState<MedicalReport[]>([])
  const [healthRecords, setHealthRecords] = useState<HealthRecord[]>([])
  const [appointments, setAppointments] = useState<Appointment[]>([])
  const [reminders, setReminders] = useState<Reminder[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    let mounted = true
    const loadDashboardData = async () => {
      setIsLoading(true)
      try {
        const [repData, recData, aptData, remData] = await Promise.all([
          reportService.getReports(),
          healthService.getHealthRecords(),
          appointmentService.getAppointments(),
          reminderService.getReminders(),
        ])
        if (mounted) {
          setReports(repData)
          setHealthRecords(recData)
          setAppointments(aptData)
          setReminders(remData)
        }
      } catch (err) {
        console.error('Failed to load dashboard data', err)
      } finally {
        if (mounted) setIsLoading(false)
      }
    }

    loadDashboardData()
    return () => {
      mounted = false
    }
  }, [])

  // Greeting by time of day
  const getGreeting = () => {
    const hour = new Date().getHours()
    if (hour < 12) return 'Good morning'
    if (hour < 17) return 'Good afternoon'
    return 'Good evening'
  }

  const upcomingApt = appointments.find((a) => a.status === 'upcoming') || appointments[0]
  const pendingReminders = reminders.filter((r) => !r.completed)

  return (
    <div className="space-y-6 animate-fade-in pb-12">
      {/* Header and Prominent Action */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-200/80">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            {getGreeting()}, {user?.fullName?.split(' ')[0] || 'Alex'}
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Here's an overview of your health journey and diagnostic insights.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <Button
            variant="primary"
            size="md"
            onClick={() => navigate('/reports/upload')}
            leftIcon={<Upload className="w-4 h-4" />}
            className="shadow-sm"
          >
            Upload Medical Report
          </Button>
          <Link to="/health-records">
            <Button variant="outline" size="md" leftIcon={<Plus className="w-4 h-4" />}>
              Add Vital
            </Button>
          </Link>
        </div>
      </div>

      {/* Safety Notice Banner */}
      <MedicalDisclaimer compact />

      {/* 4 Summary Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Medical Reports"
          value={isLoading ? '...' : `${reports.length} reports`}
          subtitle="Lab panels & blood tests"
          icon={<FileText className="w-5 h-5" />}
          color="sky"
          actionText="View Reports"
          onAction={() => navigate('/reports')}
        />

        <StatCard
          title="Health Records"
          value={isLoading ? '...' : `${healthRecords.length} entries`}
          subtitle="Vitals & personal metrics"
          icon={<Activity className="w-5 h-5" />}
          color="teal"
          actionText="View Records"
          onAction={() => navigate('/health-records')}
        />

        <StatCard
          title="Upcoming Appointment"
          value={
            isLoading
              ? '...'
              : upcomingApt
              ? `${upcomingApt.date === '2026-10-17' ? 'Today' : upcomingApt.date} · ${upcomingApt.time}`
              : 'None scheduled'
          }
          subtitle={upcomingApt ? upcomingApt.doctorName : 'Schedule a review'}
          icon={<Calendar className="w-5 h-5" />}
          color="emerald"
          actionText="Appointments"
          onAction={() => navigate('/appointments')}
        />

        <StatCard
          title="Reminders"
          value={isLoading ? '...' : `${pendingReminders.length} pending`}
          subtitle="Follow-ups and checks"
          icon={<BellRing className="w-5 h-5" />}
          color="amber"
          actionText="Manage Reminders"
          onAction={() => navigate('/reminders')}
        />
      </div>

      {/* Main Charts & Widgets Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Health Trend Chart (Recharts) */}
        <div className="lg:col-span-2">
          <HealthTrendChart records={healthRecords} isLoading={isLoading} />
        </div>

        {/* Right Col: Next Consultation Card */}
        <div className="lg:col-span-1">
          <UpcomingAppointment appointment={upcomingApt} isLoading={isLoading} />
        </div>
      </div>

      {/* Recent Medical Reports Section */}
      <div>
        <RecentReports reports={reports} isLoading={isLoading} />
      </div>
    </div>
  )
}
