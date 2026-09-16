import clsx from 'clsx'

const variants = {
  green:  'bg-green-100 text-green-800',
  red:    'bg-red-100 text-red-800',
  yellow: 'bg-yellow-100 text-yellow-800',
  blue:   'bg-blue-100 text-blue-800',
  purple: 'bg-purple-100 text-purple-800',
  gray:   'bg-slate-100 text-slate-700',
}

export default function Badge({ children, variant = 'gray', className }) {
  return (
    <span className={clsx('badge', variants[variant], className)}>
      {children}
    </span>
  )
}
