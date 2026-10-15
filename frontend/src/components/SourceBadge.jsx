export default function SourceBadge({ route }) {
  const map = {
    local: { label: 'Your documents', dot: 'bg-accent' },
    web: { label: 'Web search', dot: 'bg-success' },
    both: { label: 'Documents + Web', dot: 'bg-accent' },
    'local→web (fallback)': { label: 'Web (fallback)', dot: 'bg-success' },
  }

  const info = map[route] || { label: route, dot: 'bg-fg-dim' }

  return (
    <span className="inline-flex items-center gap-1.5 text-xs text-fg-muted">
      <span className={`w-1.5 h-1.5 rounded-full ${info.dot}`} />
      {info.label}
    </span>
  )
}