import { AnalysisState, CoordinatorResult } from '../types'
import AgentCard from './AgentCard'

const AGENT_ORDER = [
  'Fiscal Analyst',
  'Labor & Employment Analyst',
  'Equity & Social Impact Analyst',
  'Regional & Federal Analyst',
]

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

interface Props {
  state: AnalysisState
  onReset: () => void
}

export default function Stage3Findings({ state, onReset }: Props) {
  const { agents, coordinator, overall_severity, policy_title } = state
  const sc = SEV_COLOR[overall_severity] ?? SEV_COLOR.Medium

  return (
    <div style={{ animation: 'fadeUp 500ms ease both' }}>
      {/* Overall severity banner */}
      <div className="severity-banner" style={{ borderLeftColor: sc, marginBottom: 8 }}>
        <div>
          <p className="mono" style={{ fontSize: 10, letterSpacing: '0.15em', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: 4 }}>
            Overall Risk Assessment
          </p>
          <p style={{ fontSize: 28, fontWeight: 700, color: sc, fontFamily: "'DM Sans', sans-serif", lineHeight: 1 }}>
            {overall_severity}
          </p>
        </div>
        <p style={{ fontSize: 14, color: 'var(--text-secondary)', fontStyle: 'italic', textAlign: 'right', maxWidth: 280 }}>
          {policy_title}
        </p>
      </div>

      <p className="mono" style={{ fontSize: 11, color: 'var(--text-dim)', marginBottom: 24 }}>
        Consensus across 4 specialist agents and 50 synthetic Indian personas
      </p>

      {/* 2×2 agent grid */}
      <div
        className="agent-grid"
        style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 16 }}
      >
        {AGENT_ORDER.map((name, i) => {
          const result = agents.find(a => a.agent === name)
          return (
            <AgentCard
              key={name}
              agentName={name}
              agent={result}
              index={i}
              complete={!!result}
            />
          )
        })}
      </div>

      {/* Coordinator card */}
      {coordinator && <CoordinatorCard coordinator={coordinator} />}

      {/* Reset */}
      <div style={{ marginTop: 32, display: 'flex', justifyContent: 'center' }}>
        <button
          onClick={onReset}
          style={{
            background: 'none',
            border: '1px solid var(--border-bright)',
            color: 'var(--text-secondary)',
            fontFamily: "'DM Sans', sans-serif",
            fontSize: 14,
            padding: '10px 24px',
            borderRadius: 6,
            cursor: 'pointer',
            transition: 'color 150ms, border-color 150ms',
          }}
          onMouseEnter={e => {
            const el = e.currentTarget as HTMLButtonElement
            el.style.color = 'var(--text-primary)'
            el.style.borderColor = 'var(--accent)'
          }}
          onMouseLeave={e => {
            const el = e.currentTarget as HTMLButtonElement
            el.style.color = 'var(--text-secondary)'
            el.style.borderColor = 'var(--border-bright)'
          }}
        >
          Analyse Another Policy
        </button>
      </div>
    </div>
  )
}
