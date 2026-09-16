/** Format an ISO date string to a readable local date */
export const fmtDate = (iso) =>
  iso ? new Date(iso).toLocaleDateString('en', { year: 'numeric', month: 'short', day: 'numeric' }) : '—'

/** Format an ISO date string to date + time */
export const fmtDateTime = (iso) =>
  iso ? new Date(iso).toLocaleString('en', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) : '—'

/** Format bytes to KB / MB */
export const fmtBytes = (bytes) => {
  if (!bytes) return '—'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

/** Score to colour class */
export const scoreColor = (score) => {
  if (score >= 70) return 'text-green-600'
  if (score >= 45) return 'text-yellow-600'
  return 'text-red-500'
}

/** Capitalize first letter */
export const capitalize = (s) => s ? s[0].toUpperCase() + s.slice(1) : ''

/** Convert snake_case to Title Case */
export const snakeToTitle = (s) =>
  s ? s.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()) : ''
