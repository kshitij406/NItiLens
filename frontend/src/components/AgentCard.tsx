import { AgentResult } from '../types'

const ICONS: Record<string, string> = {
  'Fiscal Analyst': '💰',
  'Labor & Employment Analyst': '👷',
  'Equity & Social Impact Analyst': '⚖️',
  'Regional & Federal Analyst': '🗺️',
}

const SEV_COLOR: Record<string, string> = {
  High: 'var(--high)',
  Medium: 'var(--medium)',
  Low: 'var(--low)',
}

interface Props {
  agentName: string
  agent?: AgentResult
  index?: number
  complete: boolean
}

function WaitingContent({ agentName }: { agentName: string }) {
  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontSize: 18 }}>{ICONS[agentName] ?? '📋'}</span>
          <span style={{ fontWeight: 600, fontSize: 14, color: 'var(--text-primary)' }}>{agentName}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <div style={{
            width: 8, height: 8, borderRadius: '50%',
            background: 'var(--medium)',
            animation: 'pulseDot 1.5s infinite',
          }} />
          <span className="mono" style={{ fontSize: 11, color: 'var(--text-dim)' }}>
            Awaiting deployment
          </span>
        </div>
      </div>
      <div style={{ marginTop: 14, display: 'flex', flexDirection: 'column', gap: 8 }}>
        <div className="shimmer-line" style={{ height: 10, width: '100%' }} />
        <div className="shimmer-line" style={{ height: 10, width: '80%' }} />
        <div className="shimmer-line" style={{ height: 10, width: '60%' }} />
      </div>
    </div>
  )
}

function CompleteContent({ agent }: { agent: AgentResult }) {
  const sc = SEV_COLOR[agent.severity] ?? SEV_COLOR.Medium
  return (
    <div style={{ animation: 'fadeUp 400ms ease both' }}>
      {/* Header row */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8, flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontSize: 18 }}>{ICONS[agent.agent] ?? '📋'}</span>
          <span style={{ fontWeight: 600, fontSize: 14, color: 'var(--text-primary)' }}>{agent.agent}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
          <div style={{
            width: 8, height: 8, borderRadius: '50%',
            background: 'var(--low)', flexShrink: 0,
            animation: 'popIn 200ms ease',
          }} />
          <span className="mono" style={{ fontSize: 11, color: 'var(--low)' }}>Analysis complete</span>
          <span className="mono" style={{
            fontSize: 11, textTransform: 'uppercase',
            border: `1px solid ${sc}`, color: sc,
            padding: '2px 8px', borderRadius: 20,
          }}>
            {agent.severity}
          </span>
        </div>
      </div>

      {/* Summary */}
      {agent.summary && (
        <p style={{ marginTop: 10, fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
          {agent.summary}
        </p>
      )}

      <div style={{ borderTop: '1px solid var(--border)', margin: '12px 0' }} />

      {/* Risks */}
      {agent.risks?.length > 0 && (
        <div style={{ marginBottom: 12 }}>
          <p className="mono" style={{ fontSize: 10, letterSpacing: '0.15em', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: 6 }}>
            Risks
          </p>
          {agent.risks.map((r, i) => (
            <div key={i} style={{ borderLeft: `2px solid ${sc}`, paddingLeft: 8, fontSize: 13, color: 'var(--text-secondary)', marginBottom: 5, lineHeight: 1.5 }}>
              {r}
            </div>
          ))}
        </div>
      )}

      {/* Opportunities */}
      {agent.opportunities?.length > 0 && (
        <div style={{ marginBottom: 12 }}>
          <p className="mono" style={{ fontSize: 10, letterSpacing: '0.15em', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: 6 }}>
            Opportunities
          </p>
          {agent.opportunities.map((o, i) => (
            <div key={i} style={{ borderLeft: '2px solid var(--low)', paddingLeft: 8, fontSize: 13, color: 'var(--text-secondary)', marginBottom: 5, lineHeight: 1.5 }}>
              {o}
            </div>
          ))}
        </div>
      )}

      {/* Most Affected */}
      {agent.most_affected && (
        <div>
          <p className="mono" style={{ fontSize: 10, letterSpacing: '0.15em', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: 4 }}>
            Most Affected
          </p>
          <p style={{ fontSize: 13, color: 'var(--text-primary)', fontStyle: 'italic', lineHeight: 1.55 }}>
            {agent.most_affected}
          </p>
        </div>
      )}
    </div>
  )
}

export default function AgentCard({ agentName, agent, complete }: Props) {
  return (
    <div className={`agent-card${complete ? ' complete' : ''}`}>
      {complete && agent
        ? <CompleteContent agent={agent} />
        : <WaitingContent agentName={agentName} />
      }
    </div>
  )
}
