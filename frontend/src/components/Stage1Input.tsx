import { useState } from 'react'
import { PolicyClassification } from '../types'

interface Props {
  onSubmit: (title: string, description: string, mode: 'demo' | 'full') => void
  error: string | null
  classification?: PolicyClassification | null
}

export default function Stage1Input({ onSubmit, error, classification }: Props) {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [loading, setLoading] = useState(false)
  const [mode, setMode] = useState<'demo' | 'full'>('demo')

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!title.trim() || !description.trim()) return
    setLoading(true)
    onSubmit(title.trim(), description.trim(), mode)
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

        <div style={{ marginTop: 14, display: 'flex', gap: 8 }}>
          <button
            type="button"
            onClick={() => setMode('demo')}
            style={{
              flex: 1,
              borderRadius: 999,
              padding: '8px 12px',
              fontSize: 12,
              fontWeight: 600,
              fontFamily: "'DM Sans', sans-serif",
              cursor: 'pointer',
              border: mode === 'demo' ? '1px solid var(--accent)' : '1px solid var(--border-bright)',
              background: mode === 'demo' ? 'var(--accent)' : 'transparent',
              color: mode === 'demo' ? '#fff' : 'var(--text-secondary)',
            }}
          >
            DEMO
          </button>
          <button
            type="button"
            onClick={() => setMode('full')}
            style={{
              flex: 1,
              borderRadius: 999,
              padding: '8px 12px',
              fontSize: 12,
              fontWeight: 600,
              fontFamily: "'DM Sans', sans-serif",
              cursor: 'pointer',
              border: mode === 'full' ? '1px solid var(--accent)' : '1px solid var(--border-bright)',
              background: mode === 'full' ? 'var(--accent)' : 'transparent',
              color: mode === 'full' ? '#fff' : 'var(--text-secondary)',
            }}
          >
            FULL
          </button>
        </div>

        <p className="mono" style={{ fontSize: 10, color: 'var(--text-dim)', textAlign: 'center', marginTop: 8 }}>
          DEMO: 30 personas · ~2 min
        </p>
        <p className="mono" style={{ fontSize: 10, color: 'var(--text-dim)', textAlign: 'center', marginTop: 2 }}>
          FULL: 50 personas · ~5 min
        </p>

        {classification && (
          <div style={{ marginTop: 16, animation: 'fadeUp 350ms ease both' }}>
            <p className="mono" style={{ fontSize: 10, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.12em', marginBottom: 8 }}>
              POLICY CLASSIFICATION
            </p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {[classification.domain, classification.geography, classification.time_horizon, classification.primary_affected].map((tag) => (
                <span
                  key={tag}
                  className="mono"
                  style={{
                    fontSize: 11,
                    color: 'var(--text-dim)',
                    background: 'var(--bg-elevated)',
                    border: '1px solid var(--border-bright)',
                    borderRadius: 4,
                    padding: '4px 8px',
                    textTransform: 'uppercase',
                  }}
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}
      </form>

      {/* ── Right: quick guidance ─────────────────────────────── */}
      <div style={{
        border: '1px solid var(--border)',
        borderRadius: 12,
        display: 'grid',
        gridTemplateRows: 'auto auto 1fr',
        minHeight: 400,
        gap: 12,
        padding: 18,
        background: 'linear-gradient(180deg, rgba(19,30,46,0.55) 0%, rgba(13,21,32,0.35) 100%)',
      }}>
        <p className="mono" style={{ fontSize: 10, color: 'var(--text-dim)', letterSpacing: '0.12em', textTransform: 'uppercase' }}>
          QUICK INPUT GUIDE
        </p>
        <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
          Add concrete policy details: who is targeted, rollout timeline, funding route, and affected states.
        </p>
        <div style={{ borderTop: '1px solid var(--border)', paddingTop: 12 }}>
          <p className="mono" style={{ fontSize: 10, color: 'var(--text-dim)', marginBottom: 8 }}>EXAMPLE FORMAT</p>
          <p style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.65 }}>
            "Expand fertilizer subsidy to rainfed districts with DBT transfer, phased over 24 months, jointly financed by centre and states."
          </p>
        </div>
      </div>
    </div>
  )
}
