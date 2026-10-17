import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { AppLayout } from '../components/layout/AppLayout'
import { LandingPage } from '../pages/Landing'
import { LoginPage } from '../pages/Login'
import { RegisterPage } from '../pages/Register'
import { DashboardPage } from '../pages/Dashboard'
import { ReportsPage } from '../pages/Reports'
import { UploadReportPage } from '../pages/UploadReport'
import { ReportAnalysisPage } from '../pages/ReportAnalysis'
import { HealthRecordsPage } from '../pages/HealthRecords'
import { AppointmentsPage } from '../pages/Appointments'
import { RemindersPage } from '../pages/Reminders'
import { SettingsPage } from '../pages/Settings'

export const AppRoutes: React.FC = () => {
  return (
    <Routes>
      {/* Public Pages */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      {/* Main Application Layout & Nested Routes */}
      <Route element={<AppLayout />}>
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/reports" element={<ReportsPage />} />
        <Route path="/reports/upload" element={<UploadReportPage />} />
        <Route path="/reports/:id/analysis" element={<ReportAnalysisPage />} />
        <Route path="/health-records" element={<HealthRecordsPage />} />
        <Route path="/appointments" element={<AppointmentsPage />} />
        <Route path="/reminders" element={<RemindersPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Route>

      {/* Catch-all fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
