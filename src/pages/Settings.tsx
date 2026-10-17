import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  User,
  Shield,
  Bell,
  Lock,
  LogOut,
  Save,
  CheckCircle2,
  Trash2,
} from 'lucide-react'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { Card, CardHeader, CardTitle, CardDescription } from '../components/ui/Card'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'

export const SettingsPage: React.FC = () => {
  const { user, updateProfile, logout } = useAuth()
  const { success } = useToast()
  const navigate = useNavigate()

  const [fullName, setFullName] = useState(user?.fullName || 'Alex Morgan')
  const [email, setEmail] = useState(user?.email || 'alex.morgan@healthsense.dev')
  const [phone, setPhone] = useState(user?.phone || '+1 (555) 234-5678')
  const [language, setLanguage] = useState('English (US)')
  const [notifications, setNotifications] = useState(true)
  const [isSaving, setIsSaving] = useState(false)

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSaving(true)
    try {
      await updateProfile({ fullName, email, phone })
      success('Personal information updated.')
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="space-y-6 animate-fade-in pb-16 max-w-4xl mx-auto">
      {/* Header */}
      <div className="pb-2 border-b border-slate-200/80">
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Account & Preferences
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Manage your personal profile, notification preferences, privacy permissions, and security.
        </p>
      </div>

      {/* SECTION 1: PERSONAL INFORMATION */}
      <Card className="p-6">
        <CardHeader className="flex flex-row items-center gap-3 pb-3 border-b border-slate-100 mb-4">
          <div className="w-9 h-9 rounded-xl bg-sky-50 text-sky-600 flex items-center justify-center">
            <User className="w-5 h-5" />
          </div>
          <div>
            <CardTitle>Personal Information</CardTitle>
            <CardDescription>Primary profile data associated with your health records.</CardDescription>
          </div>
        </CardHeader>

        <form onSubmit={handleSaveProfile} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label="Full Name"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
            />
            <Input
              label="Email Address"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <Input
              label="Contact Phone"
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
            />
            <Input
              label="Date of Birth"
              type="text"
              readOnly
              value={user?.dateOfBirth || '1992-05-14'}
              className="bg-slate-50 cursor-not-allowed"
            />
          </div>

          <div className="flex justify-end pt-2">
            <Button
              type="submit"
              variant="primary"
              size="md"
              isLoading={isSaving}
              leftIcon={<Save className="w-4 h-4" />}
            >
              Save Profile
            </Button>
          </div>
        </form>
      </Card>

      {/* SECTION 2: PREFERENCES */}
      <Card className="p-6">
        <CardHeader className="flex flex-row items-center gap-3 pb-3 border-b border-slate-100 mb-4">
          <div className="w-9 h-9 rounded-xl bg-teal-50 text-teal-600 flex items-center justify-center">
            <Bell className="w-5 h-5" />
          </div>
          <div>
            <CardTitle>Preferences</CardTitle>
            <CardDescription>Localization, language, and clinical alert reminders.</CardDescription>
          </div>
        </CardHeader>

        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 py-2 border-b border-slate-100">
            <div>
              <span className="text-sm font-semibold text-slate-900 block">Display Language</span>
              <span className="text-xs text-slate-500">Language for AI explanations and report translations.</span>
            </div>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="bg-white border border-slate-200 text-xs font-semibold rounded-xl px-3 py-2 text-slate-800"
            >
              <option value="English (US)">English (US)</option>
              <option value="Spanish">Español</option>
              <option value="French">Français</option>
            </select>
          </div>

          <div className="flex items-center justify-between py-2">
            <div>
              <span className="text-sm font-semibold text-slate-900 block">Appointment & Test Reminders</span>
              <span className="text-xs text-slate-500">Receive in-app alerts for pending checkups.</span>
            </div>
            <input
              type="checkbox"
              checked={notifications}
              onChange={(e) => setNotifications(e.target.checked)}
              className="w-4 h-4 text-sky-600 rounded border-slate-300 focus:ring-sky-500"
            />
          </div>
        </div>
      </Card>

      {/* SECTION 3: PRIVACY & PERMISSIONS */}
      <Card className="p-6">
        <CardHeader className="flex flex-row items-center gap-3 pb-3 border-b border-slate-100 mb-4">
          <div className="w-9 h-9 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
            <Shield className="w-5 h-5" />
          </div>
          <div>
            <CardTitle>Privacy & Data Rights</CardTitle>
            <CardDescription>Control how your clinical data is securely managed.</CardDescription>
          </div>
        </CardHeader>

        <div className="space-y-4 text-sm text-slate-600">
          <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-100 flex items-start gap-2.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
            <p className="text-xs leading-relaxed text-slate-700">
              <strong>De-identified Processing:</strong> Uploaded medical documents are analyzed in an isolated sandbox. We do not sell your personal telemetry or commercialize your medical records.
            </p>
          </div>

          <div className="flex items-center justify-between pt-2">
            <div>
              <span className="text-sm font-semibold text-slate-900 block">Export Health History</span>
              <span className="text-xs text-slate-500">Download a full JSON archive of all uploaded reports and logged vitals.</span>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => success('Archive bundle prepared for download.')}
            >
              Download Archive
            </Button>
          </div>
        </div>
      </Card>

      {/* SECTION 4: SECURITY & SESSION */}
      <Card className="p-6">
        <CardHeader className="flex flex-row items-center gap-3 pb-3 border-b border-slate-100 mb-4">
          <div className="w-9 h-9 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center">
            <Lock className="w-5 h-5" />
          </div>
          <div>
            <CardTitle>Security & Session</CardTitle>
            <CardDescription>Password updates and session termination.</CardDescription>
          </div>
        </CardHeader>

        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div>
            <span className="text-sm font-semibold text-slate-900 block">Current Session</span>
            <span className="text-xs text-slate-500">Authenticated via token bearer interceptor.</span>
          </div>

          <div className="flex items-center gap-3 w-full sm:w-auto">
            <Button
              variant="outline"
              size="sm"
              onClick={() => alert('Password change request dispatched.')}
            >
              Change Password
            </Button>
            <Button
              variant="danger"
              size="sm"
              onClick={() => { logout(); navigate('/') }}
              leftIcon={<LogOut className="w-4 h-4" />}
            >
              Log Out
            </Button>
          </div>
        </div>
      </Card>
    </div>
  )
}
