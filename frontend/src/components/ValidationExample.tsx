import { useEffect, useState } from 'react'
import { ValidationResult } from '../types'
import AgentCard from './AgentCard'
import { CoordinatorResult } from '../types'

const API_BASE = import.meta.env.VITE_API_URL ?? ''

const SEV_COLOR: Record<string, string> = {
  High: 'var(--high)',
  Medium: 'var(--medium)',
  Low: 'var(--low)',
}

function CoordinatorCard({ coordinator }: { coordinator: CoordinatorResult }) {
  const confColor = SEV_COLOR[coordinator.confidence] ?? SEV_COLOR.Medium
  return (
    <div className="coordinator-card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 8 }}>
        <p className="mono" style={{ fontSize: 11, letterSpacing: '0.12em', color: 'var(--text-dim)', textTransform: 'uppercase' }}>
          Intelligence Briefing
        </p>
        <span className="mono" style={{
          fontSize: 11, textTransform: 'uppercase',
          border: `1px solid ${confColor}`, color: confColor,
          padding: '2px 8px', borderRadius: 20,
        }}>
          {coordinator.confidence} confidence
        </span>
      </div>

      <p style={{ fontSize: 16, fontWeight: 600, color: 'var(--text-primary)', marginTop: 8, marginBottom: 16 }}>
        Coordinator Synthesis
      </p>

      {([
        { label: 'Verdict', value: coordinator.verdict },
        { label: 'Key Risk', value: coordinator.key_risk },
        { label: 'Blind Spot', value: coordinator.blind_spot },
        { label: 'Sharpest Disagreement', value: coordinator.sharpest_disagreement },
      ] as const).map(({ label, value }) => (
        <div key={label} style={{ marginBottom: 16 }}>
          <p className="mono" style={{ fontSize: 10, letterSpacing: '0.12em', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: 4 }}>
            {label}
          </p>
          <p style={{ fontSize: 14, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
            {value}
          </p>
        </div>
      ))}
    </div>
  )
}

export default function ValidationExample() {
  const [data, setData] = useState<ValidationResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setLoading(true)
    fetch(`${API_BASE}/api/validate`)
      .then(r => { if (!r.ok) throw new Error(`Server responded with ${r.status}`); return r.json() })
      .then(d => setData(d as ValidationResult))
      .catch(e => setError((e as Error).message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16, padding: '64px 0' }}>
        <div style={{
          width: 36, height: 36, borderRadius: '50%',
          border: '2px solid var(--border-bright)',
          borderTopColor: 'var(--accent)',
          animation: 'spin 0.7s linear infinite',
        }} />
        <p className="mono" style={{ fontSize: 12, color: 'var(--text-dim)' }}>Loading validation data...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div style={{
        border: '1px solid rgba(239,68,68,0.25)',
        borderLeft: '4px solid var(--high)',
        borderRadius: 8,
        padding: '14px 18px',
        color: 'var(--text-secondary)',
        fontSize: 13,
      }}>
        <strong style={{ color: 'var(--high)' }}>Failed to load: </strong>{error}
      </div>
    )
  }

  if (!data) return null

  const sc = SEV_COLOR[data.overall_severity] ?? SEV_COLOR.Medium

  return (
    <div style={{ animation: 'fadeUp 300ms ease both' }}>
      {/* Validation banner */}
      <div style={{
        background: 'var(--accent-dim)',
        border: '1px solid var(--border-bright)',
        borderRadius: 8,
        padding: '16px 20px',
        marginBottom: 24,
      }}>
        <p style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: 15, marginBottom: 6 }}>
          Retrospective Validation: MGNREGA (2005)
        </p>
        <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
          NitiLens correctly identified the risk profile for one of India&apos;s most studied policies.
          Findings confirmed by NSSO, World Bank, and 20 years of implementation data.
        </p>
        {data.note && (
          <p className="mono" style={{ fontSize: 10, color: 'var(--text-dim)', marginTop: 8 }}>
            {data.note}
          </p>
        )}
      </div>

      {/* Overall severity banner */}
      <div className="severity-banner" style={{ borderLeftColor: sc, marginBottom: 8 }}>
        <div>
          <p className="mono" style={{ fontSize: 10, letterSpacing: '0.15em', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: 4 }}>
            Overall Risk Assessment
          </p>
          <p style={{ fontSize: 28, fontWeight: 700, color: sc, fontFamily: "'DM Sans', sans-serif", lineHeight: 1 }}>
            {data.overall_severity}
          </p>
        </div>
        <p style={{ fontSize: 14, color: 'var(--text-secondary)', fontStyle: 'italic', textAlign: 'right', maxWidth: 320 }}>
          {data.policy_title}
        </p>
      </div>

      <p className="mono" style={{ fontSize: 11, color: 'var(--text-dim)', marginBottom: 24 }}>
        Retrospective analysis grounded in 20 years of documented outcomes
      </p>

      {/* 2×2 agent grid */}
      <div
        className="agent-grid"
        style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 16 }}
      >
        {data.agents.map((agent, i) => (
          <AgentCard key={agent.agent} agentName={agent.agent} agent={agent} index={i} complete={true} />
        ))}
      </div>

      {/* Coordinator card */}
      {data.coordinator && <CoordinatorCard coordinator={data.coordinator} />}
    </div>
  )
}
