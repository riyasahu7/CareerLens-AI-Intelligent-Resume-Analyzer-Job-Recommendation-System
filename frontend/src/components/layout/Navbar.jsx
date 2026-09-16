import { useLocation } from 'react-router-dom'

const titles = {
  '/dashboard':       'Dashboard',
  '/upload':          'Upload Resume',
  '/job-match':       'Job Match',
  '/recommendations': 'Recommendations',
  '/history':         'Analysis History',
  '/profile':         'Profile',
  '/settings':        'Settings',
  '/admin':           'Admin Dashboard',
}

export default function Navbar({ onMenuClick }) {
  const location = useLocation()
  const title = Object.entries(titles).find(([path]) =>
    location.pathname.startsWith(path)
  )?.[1] || 'CareerLens AI'

  return (
    <header className="bg-white border-b border-slate-100 px-4 md:px-8 py-4 flex items-center gap-4">
      <button
        className="md:hidden p-1.5 rounded-lg hover:bg-slate-100 transition-colors"
        onClick={onMenuClick}
        aria-label="Open menu"
      >
        <div className="w-5 h-0.5 bg-slate-600 mb-1 rounded" />
        <div className="w-5 h-0.5 bg-slate-600 mb-1 rounded" />
        <div className="w-5 h-0.5 bg-slate-600 rounded" />
      </button>
      <h1 className="text-lg font-semibold text-slate-800">{title}</h1>
    </header>
  )
}
