import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Menu, PanelLeftClose, PanelLeft, Upload, ShieldCheck } from 'lucide-react'
import { useAuth } from '../../context/AuthContext'
import { USE_MOCK_API } from '../../services/api'
import { Badge } from '../ui/Badge'

interface HeaderProps {
  onToggleSidebar?: () => void
  onOpenMobileNav?: () => void
  sidebarCollapsed?: boolean
}

export const Header: React.FC<HeaderProps> = ({
  onToggleSidebar,
  onOpenMobileNav,
  sidebarCollapsed,
}) => {
  const { user } = useAuth()
  const location = useLocation()

  // Map route to clean title
  const getPageTitle = (pathname: string) => {
    if (pathname.startsWith('/reports/upload')) return 'Upload Medical Report'
    if (pathname.includes('/analysis')) return 'AI-Assisted Report Explanation'
    if (pathname.startsWith('/reports')) return 'Medical Reports'
    if (pathname.startsWith('/health-records')) return 'Health Records & Trends'
    if (pathname.startsWith('/appointments')) return 'Appointments'
    if (pathname.startsWith('/reminders')) return 'Healthcare Reminders'
    if (pathname.startsWith('/settings')) return 'Profile & Settings'
    return 'Patient Dashboard'
  }

  return (
    <header className="h-16 bg-white border-b border-slate-200/80 px-4 sm:px-6 flex items-center justify-between sticky top-0 z-20">
      <div className="flex items-center gap-3">
        {/* Mobile menu button */}
        <button
          onClick={onOpenMobileNav}
          className="lg:hidden p-2 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors"
          aria-label="Open mobile navigation"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Desktop sidebar toggle button */}
        <button
          onClick={onToggleSidebar}
          className="hidden lg:flex p-2 rounded-xl text-slate-500 hover:text-slate-900 hover:bg-slate-100 transition-colors"
          aria-label={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {sidebarCollapsed ? <PanelLeft className="w-5 h-5" /> : <PanelLeftClose className="w-5 h-5" />}
        </button>

        {/* Dynamic Page Title */}
        <div className="flex flex-col">
          <h1 className="text-base sm:text-lg font-bold text-slate-900 tracking-tight leading-snug">
            {getPageTitle(location.pathname)}
          </h1>
        </div>
      </div>

      {/* Right controls */}
      <div className="flex items-center gap-3">

        {/* Quick Upload action */}
        {!location.pathname.startsWith('/reports/upload') && (
          <Link
            to="/reports/upload"
            className="hidden md:inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-sky-700 bg-sky-50 hover:bg-sky-100 border border-sky-200/80 rounded-xl transition-colors shadow-2xs"
          >
            <Upload className="w-3.5 h-3.5" />
            <span>Upload</span>
          </Link>
        )}

        {/* User avatar / profile button */}
        <Link
          to="/settings"
          className="flex items-center gap-2 p-1 rounded-full hover:ring-2 hover:ring-sky-500/20 transition-all"
          title="Account settings"
        >
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-sky-600 to-teal-500 text-white font-bold text-xs flex items-center justify-center shadow-xs">
            {user?.fullName ? user.fullName.charAt(0).toUpperCase() : 'U'}
          </div>
        </Link>
      </div>
    </header>
  )
}
