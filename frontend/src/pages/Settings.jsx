import { useAuth } from '../context/AuthContext'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import api from '../services/api'

export default function Settings() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleDeleteAllData = async () => {
    const confirmed = window.confirm(
      'This will delete all your resumes and analyses. This cannot be undone. Continue?'
    )
    if (!confirmed) return
    try {
      const resumesRes = await api.get('/resumes')
      const resumes = resumesRes.data.resumes || []
      await Promise.all(resumes.map(r => api.delete(`/resumes/${r.id}`)))
      toast.success('All your data has been deleted.')
      navigate('/dashboard')
    } catch { toast.error('Failed to delete data.') }
  }

  return (
    <div className="max-w-xl mx-auto space-y-6">
      <h2 className="text-xl font-bold text-slate-800">Settings</h2>

      <div className="card space-y-2">
        <h3 className="text-sm font-semibold text-slate-700">Account</h3>
        <p className="text-sm text-slate-500">Email: <span className="font-medium text-slate-700">{user?.email}</span></p>
        <p className="text-sm text-slate-500">Role: <span className="font-medium text-slate-700 capitalize">{user?.role}</span></p>
      </div>

      <div className="card space-y-3 border-red-100">
        <h3 className="text-sm font-semibold text-red-700">Danger Zone</h3>
        <p className="text-xs text-slate-500">Deleting your data removes all uploaded resumes and analysis records. Your account remains active.</p>
        <button className="btn-danger text-sm" onClick={handleDeleteAllData}>
          🗑️ Delete All My Data
        </button>
      </div>

      <div className="card space-y-2">
        <h3 className="text-sm font-semibold text-slate-700">About</h3>
        <p className="text-xs text-slate-500">CareerLens AI — Resume Analyzer & Job Recommendation System</p>
        <p className="text-xs text-slate-400">ATS scores are explainable estimates, not proprietary system scores. They do not predict hiring outcomes.</p>
      </div>
    </div>
  )
}
