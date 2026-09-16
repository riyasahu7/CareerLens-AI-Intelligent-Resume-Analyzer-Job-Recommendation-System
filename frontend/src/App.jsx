import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import AppLayout from './components/layout/AppLayout'

import Landing      from './pages/Landing'
import Login        from './pages/Login'
import Register     from './pages/Register'
import Dashboard    from './pages/Dashboard'
import Upload       from './pages/Upload'
import Analysis     from './pages/Analysis'
import JobMatch     from './pages/JobMatch'
import Recommendations from './pages/Recommendations'
import History      from './pages/History'
import Profile      from './pages/Profile'
import Settings     from './pages/Settings'
import Admin        from './pages/Admin'
import NotFound     from './pages/NotFound'

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        {/* Public */}
        <Route path="/"         element={<Landing />} />
        <Route path="/login"    element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Protected — inside shared layout */}
        <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
          <Route path="/dashboard"       element={<Dashboard />} />
          <Route path="/upload"          element={<Upload />} />
          <Route path="/analysis/:id"    element={<Analysis />} />
          <Route path="/job-match"       element={<JobMatch />} />
          <Route path="/recommendations" element={<Recommendations />} />
          <Route path="/history"         element={<History />} />
          <Route path="/profile"         element={<Profile />} />
          <Route path="/settings"        element={<Settings />} />
          <Route path="/admin"           element={<Admin />} />
        </Route>

        <Route path="*" element={<NotFound />} />
      </Routes>
    </AuthProvider>
  )
}
