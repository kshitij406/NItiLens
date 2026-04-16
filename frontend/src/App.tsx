import { useState, useRef, useCallback } from 'react'
import { AnalysisState, AgentResult, CoordinatorResult } from './types'
import Stage1Input from './components/Stage1Input'
import Stage2Simulation from './components/Stage2Simulation'
import Stage3Findings from './components/Stage3Findings'
import ValidationExample from './components/ValidationExample'

const INITIAL_STATE: AnalysisState = {
  stage: 'idle',
  agents: [],
  activeAgent: 0,
  personaCount: 0,
  coordinator: null,
  overall_severity: '',
  policy_title: '',
}

const TABS = ['Analyse Policy', 'Historical Validation']

export default function App() {
  const [state, setState] = useState<AnalysisState>(INITIAL_STATE)
  const [activeTab, setActiveTab] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const esRef = useRef<EventSource | null>(null)

  const startAnalysis = useCallback((title: string, description: string) => {
    esRef.current?.close()
    setError(null)
    setState({
      ...INITIAL_STATE,
      stage: 'agents',
      policy_title: title,
    })

    const params = new URLSearchParams({ title, description })
    const es = new EventSource(`/api/analyse/stream?${params}`)
    esRef.current = es

    es.onmessage = (e: MessageEvent) => {
      try {
        const event = JSON.parse(e.data as string)

        if (event.type === 'agent') {
          setState(prev => ({
            ...prev,
            agents: [...prev.agents, event.data as AgentResult],
            activeAgent: prev.agents.length + 1,
          }))
        } else if (event.type === 'coordinator') {
          setState(prev => ({ ...prev, coordinator: event.data as CoordinatorResult }))
        } else if (event.type === 'done') {
          setState(prev => ({
            ...prev,
            overall_severity: event.overall_severity as string,
            stage: 'personas',
          }))
          es.close()
        }
      } catch {
        // ignore malformed event
      }
    }

    es.onerror = () => {
      setError('Analysis failed — check that the backend is running on port 8000.')
      setState(prev => ({ ...prev, stage: 'idle' }))
      es.close()
    }
  }, [])

  const handlePersonasDone = useCallback(() => {
    setState(prev => ({ ...prev, stage: 'complete' }))
  }, [])

  return (
    <div className="content" style={{ maxWidth: 1200, margin: '0 auto', padding: '0 24px 80px' }}>

      {/* ── Header ──────────────────────────────────────────── */}
      <header style={{ paddingTop: 32, marginBottom: 0 }}>
        <p className="mono" style={{ fontSize: 11, letterSpacing: '0.15em', color: 'var(--text-dim)', textTransform: 'uppercase' }}>
          NITILENS / POLICY INTELLIGENCE
        </p>
        <h1 style={{
          fontFamily: "'Instrument Serif', Georgia, serif",
          fontSize: 'clamp(48px, 7vw, 72px)',
          lineHeight: 1,
          color: 'var(--text-primary)',
          marginTop: 8,
        }}>
          NitiLens
        </h1>
        <p style={{ fontSize: 18, color: 'var(--text-secondary)', marginTop: 8 }}>
          AI Policy Stress Tester for India
        </p>
        <div style={{ marginTop: 12, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {['AI & ML Track', 'DayZero 2.0', 'Team JFKN'].map(label => (
            <span key={label} className="mono" style={{
              fontSize: 11,
              color: 'var(--text-dim)',
              background: 'var(--bg-elevated)',
              border: '1px solid var(--border-bright)',
              borderRadius: 4,
              padding: '4px 10px',
              display: 'inline-block',
            }}>
              {label}
            </span>
          ))}
        </div>
        <hr style={{ border: 'none', borderTop: '1px solid var(--border)', marginTop: 24 }} />
      </header>

      {/* ── Tab bar ─────────────────────────────────────────── */}
      <div style={{ display: 'flex', borderBottom: '1px solid var(--border)', marginTop: 0 }}>
        {TABS.map((tab, i) => (
          <button
            key={tab}
            onClick={() => setActiveTab(i)}
            style={{
              background: 'none',
              border: 'none',
              borderBottom: activeTab === i ? '2px solid var(--accent)' : '2px solid transparent',
              color: activeTab === i ? 'var(--text-primary)' : 'var(--text-secondary)',
              fontFamily: "'DM Sans', sans-serif",
              fontSize: 14,
              fontWeight: 500,
              padding: '16px 0',
              marginRight: 32,
              marginBottom: -1,
              cursor: 'pointer',
              transition: 'color 150ms ease, border-color 150ms ease',
            }}
            onMouseEnter={e => { if (activeTab !== i) (e.target as HTMLElement).style.color = 'var(--text-primary)' }}
            onMouseLeave={e => { if (activeTab !== i) (e.target as HTMLElement).style.color = 'var(--text-secondary)' }}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* ── Tab content ─────────────────────────────────────── */}
      <div style={{ marginTop: 32 }}>
        {activeTab === 0 && (
          <>
            {/* Stage 1 — idle */}
            {state.stage === 'idle' && (
              <Stage1Input onSubmit={startAnalysis} error={error} />
            )}

            {/* Stage 2 — agents + personas */}
            {(state.stage === 'agents' || state.stage === 'personas') && (
              <Stage2Simulation state={state} onPersonasDone={handlePersonasDone} />
            )}

            {/* Stage 3 — complete */}
            {state.stage === 'complete' && (
              <Stage3Findings state={state} onReset={() => setState(INITIAL_STATE)} />
            )}
          </>
        )}

        {activeTab === 1 && <ValidationExample />}
      </div>

    </div>
  )
}
