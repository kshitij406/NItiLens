import { AnalysisState } from '../types'
import AgentCard from './AgentCard'

const AGENT_ORDER = [
  'Fiscal Analyst',
  'Labor & Employment Analyst',
  'Equity & Social Impact Analyst',
  'Regional & Federal Analyst',
]

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

function regionColor(state: string): string {
  const region = getRegion(state)
  if (region === 'North') return '#3B82F6'
  if (region === 'South') return '#10B981'
  if (region === 'East') return '#F59E0B'
  if (region === 'West') return '#8B5CF6'
  return '#EC4899'
}

interface Props {
  state: AnalysisState
}

export default function Stage2Simulation({ state }: Props) {
  const total = state.personaProgress.total || (state.mode === 'demo' ? 30 : 50)
  const currentTicker = state.personaResults.length > 0
    ? state.personaResults[state.personaResults.length - 1]
    : null
  const progress = total > 0 ? (state.personaResults.length / total) * 100 : 0

  return (
    <div>
      <p className="mono" style={{ fontSize: 11, letterSpacing: '0.15em', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: 16 }}>
        Specialist Agents
      </p>
      <div
        className="agent-grid"
        style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 16 }}
      >
        {AGENT_ORDER.map((name, i) => {
          const result = state.agents[i]
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

      {(state.stage === 'personas' || state.personaResults.length > 0) && (
        <div style={{ marginTop: 40, animation: 'fadeUp 400ms ease both' }}>
          <p className="mono" style={{ fontSize: 11, letterSpacing: '0.15em', color: 'var(--text-dim)', textTransform: 'uppercase' }}>
            Simulating Citizen Responses
          </p>
          <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 4, marginBottom: 20 }}>
            Cross-referencing with {total} synthetic Indian personas grounded in NSSO demographic data
          </p>

          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
            {Array.from({ length: total }).map((_, i) => {
              const persona = state.personaResults[i]
              const filled = !!persona
              return (
                <div
                  key={i}
                  className={`persona-dot${filled ? ' revealed' : ''}`}
                  style={{ background: filled ? regionColor(persona.state) : 'var(--border)' }}
                  title={filled ? `${persona.name} · ${persona.occupation ?? 'N/A'} · ${persona.caste_category ?? 'N/A'}` : 'Pending persona'}
                />
              )
            })}
          </div>

          <div style={{ marginTop: 12, height: 4, borderRadius: 4, background: 'var(--border)' }}>
            <div style={{ height: '100%', width: `${progress}%`, background: 'var(--accent)', borderRadius: 4, transition: 'width 200ms ease' }} />
          </div>

          <p className="mono" style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 16, minHeight: 20 }}>
            {currentTicker ? `${currentTicker.name}, ${currentTicker.state}` : ''}
          </p>
          <p className="mono" style={{ fontSize: 11, color: 'var(--text-dim)', marginTop: 4 }}>
            Processing persona {state.personaProgress.current || state.personaResults.length} of {total}...
          </p>
        </div>
      )}
    </div>
  )
}
