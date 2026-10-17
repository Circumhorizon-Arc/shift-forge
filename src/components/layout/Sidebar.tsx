import React from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard,
  FileText,
  Activity,
  Calendar,
  BellRing,
  Settings,
  LogOut,
  Upload,
  HeartPulse,
} from 'lucide-react'
import { useAuth } from '../../context/AuthContext'
import { cn } from '../../utils/cn'

interface SidebarProps {
  collapsed?: boolean
  onToggleCollapse?: () => void
  onItemClick?: () => void
}

export const Sidebar: React.FC<SidebarProps> = ({ collapsed = false, onItemClick }) => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Medical Reports', path: '/reports', icon: FileText },
    { name: 'Health Records', path: '/health-records', icon: Activity },
    { name: 'Appointments', path: '/appointments', icon: Calendar },
    { name: 'Reminders', path: '/reminders', icon: BellRing },
  ]

  return (
    <aside
      className={cn(
        'h-screen bg-white border-r border-slate-200/90 flex flex-col justify-between transition-all duration-300 z-30 select-none',
        collapsed ? 'w-20' : 'w-64'
      )}
    >
      {/* Top Header / Logo */}
      <div>
        <div className="h-16 flex items-center px-6 border-b border-slate-100">
          <NavLink to="/dashboard" className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-sky-600 to-teal-500 flex items-center justify-center text-white shadow-sm flex-shrink-0">
              <HeartPulse className="w-5 h-5" />
            </div>
            {!collapsed && (
              <div className="flex flex-col">
                <span className="font-bold text-base tracking-tight text-slate-900 leading-none">
                  Health<span className="text-sky-600">Sense</span>
                </span>
                <span className="text-[10px] text-slate-600 font-bold uppercase tracking-wider mt-0.5">
                  Clinical AI Platform
                </span>
              </div>
            )}
          </NavLink>
        </div>

        {/* Action Button: Upload */}
        <div className="p-4">
          <NavLink
            to="/reports/upload"
            onClick={onItemClick}
            className={cn(
              'flex items-center justify-center gap-2 w-full py-2.5 px-3 rounded-xl bg-sky-600 hover:bg-sky-700 active:bg-sky-800 text-white font-medium text-sm shadow-sm transition-all duration-150',
              collapsed && 'px-0 justify-center'
            )}
            title="Upload Medical Report"
          >
            <Upload className="w-4 h-4 flex-shrink-0" />
            {!collapsed && <span>Upload Report</span>}
          </NavLink>
        </div>

        {/* Navigation items */}
        <nav className="px-3 space-y-1 mt-1">
          {navItems.map((item) => {
            const Icon = item.icon
            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={onItemClick}
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors duration-150',
                    isActive
                      ? 'bg-sky-50 text-sky-700 font-semibold border border-sky-100/80 shadow-xs'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50',
                    collapsed && 'justify-center px-0'
                  )
                }
                title={collapsed ? item.name : undefined}
              >
                <Icon className="w-4 h-4 flex-shrink-0" />
                {!collapsed && <span>{item.name}</span>}
              </NavLink>
            )
          })}
        </nav>
      </div>

      {/* Bottom Profile / Settings */}
      <div className="p-3 border-t border-slate-100 space-y-1">
        <NavLink
          to="/settings"
          onClick={onItemClick}
          className={({ isActive }) =>
            cn(
              'flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors duration-150',
              isActive
                ? 'bg-sky-50 text-sky-700 font-semibold'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50',
              collapsed && 'justify-center px-0'
            )
          }
          title={collapsed ? 'Settings' : undefined}
        >
          <Settings className="w-4 h-4 flex-shrink-0" />
          {!collapsed && <span>Settings</span>}
        </NavLink>

        <button
          onClick={() => {
            logout()
            navigate('/')
            if (onItemClick) onItemClick()
          }}
          className={cn(
            'flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-sm font-medium text-slate-600 hover:text-rose-600 hover:bg-rose-50 transition-colors duration-150',
            collapsed && 'justify-center px-0'
          )}
          title={collapsed ? 'Log out' : undefined}
        >
          <LogOut className="w-4 h-4 flex-shrink-0" />
          {!collapsed && <span>Log Out</span>}
        </button>

        {!collapsed && user && (
          <div className="mt-3 pt-3 border-t border-slate-100 flex items-center gap-3 px-2">
            <div className="w-8 h-8 rounded-full bg-sky-100 text-sky-800 font-bold text-xs flex items-center justify-center flex-shrink-0">
              {user.fullName ? user.fullName.charAt(0).toUpperCase() : 'U'}
            </div>
            <div className="flex flex-col min-w-0">
              <span className="text-xs font-semibold text-slate-900 truncate leading-tight">
                {user.fullName || 'Patient User'}
              </span>
              <span className="text-[11px] text-slate-400 truncate leading-tight mt-0.5">
                {user.email}
              </span>
            </div>
          </div>
        )}
      </div>
    </aside>
  )
}
