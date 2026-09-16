import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'
import toast from 'react-hot-toast'

export default function Profile() {
  const { user, refreshUser } = useAuth()
  const [name, setName]         = useState(user?.full_name || '')
  const [saving, setSaving]     = useState(false)
  const [pwForm, setPwForm]     = useState({ current_password: '', new_password: '', confirm: '' })
  const [pwSaving, setPwSaving] = useState(false)

  const handleSaveName = async e => {
    e.preventDefault()
    if (!name.trim()) { toast.error('Name cannot be empty.'); return }
    setSaving(true)
    try {
      await api.put('/auth/profile', { full_name: name })
      await refreshUser()
      toast.success('Profile updated.')
    } catch (err) { toast.error(err.response?.data?.error || 'Update failed.') }
    finally { setSaving(false) }
  }

  const handlePwChange = async e => {
    e.preventDefault()
    if (pwForm.new_password !== pwForm.confirm) { toast.error('Passwords do not match.'); return }
    setPwSaving(true)
    try {
      await api.put('/auth/change-password', {
        current_password: pwForm.current_password,
        new_password: pwForm.new_password,
      })
      toast.success('Password changed successfully.')
      setPwForm({ current_password: '', new_password: '', confirm: '' })
    } catch (err) { toast.error(err.response?.data?.error || 'Password change failed.') }
    finally { setPwSaving(false) }
  }

  return (
    <div className="max-w-xl mx-auto space-y-6">
      <h2 className="text-xl font-bold text-slate-800">Your Profile</h2>

      {/* Info */}
      <div className="card flex items-center gap-4">
        <div className="w-16 h-16 bg-brand-600 rounded-2xl flex items-center justify-center text-white text-2xl font-bold flex-shrink-0">
          {user?.full_name?.[0]?.toUpperCase()}
        </div>
        <div>
          <p className="font-bold text-slate-800 text-lg">{user?.full_name}</p>
          <p className="text-slate-500 text-sm">{user?.email}</p>
          <p className="text-xs text-slate-400 mt-0.5">Member since {user?.created_at ? new Date(user.created_at).toLocaleDateString() : '—'}</p>
        </div>
      </div>

      {/* Edit Name */}
      <form onSubmit={handleSaveName} className="card space-y-4">
        <h3 className="text-sm font-semibold text-slate-700">Edit Name</h3>
        <div>
          <label className="label">Full Name</label>
          <input className="input" value={name} onChange={e => setName(e.target.value)} />
        </div>
        <button className="btn-primary" type="submit" disabled={saving}>
          {saving ? 'Saving…' : 'Save Name'}
        </button>
      </form>

      {/* Change Password */}
      <form onSubmit={handlePwChange} className="card space-y-4">
        <h3 className="text-sm font-semibold text-slate-700">Change Password</h3>
        {['current_password', 'new_password', 'confirm'].map(field => (
          <div key={field}>
            <label className="label">{field === 'current_password' ? 'Current Password' : field === 'new_password' ? 'New Password' : 'Confirm New Password'}</label>
            <input
              className="input" type="password"
              value={pwForm[field]}
              onChange={e => setPwForm(p => ({ ...p, [field]: e.target.value }))}
              placeholder="••••••••"
            />
          </div>
        ))}
        <button className="btn-primary" type="submit" disabled={pwSaving}>
          {pwSaving ? 'Changing…' : 'Change Password'}
        </button>
      </form>
    </div>
  )
}
