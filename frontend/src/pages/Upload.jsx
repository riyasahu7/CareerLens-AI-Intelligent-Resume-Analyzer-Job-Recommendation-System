import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'
import toast from 'react-hot-toast'
import clsx from 'clsx'

export default function Upload() {
  const navigate = useNavigate()
  const [file, setFile]           = useState(null)
  const [jobDesc, setJobDesc]     = useState('')
  const [uploading, setUploading] = useState(false)
  const [step, setStep]           = useState('upload') // upload | analyse | done

  const onDrop = useCallback(accepted => {
    if (accepted[0]) setFile(accepted[0])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    maxSize: 5 * 1024 * 1024,
    multiple: false,
    onDropRejected: files => {
      const err = files[0]?.errors?.[0]?.message || 'Invalid file.'
      toast.error(err)
    }
  })

  const handleUploadAndAnalyse = async () => {
    if (!file) { toast.error('Please select a PDF resume.'); return }
    setUploading(true)
    setStep('analyse')

    try {
      // 1. Upload
      const fd = new FormData()
      fd.append('file', file)
      const uploadRes = await api.post('/resumes', fd, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      const resumeId = uploadRes.data.resume.id

      if (uploadRes.data.resume?.warning) {
        toast.error(uploadRes.data.resume.warning, { duration: 8000 })
        setUploading(false); setStep('upload'); return
      }

      // 2. Analyse
      const analyseRes = await api.post('/analysis/resume', {
        resume_id: resumeId,
        job_description: jobDesc.trim() || undefined,
      })
      const analysisId = analyseRes.data.analysis.id
      toast.success('Analysis complete!')
      navigate(`/analysis/${analysisId}`)
    } catch (err) {
      toast.error(err.response?.data?.error || err.response?.data?.detail || 'Upload failed.')
      setStep('upload')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-800">Upload Your Resume</h2>
        <p className="text-slate-500 text-sm mt-1">
          Upload a text-based PDF (max 5 MB). Your file is processed in memory and not permanently stored by default.
        </p>
      </div>

      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={clsx(
          'border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all',
          isDragActive ? 'border-brand-500 bg-brand-50' : 'border-slate-200 hover:border-brand-400 hover:bg-slate-50',
          file ? 'border-green-400 bg-green-50' : ''
        )}
      >
        <input {...getInputProps()} />
        {file ? (
          <div className="space-y-2">
            <div className="text-4xl">✅</div>
            <p className="font-semibold text-green-700">{file.name}</p>
            <p className="text-sm text-slate-500">{(file.size / 1024).toFixed(1)} KB · Click to change</p>
          </div>
        ) : (
          <div className="space-y-3">
            <div className="text-4xl">📄</div>
            <p className="font-semibold text-slate-700">
              {isDragActive ? 'Drop your PDF here' : 'Drag & drop your PDF resume'}
            </p>
            <p className="text-sm text-slate-400">or click to browse · PDF only · max 5 MB</p>
          </div>
        )}
      </div>

      {/* Optional JD */}
      <div className="card">
        <label className="label">
          Job Description <span className="text-slate-400 font-normal">(optional — enables keyword matching)</span>
        </label>
        <textarea
          className="input resize-none"
          rows={6}
          placeholder="Paste a job description here to get TF-IDF similarity scoring and keyword gap analysis…"
          value={jobDesc}
          onChange={e => setJobDesc(e.target.value)}
        />
        <p className="text-xs text-slate-400 mt-1.5">
          The job description is used only for analysis and is not stored permanently.
        </p>
      </div>

      <button
        className="btn-primary w-full py-3 text-base"
        onClick={handleUploadAndAnalyse}
        disabled={!file || uploading}
      >
        {uploading
          ? step === 'analyse' ? '🔬 Analysing resume…' : '⬆️ Uploading…'
          : '🚀 Upload & Analyse'
        }
      </button>

      <div className="card bg-amber-50 border-amber-200">
        <h4 className="text-sm font-semibold text-amber-800 mb-1">ℹ️ What we analyse</h4>
        <ul className="text-xs text-amber-700 space-y-0.5 list-disc list-inside">
          <li>Contact info, summary, experience, education, skills, projects, certifications</li>
          <li>Technical skills detected from your text (not invented)</li>
          <li>ATS-style score based on section completeness, skills, and formatting signals</li>
          <li>Job description keyword matching (TF-IDF) when a JD is provided</li>
        </ul>
      </div>
    </div>
  )
}
