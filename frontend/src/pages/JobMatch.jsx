import { useEffect, useState } from 'react'
import api from '../services/api'
import ScoreRing from '../components/ui/ScoreRing'
import Badge from '../components/ui/Badge'
import toast from 'react-hot-toast'

export default function JobMatch() {
  const [resumes, setResumes]   = useState([])
  const [resumeId, setResumeId] = useState('')
  const [jobDesc, setJobDesc]   = useState('')
  const [result, setResult]     = useState(null)
  const [loading, setLoading]   = useState(false)

  useEffect(() => {
    api.get('/resumes').then(r => {
      const list = r.data.resumes || []
      setResumes(list)
      if (list.length) setResumeId(list[0].id)
    }).catch(() => {})
  }, [])

  const handleSubmit = async e => {
    e.preventDefault()
    if (!resumeId) { toast.error('Select a resume first.'); return }
    if (!jobDesc.trim()) { toast.error('Paste a job description.'); return }
    setLoading(true); setResult(null)
    try {
      const r = await api.post('/analysis/job-match', { resume_id: resumeId, job_description: jobDesc })
      setResult(r.data)
    } catch (err) {
      toast.error(err.response?.data?.error || 'Match failed.')
    } finally { setLoading(false) }
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-800">Job Description Matching</h2>
        <p className="text-slate-500 text-sm mt-1">
          Select a resume, paste a job description, and see TF-IDF keyword similarity plus skill alignment.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="card space-y-4">
        <div>
          <label className="label">Select Resume</label>
          {resumes.length === 0
            ? <p className="text-sm text-slate-400">No resumes yet. <a href="/upload" className="text-brand-600 underline">Upload one</a>.</p>
            : <select className="input" value={resumeId} onChange={e => setResumeId(e.target.value)}>
                {resumes.map(r => (
                  <option key={r.id} value={r.id}>{r.original_filename}</option>
                ))}
              </select>
          }
        </div>
        <div>
          <label className="label">Job Description</label>
          <textarea className="input resize-none" rows={8}
            placeholder="Paste the full job description here…"
            value={jobDesc} onChange={e => setJobDesc(e.target.value)} />
        </div>
        <button className="btn-primary w-full" type="submit" disabled={loading || !resumes.length}>
          {loading ? 'Matching…' : '🎯 Run Job Match'}
        </button>
      </form>

      {result && (
        <div className="space-y-6">
          {/* TF-IDF Score */}
          <div className="card flex flex-col sm:flex-row items-center gap-6">
            <ScoreRing score={result.tfidf_similarity?.score ?? 0} size={120} label="TF-IDF Similarity" />
            <div>
              <h3 className="font-semibold text-slate-800 mb-1">Textual Similarity Score</h3>
              <p className="text-sm text-slate-500 max-w-sm">{result.tfidf_similarity?.note}</p>
            </div>
          </div>

          {/* Skill Alignment */}
          <div className="card">
            <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
              <h3 className="font-semibold text-slate-800">Skill Alignment</h3>
              <Badge variant="blue">
                {result.skill_alignment?.overlap_score ?? 0}% skill overlap
              </Badge>
            </div>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <p className="text-xs font-semibold text-green-600 mb-2">✅ Skills You Have ({result.skill_alignment?.matched_skills?.length})</p>
                <div className="flex flex-wrap gap-1.5">
                  {result.skill_alignment?.matched_skills?.length
                    ? result.skill_alignment.matched_skills.map(s => <Badge key={s} variant="green">{s}</Badge>)
                    : <p className="text-xs text-slate-400">No matching skills found in the JD.</p>
                  }
                </div>
              </div>
              <div>
                <p className="text-xs font-semibold text-red-500 mb-2">❌ Skills to Add ({result.skill_alignment?.missing_skills?.length})</p>
                <div className="flex flex-wrap gap-1.5">
                  {result.skill_alignment?.missing_skills?.length
                    ? result.skill_alignment.missing_skills.map(s => <Badge key={s} variant="red">{s}</Badge>)
                    : <p className="text-xs text-slate-400">No missing skills detected.</p>
                  }
                </div>
              </div>
            </div>
          </div>

          {/* Keywords */}
          <div className="card">
            <h3 className="font-semibold text-slate-800 mb-4">Keyword Analysis</h3>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <p className="text-xs font-semibold text-green-600 mb-2">✅ Matched Keywords</p>
                <div className="flex flex-wrap gap-1.5">
                  {result.tfidf_similarity?.matched_keywords?.map(k => <Badge key={k} variant="green">{k}</Badge>)
                    || <p className="text-xs text-slate-400">None</p>}
                </div>
              </div>
              <div>
                <p className="text-xs font-semibold text-red-500 mb-2">❌ Missing Keywords</p>
                <div className="flex flex-wrap gap-1.5">
                  {result.tfidf_similarity?.missing_keywords?.map(k => <Badge key={k} variant="red">{k}</Badge>)
                    || <p className="text-xs text-slate-400">None</p>}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
