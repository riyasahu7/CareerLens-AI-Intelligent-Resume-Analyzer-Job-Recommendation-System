import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'
import StatCard from '../components/ui/StatCard'
import Skeleton from '../components/ui/Skeleton'
import EmptyState from '../components/ui/EmptyState'
import Badge from '../components/ui/Badge'

export default function Dashboard() {
  const { user } = useAuth()
  const [history, setHistory]     = useState([])
  const [resumes, setResumes]     = useState([])
  const [loading, setLoading]     = useState(true)

  useEffect(() => {
    Promise.all([
      api.get('/analysis/history'),
      api.get('/resumes'),
    ]).then(([h, r]) => {
      setHistory(h.data.history || [])
      setResumes(r.data.resumes || [])
    }).catch(() => {}).finally(() => setLoading(false))
  }, [])

  const avgScore = history.length
    ? Math.round(history.reduce((s, h) => s + (h.ats_result?.overall_score || 0), 0) / history.length)
    : 0

  // Skills frequency across all analyses
  const skillFreq = {}
  history.forEach(h => (h.skills || []).forEach(s => { skillFreq[s] = (skillFreq[s] || 0) + 1 }))
  const topSkills = Object.entries(skillFreq).sort((a, b) => b[1] - a[1]).slice(0, 8)
    .map(([name, count]) => ({ name, count }))

  // Score trend
  const scoreTrend = [...history].reverse().slice(-7).map(h => ({
    name: new Date(h.created_at).toLocaleDateString('en', { month: 'short', day: 'numeric' }),
    score: h.ats_result?.overall_score || 0,
  }))

  return (
    <div className="space-y-6">
      {/* Welcome */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h2 className="text-xl font-bold text-slate-800">
            Welcome back, {user?.full_name?.split(' ')[0]} 👋
          </h2>
          <p className="text-slate-500 text-sm mt-0.5">Here's your career progress overview.</p>
        </div>
        <Link to="/upload" className="btn-primary">+ Upload Resume</Link>
      </div>

      {/* Stats */}
      {loading ? (
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-24 w-full" />)}
        </div>
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard icon="📄" label="Resumes Uploaded"     value={resumes.length}  color="brand"  />
          <StatCard icon="🔬" label="Analyses Run"          value={history.length}  color="purple" />
          <StatCard icon="⭐" label="Avg ATS Score"          value={avgScore || '—'} color="green"
            sub={avgScore ? 'Based on section & skill coverage' : 'Upload a resume to start'} />
          <StatCard icon="🎯" label="Latest Score"
            value={history[0]?.ats_result?.overall_score ?? '—'}
            color="yellow"
            sub={history[0] ? `Grade ${history[0].ats_result?.grade}` : 'No analysis yet'} />
        </div>
      )}

      {/* Charts */}
      {history.length > 0 && (
        <div className="grid lg:grid-cols-2 gap-6">
          <div className="card">
            <h3 className="text-sm font-semibold text-slate-700 mb-4">ATS Score Trend</h3>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={scoreTrend} barSize={32}>
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
                <Tooltip formatter={v => [`${v}`, 'Score']} />
                <Bar dataKey="score" fill="#6366f1" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {topSkills.length > 0 && (
            <div className="card">
              <h3 className="text-sm font-semibold text-slate-700 mb-4">Top Skills Detected</h3>
              <ResponsiveContainer width="100%" height={200}>
                <RadarChart data={topSkills}>
                  <PolarGrid stroke="#e2e8f0" />
                  <PolarAngleAxis dataKey="name" tick={{ fontSize: 10 }} />
                  <Radar dataKey="count" fill="#6366f1" fillOpacity={0.5} stroke="#6366f1" />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}

      {/* Recent History */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-slate-700">Recent Analyses</h3>
          <Link to="/history" className="text-xs text-brand-600 hover:underline font-medium">View all</Link>
        </div>
        {loading ? <Skeleton className="h-14 w-full" count={3} /> : (
          history.length === 0 ? (
            <EmptyState
              icon="🔬"
              title="No analyses yet"
              description="Upload your first resume to see analysis results here."
              action={<Link to="/upload" className="btn-primary text-sm">Upload Resume</Link>}
            />
          ) : (
            <div className="space-y-3">
              {history.slice(0, 5).map(h => (
                <Link key={h.id} to={`/analysis/${h.id}`}
                  className="flex items-center justify-between p-3 rounded-xl hover:bg-slate-50 transition-colors border border-transparent hover:border-slate-100">
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="w-8 h-8 bg-brand-100 rounded-lg flex items-center justify-center text-brand-600 text-sm flex-shrink-0">📄</div>
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-slate-700 truncate">{h.resume_filename || 'Resume'}</p>
                      <p className="text-xs text-slate-400">{new Date(h.created_at).toLocaleDateString()}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0 ml-2">
                    <Badge variant={h.ats_result?.overall_score >= 70 ? 'green' : h.ats_result?.overall_score >= 45 ? 'yellow' : 'red'}>
                      {h.ats_result?.overall_score ?? '?'} / 100
                    </Badge>
                    <span className="text-xs font-bold text-slate-500">{h.ats_result?.grade}</span>
                  </div>
                </Link>
              ))}
            </div>
          )
        )}
      </div>
    </div>
  )
}
