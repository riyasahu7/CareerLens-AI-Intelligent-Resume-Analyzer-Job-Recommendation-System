import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api'
import Badge from '../components/ui/Badge'
import Skeleton from '../components/ui/Skeleton'
import EmptyState from '../components/ui/EmptyState'
import toast from 'react-hot-toast'

export default function History() {
  const [items, setItems]   = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/analysis/history')
      .then(r => setItems(r.data.history || []))
      .catch(() => toast.error('Failed to load history.'))
      .finally(() => setLoading(false))
  }, [])

  const handleDelete = async id => {
    if (!window.confirm('Delete this analysis? This cannot be undone.')) return
    try {
      await api.delete(`/analysis/${id}`)
      setItems(p => p.filter(i => i.id !== id))
      toast.success('Analysis deleted.')
    } catch { toast.error('Delete failed.') }
  }

  if (loading) return (
    <div className="space-y-3">
      <Skeleton className="h-20 w-full" count={5} />
    </div>
  )

  if (!items.length) return (
    <EmptyState
      icon="🕐"
      title="No analysis history"
      description="Upload and analyse your first resume to see results here."
      action={<Link to="/upload" className="btn-primary">Upload Resume</Link>}
    />
  )

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-slate-800">Analysis History</h2>
        <span className="text-sm text-slate-400">{items.length} record{items.length !== 1 ? 's' : ''}</span>
      </div>

      <div className="space-y-3">
        {items.map(item => {
          const score = item.ats_result?.overall_score ?? null
          const grade = item.ats_result?.grade ?? '?'
          const badgeVariant = score >= 70 ? 'green' : score >= 45 ? 'yellow' : 'red'

          return (
            <div key={item.id} className="card flex items-center justify-between gap-4 flex-wrap hover:shadow-sm transition-shadow">
              <div className="flex items-center gap-3 min-w-0 flex-1">
                <div className="w-10 h-10 bg-brand-100 rounded-xl flex items-center justify-center text-brand-600 flex-shrink-0 text-lg">📄</div>
                <div className="min-w-0">
                  <p className="font-semibold text-slate-800 truncate text-sm">{item.resume_filename || 'Resume'}</p>
                  <p className="text-xs text-slate-400">{new Date(item.created_at).toLocaleString()}</p>
                  <div className="flex flex-wrap gap-1.5 mt-1">
                    {score !== null && <Badge variant={badgeVariant}>Score: {score} / 100 · Grade {grade}</Badge>}
                    {item.job_description_provided && <Badge variant="purple">Job Match</Badge>}
                    {item.skills?.length > 0 && <Badge variant="blue">{item.skills.length} skills</Badge>}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2 flex-shrink-0">
                <Link to={`/analysis/${item.id}`} className="btn-secondary text-xs px-3 py-1.5">View</Link>
                <button
                  onClick={() => handleDelete(item.id)}
                  className="btn-danger text-xs px-3 py-1.5"
                >Delete</button>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
