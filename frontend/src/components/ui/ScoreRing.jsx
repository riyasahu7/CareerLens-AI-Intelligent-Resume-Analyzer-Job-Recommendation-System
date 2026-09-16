import clsx from 'clsx'

export default function ScoreRing({ score = 0, size = 120, label = 'Score' }) {
  const radius = 45
  const circ = 2 * Math.PI * radius
  const offset = circ - (score / 100) * circ
  const color = score >= 70 ? '#22c55e' : score >= 45 ? '#f59e0b' : '#ef4444'

  return (
    <div className="flex flex-col items-center gap-2">
      <svg width={size} height={size} viewBox="0 0 100 100">
        <circle cx="50" cy="50" r={radius} fill="none" stroke="#e2e8f0" strokeWidth="8" />
        <circle
          cx="50" cy="50" r={radius}
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeDasharray={circ}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform="rotate(-90 50 50)"
          style={{ transition: 'stroke-dashoffset 0.8s ease' }}
        />
        <text x="50" y="50" textAnchor="middle" dominantBaseline="central" fontSize="18" fontWeight="700" fill={color}>
          {score}
        </text>
      </svg>
      <p className="text-xs text-slate-500 font-medium">{label}</p>
    </div>
  )
}
