import { useEffect, useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import api from '../services/api'
import ScoreRing from '../components/ui/ScoreRing'
import Badge from '../components/ui/Badge'
import Skeleton from '../components/ui/Skeleton'
import toast from 'react-hot-toast'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

export default function Analysis() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [data, setData]     = useState(null)
  const [catData, setCatData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [genRec, setGenRec]  = useState(false)

  useEffect(() => {
    api.get(`/analysis/${id}`)
      .then(r => { setData(r.data.analysis); setCatData(r.data.skills_by_category) })
      .catch(() => toast.error('Analysis not found.'))
      .finally(() => setLoading(false))
  }, [id])

  const handleGenRecommendations = async () => {
    setGenRec(true)
    try {
      const r = await api.post('/recommendations', { analysis_id: id })
      navigate('/recommendations', { state: { rec: r.data.recommendation } })
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to generate recommendations.')
    } finally { setGenRec(false) }
  }

  if (loading) return (
    <div className="space-y-4">
      <Skeleton className="h-8 w-48" />
      <Skeleton className="h-40 w-full" />
      <Skeleton className="h-40 w-full" />
    </div>
  )
  if (!data) return (
    <div className="card text-center py-16">
      <p className="text-slate-500">Analysis not found.</p>
      <Link to="/history" className="btn-primary mt-4 inline-flex">Back to History</Link>
    </div>
  )

  const ats = data.ats_result || {}
  const catScores = Object.entries(ats.category_scores || {}).map(([k, v]) => ({
    name: k.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
    score: v,
  }))

  const sections = data.sections || {}
  const sectionEntries = Object.entries(sections)

  const feedback = data.llm_feedback || {}
  const suggestions = ats.suggestions || []

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold text-slate-800">Resume Analysis</h2>
          <p className="text-xs text-slate-400 mt-0.5">{data.resume_filename} · {new Date(data.created_at).toLocaleString()}</p>
        </div>
        <div className="flex gap-2 flex-wrap">
          <Link to="/upload" className="btn-secondary text-sm">+ New Analysis</Link>
          <button className="btn-primary text-sm" onClick={handleGenRecommendations} disabled={genRec}>
            {genRec ? 'Generating…' : '💡 Get Recommendations'}
          </button>
        </div>
      </div>

      {/* Score + Category Breakdown */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="card flex flex-col items-center justify-center gap-4 py-8">
          <ScoreRing score={ats.overall_score ?? 0} size={140} label="ATS Score" />
          <div className="text-center">
            <p className="text-3xl font-extrabold text-slate-800">Grade {ats.grade}</p>
            <p className="text-xs text-slate-400 mt-1 max-w-xs">{ats.score_explanation}</p>
          </div>
        </div>

        <div className="card">
          <h3 className="text-sm font-semibold text-slate-700 mb-4">Score Breakdown</h3>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={catScores} layout="vertical" barSize={12}>
              <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 10 }} />
              <YAxis type="category" dataKey="name" width={140} tick={{ fontSize: 10 }} />
              <Tooltip formatter={v => [`${v}`, 'Score']} />
              <Bar dataKey="score" fill="#6366f1" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Sections */}
      <div className="card">
        <h3 className="text-sm font-semibold text-slate-700 mb-4">Resume Sections Detected</h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {sectionEntries.map(([sec, found]) => (
            <div key={sec} className={`rounded-xl px-3 py-2.5 text-sm font-medium flex items-center gap-2 ${found ? 'bg-green-50 text-green-700' : 'bg-slate-50 text-slate-400'}`}>
              <span>{found ? '✅' : '❌'}</span>
              <span className="capitalize">{sec}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Skills */}
      <div className="card">
        <h3 className="text-sm font-semibold text-slate-700 mb-3">Detected Skills ({data.skills?.length || 0})</h3>
        {data.skills?.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {data.skills.map(s => (
              <Badge key={s} variant="blue">{s}</Badge>
            ))}
          </div>
        ) : <p className="text-sm text-slate-400">No skills detected in this resume text.</p>}
        <p className="text-xs text-slate-400 mt-3">Skills shown are those explicitly found in your resume text — nothing is inferred.</p>
      </div>

      {/* Job Match */}
      {data.job_match_result && (
        <div className="card">
          <h3 className="text-sm font-semibold text-slate-700 mb-4">Job Description Match</h3>
          <div className="flex items-center gap-4 mb-4">
            <ScoreRing score={data.job_match_result.tfidf_score ?? 0} size={90} label="TF-IDF Match" />
            <p className="text-xs text-slate-500 max-w-xs">{data.job_match_result.note}</p>
          </div>
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <p className="text-xs font-semibold text-green-600 mb-2">✅ Matched Keywords</p>
              <div className="flex flex-wrap gap-1.5">
                {data.job_match_result.matched_keywords?.map(k => <Badge key={k} variant="green">{k}</Badge>)}
                {!data.job_match_result.matched_keywords?.length && <p className="text-xs text-slate-400">None matched</p>}
              </div>
            </div>
            <div>
              <p className="text-xs font-semibold text-red-500 mb-2">❌ Missing Keywords</p>
              <div className="flex flex-wrap gap-1.5">
                {data.job_match_result.missing_keywords?.map(k => <Badge key={k} variant="red">{k}</Badge>)}
                {!data.job_match_result.missing_keywords?.length && <p className="text-xs text-slate-400">None missing</p>}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Suggestions */}
      {suggestions.length > 0 && (
        <div className="card">
          <h3 className="text-sm font-semibold text-slate-700 mb-3">Improvement Suggestions</h3>
          <div className="space-y-2.5">
            {suggestions.map((s, i) => (
              <div key={i} className={`rounded-xl px-4 py-3 text-sm flex items-start gap-3 ${s.priority === 'high' ? 'bg-red-50 border border-red-100' : s.priority === 'medium' ? 'bg-yellow-50 border border-yellow-100' : 'bg-slate-50 border border-slate-100'}`}>
                <span className="mt-0.5 flex-shrink-0">{s.priority === 'high' ? '🔴' : s.priority === 'medium' ? '🟡' : '⚪'}</span>
                <div>
                  <span className="font-medium capitalize">{s.type}</span> — {s.message}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* LLM / Rule-based Feedback */}
      {feedback?.suggestions?.length > 0 && (
        <div className="card">
          <div className="flex items-center gap-2 mb-3">
            <h3 className="text-sm font-semibold text-slate-700">Resume Feedback</h3>
            <Badge variant={feedback.source === 'llm' ? 'purple' : 'gray'}>
              {feedback.source === 'llm' ? 'AI-generated' : 'Rule-based'}
            </Badge>
          </div>
          {feedback.overall_impression && (
            <p className="text-sm text-slate-600 mb-3 bg-slate-50 rounded-xl p-3">{feedback.overall_impression}</p>
          )}
          <div className="space-y-2.5">
            {feedback.suggestions.map((s, i) => (
              <div key={i} className="bg-blue-50 border border-blue-100 rounded-xl px-4 py-3 text-sm">
                <p className="font-semibold text-blue-800">{s.section} — {s.issue}</p>
                <p className="text-blue-700 mt-0.5">{s.recommendation}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
