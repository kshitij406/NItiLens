import { useState } from 'react'

interface Props {
  onSubmit: (title: string, description: string) => void
  error: string | null
}

export default function Stage1Input({ onSubmit, error }: Props) {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [loading, setLoading] = useState(false)

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!title.trim() || !description.trim()) return
    setLoading(true)
    onSubmit(title.trim(), description.trim())
    // loading resets when App changes stage
  }

  return (
    <div
      className="two-col"
      style={{ display: 'grid', gridTemplateColumns: '38% 1fr', gap: 32, alignItems: 'start' }}
    >
      {/* ── Left: form ──────────────────────────────────────── */}
      <form onSubmit={handleSubmit}>
        <label className="nl-label">Policy Title</label>
        <input
          type="text"
          value={title}
          onChange={e => setTitle(e.target.value)}
          placeholder="e.g. One Nation One Election"
          required
          className="nl-input"
          style={{ display: 'block' }}
        />

        <label className="nl-label">Policy Description</label>
        <textarea
          value={description}
          onChange={e => setDescription(e.target.value)}
          placeholder="Describe the policy in detail. Include its objectives, implementation mechanism, and scope..."
          required
          rows={10}
          className="nl-input"
          style={{ height: 200, lineHeight: 1.6 }}
        />

        {error && (
          <div style={{
            marginTop: 16,
            background: 'rgba(239,68,68,0.08)',
            border: '1px solid rgba(239,68,68,0.3)',
            borderRadius: 6,
            padding: '10px 14px',
            fontSize: 13,
            color: 'var(--high)',
          }}>
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          style={{
            width: '100%',
            marginTop: 20,
            background: loading ? 'rgba(59,130,246,0.5)' : 'var(--accent)',
            color: '#fff',
            fontFamily: "'DM Sans', sans-serif",
            fontWeight: 600,
            fontSize: 15,
            padding: 14,
            borderRadius: 8,
            border: 'none',
            cursor: loading ? 'not-allowed' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 8,
            transition: 'background 150ms ease',
            opacity: loading ? 0.7 : 1,
          }}
          onMouseEnter={e => { if (!loading) (e.currentTarget as HTMLButtonElement).style.background = '#2563EB' }}
          onMouseLeave={e => { if (!loading) (e.currentTarget as HTMLButtonElement).style.background = 'var(--accent)' }}
        >
          {loading && (
            <span style={{
              display: 'inline-block',
              width: 16, height: 16,
              border: '2px solid white',
              borderTopColor: 'transparent',
              borderRadius: '50%',
              animation: 'spin 0.8s linear infinite',
              verticalAlign: 'middle',
            }} />
          )}
          {loading ? 'Deploying agents...' : 'Analyse Policy'}
        </button>

        <p className="mono" style={{ fontSize: 11, color: 'var(--text-dim)', textAlign: 'center', marginTop: 10 }}>
          Powered by 4 specialist AI agents + coordinator synthesis
        </p>
      </form>

      {/* ── Right: placeholder ───────────────────────────────── */}
      <div style={{
        border: '1px dashed var(--border)',
        borderRadius: 12,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: 400,
        gap: 10,
      }}>
        <span style={{ fontSize: 28, opacity: 0.2 }}>◈</span>
        <p className="mono" style={{ fontSize: 12, color: 'var(--text-dim)' }}>
          Analysis results will appear here
        </p>
      </div>
    </div>
  )
}
