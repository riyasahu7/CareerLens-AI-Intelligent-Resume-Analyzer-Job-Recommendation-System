import { useEffect, useState } from 'react'
import { useLocation, Link } from 'react-router-dom'
import api from '../services/api'
import ScoreRing from '../components/ui/ScoreRing'
import Badge from '../components/ui/Badge'
import Skeleton from '../components/ui/Skeleton'
import EmptyState from '../components/ui/EmptyState'

export default function Recommendations() {
  const location = useLocation()
  const [rec, setRec]         = useState(location.state?.rec || null)
  const [loading, setLoading] = useState(!rec)
  const [expanded, setExpanded] = useState(null)

  useEffect(() => {
    if (!rec) {
      api.get('/recommendations').then(r => {
        const list = r.data.recommendations || []
        if (list.length) setRec(list[0])
      }).catch(() => {}).finally(() => setLoading(false))
    }
  }, [])

  if (loading) return (
    <div className="space-y-4">
      <Skeleton className="h-8 w-48" />
      <Skeleton className="h-32 w-full" count={3} />
    </div>
  )

  if (!rec) return (
    <EmptyState
      icon="💡"
      title="No recommendations yet"
      description="Run an analysis first, then click 'Get Recommendations' to see role matches."
      action={<Link to="/upload" className="btn-primary">Upload & Analyse</Link>}
    />
  )

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-800">Job Role Recommendations</h2>
        <p className="text-slate-500 text-sm mt-1">
          Scores are based on skill overlap — not a prediction of hiring outcome.
        </p>
      </div>

      {/* Roles */}
      <div className="space-y-4">
        {(rec.roles || []).map((role, i) => (
          <div key={role.role} className="card hover:shadow-md transition-shadow">
            <div
              className="flex items-center justify-between cursor-pointer"
              onClick={() => setExpanded(expanded === i ? null : i)}
            >
              <div className="flex items-center gap-4 flex-1 min-w-0">
                <ScoreRing score={role.match_score} size={72} label="" />
                <div className="min-w-0">
                  <p className="font-bold text-slate-800 text-base">{role.role}</p>
                  <p className="text-sm text-slate-500 truncate">{role.description}</p>
                  <div className="flex items-center gap-2 mt-1 flex-wrap">
                    <Badge variant={role.match_score >= 60 ? 'green' : role.match_score >= 30 ? 'yellow' : 'red'}>
                      {role.match_score}% match
                    </Badge>
                    {role.matched_required?.length > 0 && (
                      <span className="text-xs text-slate-400">{role.matched_required.length} required skills matched</span>
                    )}
                  </div>
                </div>
              </div>
              <span className="text-slate-400 text-lg ml-4">{expanded === i ? '▲' : '▼'}</span>
            </div>

            {expanded === i && (
              <div className="mt-4 pt-4 border-t border-slate-100 grid md:grid-cols-2 gap-4">
                <div>
                  <p className="text-xs font-semibold text-green-600 mb-2">✅ Matched Required Skills</p>
                  <div className="flex flex-wrap gap-1.5">
                    {role.matched_required?.length
                      ? role.matched_required.map(s => <Badge key={s} variant="green">{s}</Badge>)
                      : <p className="text-xs text-slate-400">None</p>}
                  </div>
                </div>
                <div>
                  <p className="text-xs font-semibold text-red-500 mb-2">❌ Missing Required Skills</p>
                  <div className="flex flex-wrap gap-1.5">
                    {role.missing_required?.length
                      ? role.missing_required.map(s => <Badge key={s} variant="red">{s}</Badge>)
                      : <p className="text-xs text-slate-400">None missing!</p>}
                  </div>
                </div>
                <div>
                  <p className="text-xs font-semibold text-blue-600 mb-2">⭐ Nice-to-Have Matched</p>
                  <div className="flex flex-wrap gap-1.5">
                    {role.matched_nice_to_have?.length
                      ? role.matched_nice_to_have.map(s => <Badge key={s} variant="blue">{s}</Badge>)
                      : <p className="text-xs text-slate-400">None</p>}
                  </div>
                </div>
                <div>
                  <p className="text-xs font-semibold text-slate-500 mb-2">📌 Nice-to-Have to Learn</p>
                  <div className="flex flex-wrap gap-1.5">
                    {role.missing_nice_to_have?.slice(0,6).map(s => <Badge key={s} variant="gray">{s}</Badge>)}
                  </div>
                </div>
                <div className="md:col-span-2">
                  <p className="text-xs text-slate-400 italic">{role.scoring_note}</p>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Skill Gap & Learning Plan */}
      {rec.learning_plan?.length > 0 && (
        <div className="card">
          <h3 className="text-base font-bold text-slate-800 mb-1">Personalised Learning Plan</h3>
          <p className="text-xs text-slate-400 mb-5">
            Based on your top missing skills. Study hours are estimates only.
          </p>
          <div className="space-y-4">
            {rec.learning_plan.map(item => (
              <details key={item.skill} className="group border border-slate-100 rounded-xl overflow-hidden">
                <summary className="flex items-center justify-between px-4 py-3 cursor-pointer bg-slate-50 hover:bg-slate-100 transition-colors list-none">
                  <div className="flex items-center gap-3">
                    <Badge variant={item.priority === 'high' ? 'red' : item.priority === 'medium' ? 'yellow' : 'gray'}>
                      {item.priority}
                    </Badge>
                    <span className="font-semibold text-slate-800 text-sm">{item.skill}</span>
                    <span className="text-xs text-slate-400">{item.category}</span>
                  </div>
                  <span className="text-slate-400 group-open:rotate-180 transition-transform">▼</span>
                </summary>
                <div className="px-4 py-4 space-y-3 text-sm">
                  <p className="text-slate-600">{item.beginner_explanation}</p>
                  {item.topics_to_learn?.length > 0 && (
                    <div>
                      <p className="font-semibold text-slate-700 mb-1">Topics to Learn</p>
                      <ul className="list-disc list-inside text-slate-600 space-y-0.5">
                        {item.topics_to_learn.map(t => <li key={t}>{t}</li>)}
                      </ul>
                    </div>
                  )}
                  <div className="grid md:grid-cols-2 gap-3">
                    <div className="bg-blue-50 rounded-xl p-3">
                      <p className="font-semibold text-blue-800 text-xs mb-1">🛠️ Practice Task</p>
                      <p className="text-blue-700 text-xs">{item.practice_task}</p>
                    </div>
                    <div className="bg-purple-50 rounded-xl p-3">
                      <p className="font-semibold text-purple-800 text-xs mb-1">🚀 Mini Project</p>
                      <p className="text-purple-700 text-xs">{item.mini_project}</p>
                    </div>
                  </div>
                  {item.estimated_hours && (
                    <p className="text-xs text-slate-400 italic">⏱ {item.estimated_hours}</p>
                  )}
                </div>
              </details>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
