import { useEffect, useState } from 'react'
import { AnalysisState } from '../types'
import AgentCard from './AgentCard'

const AGENT_ORDER = [
  'Fiscal Analyst',
  'Labor & Employment Analyst',
  'Equity & Social Impact Analyst',
  'Regional & Federal Analyst',
]

const PERSONAS = [
  'UP farmer, age 34, annual income ₹85,000',
  'Mumbai gig worker, age 26, no formal contract',
  'Kerala nurse, age 31, government employed',
  'Rajasthan ASHA worker, age 44, female',
  'Bihar landless laborer, age 52, SC household',
  'Chennai software engineer, age 28, private sector',
  'Assam tea garden worker, age 38, ST community',
  'Delhi auto-rickshaw driver, age 41, self-employed',
  'Odisha tribal farmer, age 29, forest rights holder',
  'Gujarat MSME owner, age 47, 12 employees',
  'Punjab wheat farmer, age 55, medium landholding',
  'Jharkhand migrant worker, age 33, seasonal',
  'Hyderabad IT professional, age 30, high income',
  'West Bengal jute mill worker, age 48, union member',
  'MP Anganwadi worker, age 39, government scheme',
  'Tamil Nadu fisherwoman, age 36, coastal community',
  'Uttarakhand hill farmer, age 61, marginal land',
  'Nagaland tribal council member, age 55',
  'Haryana dairy farmer, age 43, cooperative member',
  'Karnataka garment worker, age 27, female migrant',
]

// 50 dots: North(15)=blue, South(12)=green, East(8)=amber, West(12)=purple, NE(3)=pink
const RAW_COLORS = [
  ...Array(15).fill('#3B82F6'),
  ...Array(12).fill('#10B981'),
  ...Array(8).fill('#F59E0B'),
  ...Array(12).fill('#8B5CF6'),
  ...Array(3).fill('#EC4899'),
]
// deterministic shuffle via seeded-ish sort
const DOT_COLORS = RAW_COLORS
  .map((c, i) => ({ c, k: (i * 2654435761) % 50 }))
  .sort((a, b) => a.k - b.k)
  .map(x => x.c)

interface Props {
  state: AnalysisState
  onPersonasDone: () => void
}

export default function Stage2Simulation({ state, onPersonasDone }: Props) {
  const [personaCount, setPersonaCount] = useState(0)

  useEffect(() => {
    if (state.stage !== 'personas') {
      setPersonaCount(0)
      return
    }
    let count = 0
    const interval = setInterval(() => {
      count++
      setPersonaCount(count)
      if (count >= 50) {
        clearInterval(interval)
        setTimeout(onPersonasDone, 600)
      }
    }, 80)
    return () => clearInterval(interval)
  }, [state.stage, onPersonasDone])

  const currentTicker = personaCount > 0
    ? PERSONAS[(personaCount - 1) % PERSONAS.length]
    : ''

  return (
    <div>
      {/* ── Agent cards grid ─────────────────────────────── */}
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

      {/* ── Persona simulation ───────────────────────────── */}
      {state.stage === 'personas' && (
        <div style={{ marginTop: 40, animation: 'fadeUp 400ms ease both' }}>
          <p className="mono" style={{ fontSize: 11, letterSpacing: '0.15em', color: 'var(--text-dim)', textTransform: 'uppercase' }}>
            Simulating Citizen Responses
          </p>
          <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 4, marginBottom: 20 }}>
            Cross-referencing with 50 synthetic Indian personas grounded in NSSO demographic data
          </p>

          {/* Dot grid */}
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
            {DOT_COLORS.map((color, i) => (
              <div
                key={i}
                className={`persona-dot${i < personaCount ? ' revealed' : ''}`}
                style={{ background: color }}
              />
            ))}
          </div>

          {/* Ticker */}
          <p className="mono" style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 16, minHeight: 20 }}>
            {currentTicker}
          </p>
          <p className="mono" style={{ fontSize: 11, color: 'var(--text-dim)', marginTop: 4 }}>
            Processing persona {personaCount} of 50...
          </p>
        </div>
      )}
    </div>
  )
}
