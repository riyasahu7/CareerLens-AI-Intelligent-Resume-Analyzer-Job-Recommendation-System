import { NavLink } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import clsx from 'clsx'

const navItems = [
  { to: '/dashboard',       label: 'Dashboard',        icon: '🏠' },
  { to: '/upload',          label: 'Upload Resume',     icon: '📄' },
  { to: '/job-match',       label: 'Job Match',         icon: '🎯' },
  { to: '/recommendations', label: 'Recommendations',   icon: '💡' },
  { to: '/history',         label: 'History',           icon: '🕐' },
  { to: '/profile',         label: 'Profile',           icon: '👤' },
  { to: '/settings',        label: 'Settings',          icon: '⚙️' },
]

export default function Sidebar({ open, onClose }) {
  const { user, logout } = useAuth()

  return (
    <>
      {/* Mobile overlay */}
      {open && (
        <div
          className="fixed inset-0 bg-black/40 z-20 md:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={clsx(
          'fixed md:static inset-y-0 left-0 z-30 w-64 bg-brand-900 text-white flex flex-col transition-transform duration-300',
          open ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        )}
      >
        {/* Logo */}
        <div className="flex items-center gap-2.5 px-6 py-5 border-b border-brand-800">
          <div className="w-8 h-8 bg-brand-400 rounded-lg flex items-center justify-center text-brand-900 font-bold text-sm">CL</div>
          <div>
            <p className="font-bold text-sm leading-tight">CareerLens AI</p>
            <p className="text-brand-300 text-xs">Resume Analyzer</p>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {navItems.map(item => (
            <NavLink
              key={item.to}
              to={item.to}
              onClick={onClose}
              className={({ isActive }) =>
                clsx(
                  'flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all',
                  isActive
                    ? 'bg-brand-700 text-white'
                    : 'text-brand-200 hover:bg-brand-800 hover:text-white'
                )
              }
            >
              <span className="text-base">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
          {user?.role === 'admin' && (
            <NavLink
              to="/admin"
              onClick={onClose}
              className={({ isActive }) =>
                clsx(
                  'flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all',
                  isActive ? 'bg-brand-700 text-white' : 'text-brand-200 hover:bg-brand-800 hover:text-white'
                )
              }
            >
              <span>🛡️</span> Admin
            </NavLink>
          )}
        </nav>

        {/* User */}
        <div className="px-4 py-4 border-t border-brand-800">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-8 h-8 bg-brand-600 rounded-full flex items-center justify-center text-sm font-bold">
              {user?.full_name?.[0]?.toUpperCase() || '?'}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{user?.full_name}</p>
              <p className="text-brand-300 text-xs truncate">{user?.email}</p>
            </div>
          </div>
          <button
            onClick={logout}
            className="w-full text-left text-xs text-brand-300 hover:text-white px-2 py-1.5 rounded-lg hover:bg-brand-800 transition-all"
          >
            Sign out →
          </button>
        </div>
      </aside>
    </>
  )
}
