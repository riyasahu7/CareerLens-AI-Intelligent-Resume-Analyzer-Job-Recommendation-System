import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { Navigate } from 'react-router-dom'
import api from '../services/api'
import StatCard from '../components/ui/StatCard'
import Skeleton from '../components/ui/Skeleton'

export default function Admin() {
  const { user } = useAuth()
  const [stats, setStats] = useState(null)
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)

  if (user?.role !== 'admin') return <Navigate to="/dashboard" replace />

  useEffect(() => {
    Promise.all([api.get('/admin/stats'), api.get('/admin/users')])
      .then(([s, u]) => { setStats(s.data); setUsers(u.data.users || []) })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="space-y-4"><Skeleton className="h-24 w-full" count={4} /></div>

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-slate-800">Admin Dashboard</h2>

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon="👥" label="Total Users"      value={stats?.users ?? 0}         color="brand" />
        <StatCard icon="🔬" label="Total Analyses"   value={stats?.analyses ?? 0}      color="purple" />
        <StatCard icon="📄" label="Total Resumes"    value={stats?.resumes ?? 0}       color="green" />
        <StatCard icon="💡" label="Recommendations" value={stats?.recommendations ?? 0} color="yellow" />
      </div>

      <div className="card overflow-x-auto">
        <h3 className="text-sm font-semibold text-slate-700 mb-4">All Users</h3>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs text-slate-500 border-b border-slate-100">
              <th className="pb-2 pr-4 font-medium">Name</th>
              <th className="pb-2 pr-4 font-medium">Email</th>
              <th className="pb-2 pr-4 font-medium">Role</th>
              <th className="pb-2 font-medium">Joined</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {users.map(u => (
              <tr key={u.id} className="hover:bg-slate-50">
                <td className="py-2.5 pr-4 font-medium text-slate-800">{u.full_name}</td>
                <td className="py-2.5 pr-4 text-slate-600">{u.email}</td>
                <td className="py-2.5 pr-4">
                  <span className={`badge ${u.role === 'admin' ? 'bg-purple-100 text-purple-700' : 'bg-slate-100 text-slate-600'}`}>
                    {u.role}
                  </span>
                </td>
                <td className="py-2.5 text-slate-400 text-xs">{u.created_at ? new Date(u.created_at).toLocaleDateString() : '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
