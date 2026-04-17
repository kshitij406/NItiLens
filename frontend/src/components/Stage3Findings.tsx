import { AnalysisState, CoordinatorResult, PersonaResult } from '../types'
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

const CONF_COLOR: Record<string, string> = {
  High: '#10B981',
  Medium: '#F59E0B',
  Low: '#EF4444',
}

const REGION_COLOR: Record<string, string> = {
  North: '#3B82F6',
  South: '#10B981',
  East: '#F59E0B',
  West: '#8B5CF6',
  NE: '#EC4899',
}

const NORTH_STATES = new Set([
  'Uttar Pradesh', 'Bihar', 'Punjab', 'Haryana', 'Himachal Pradesh',
  'Uttarakhand', 'J&K', 'Delhi', 'Rajasthan', 'Madhya Pradesh',
])
const SOUTH_STATES = new Set(['Tamil Nadu', 'Kerala', 'Karnataka', 'Andhra Pradesh', 'Telangana'])
const WEST_STATES = new Set(['Maharashtra', 'Gujarat', 'Goa'])
const NORTHEAST_STATES = new Set(['Manipur', 'Mizoram', 'Nagaland', 'Meghalaya', 'Sikkim', 'Tripura', 'Arunachal'])

function getRegion(state: string): 'North' | 'South' | 'East' | 'West' | 'NE' {
  if (NORTHEAST_STATES.has(state)) return 'NE'
  if (NORTH_STATES.has(state)) return 'North'
  if (SOUTH_STATES.has(state)) return 'South'
  if (WEST_STATES.has(state)) return 'West'
  return 'East'
}

function computeConsensus(personas: PersonaResult[]) {
  const significant = personas.filter(p =>
    Array.isArray(p.validations) && p.validations.some(v => Number(v.severity_for_me) >= 2)
  ).length

  const byRegion = { North: 0, South: 0, East: 0, West: 0, NE: 0 }
  for (const p of personas) {
    const hasSignificant = Array.isArray(p.validations) && p.validations.some(v => Number(v.severity_for_me) >= 2)
    if (hasSignificant) {
      const region = getRegion(p.state)
      byRegion[region] += 1
    }
  }

  const missed = personas
    .filter(p => typeof p.missed_risk === 'string' && p.missed_risk.trim().length > 0)
    .map(p => ({ name: p.name, state: p.state, text: (p.missed_risk as string).trim() }))

  return { significant, byRegion, missed }
}

function CoordinatorCard({ coordinator, personas }: { coordinator: CoordinatorResult; personas: PersonaResult[] }) {
  const confColor = SEV_COLOR[coordinator.confidence] ?? SEV_COLOR.Medium
  const consensus = computeConsensus(personas)

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

      <div style={{ borderTop: '1px solid var(--border)', margin: '20px 0 14px' }} />
      <p className="mono" style={{ fontSize: 10, letterSpacing: '0.12em', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: 8 }}>
        PERSONA CONSENSUS
      </p>
      <p style={{ fontSize: 14, color: 'var(--text-primary)', marginBottom: 10 }}>
        {consensus.significant} of {personas.length} personas identified significant impact (severity_for_me {'>='} 2)
      </p>
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        {([
          ['North', consensus.byRegion.North],
          ['South', consensus.byRegion.South],
          ['East', consensus.byRegion.East],
          ['West', consensus.byRegion.West],
          ['NE', consensus.byRegion.NE],
        ] as const).map(([label, count]) => (
          <span
            key={label}
            className="mono"
            style={{
              fontSize: 10,
              border: `1px solid ${REGION_COLOR[label]}`,
              color: REGION_COLOR[label],
              borderRadius: 20,
              padding: '3px 8px',
            }}
          >
            {label}: {count}
          </span>
        ))}
      </div>

      {consensus.missed.length > 0 && (
        <>
          <div style={{ borderTop: '1px solid var(--border)', margin: '18px 0 12px' }} />
          <p className="mono" style={{ fontSize: 10, letterSpacing: '0.12em', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: 8 }}>
            CITIZEN-FLAGGED RISKS
          </p>
          <div style={{ display: 'grid', gap: 8 }}>
            {consensus.missed.map((item, idx) => (
              <div key={`${item.name}-${idx}`} style={{ border: '1px solid var(--border)', borderRadius: 8, padding: '10px 12px' }}>
                <p className="mono" style={{ fontSize: 10, color: 'var(--text-dim)', marginBottom: 4 }}>
                  {item.name} · {item.state}
                </p>
                <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                  {item.text}
                </p>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}

interface Props {
  state: AnalysisState
  onReset: () => void
}

export default function Stage3Findings({ state, onReset }: Props) {
  const { agents, coordinator, overall_severity, policy_title, personaResults, confidence, seal } = state
  const sc = SEV_COLOR[overall_severity] ?? SEV_COLOR.Medium
  const confColor = confidence ? CONF_COLOR[confidence.label] : 'var(--text-dim)'

  return (
    <div style={{ animation: 'fadeUp 280ms ease both' }}>
      <div className="severity-banner" style={{ borderLeftColor: sc, marginBottom: 8 }}>
        <div>
          <p className="mono" style={{ fontSize: 10, letterSpacing: '0.15em', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: 4 }}>
            Overall Risk Assessment
          </p>
          <p style={{ fontSize: 28, fontWeight: 700, color: sc, fontFamily: "'DM Sans', sans-serif", lineHeight: 1 }}>
            {overall_severity}
          </p>
        </div>
        <div style={{ textAlign: 'right', maxWidth: 320 }}>
          <p style={{ fontSize: 14, color: 'var(--text-secondary)', fontStyle: 'italic' }}>
            {policy_title}
          </p>
          {confidence && (
            <p className="mono" style={{ fontSize: 12, marginTop: 6, color: confColor }}>
              System Confidence: {confidence.score}/{confidence.out_of}
            </p>
          )}
        </div>
      </div>

      <p className="mono" style={{ fontSize: 11, color: 'var(--text-dim)', marginBottom: 18 }}>
        Consensus across 4 specialist agents and {personaResults.length} synthetic Indian personas
      </p>

      <div
        className="agent-grid"
        style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 14 }}
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

      {coordinator && <CoordinatorCard coordinator={coordinator} personas={personaResults} />}

      {confidence && confidence.caveats.length > 0 && (
        <div
          style={{
            border: '1px solid var(--border)',
            background: 'var(--bg-surface)',
            borderLeft: '3px solid #F59E0B',
            padding: '12px 16px',
            borderRadius: 8,
            marginTop: 18,
          }}
        >
          <p className="mono" style={{ fontSize: 10, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.12em', marginBottom: 8 }}>
            ANALYTICAL CAVEATS
          </p>
          {confidence.caveats.map((c) => (
            <p key={c} style={{ fontSize: 14, color: 'var(--text-secondary)', marginBottom: 6 }}>
              • {c}
            </p>
          ))}
          <p style={{ fontSize: 12, color: 'var(--text-dim)', fontStyle: 'italic', marginTop: 8 }}>
            {confidence.caveat_text}
          </p>
        </div>
      )}

      {seal && (
        <div style={{ marginTop: 18 }}>
          <p className="mono" style={{ fontSize: 11, color: 'var(--text-dim)' }}>
            Analysis sealed · <span style={{ color: 'var(--text-secondary)' }}>{seal.hash}</span> · {seal.timestamp}
          </p>
        </div>
      )}

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
