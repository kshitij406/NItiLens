import { useState, useRef, useCallback } from 'react'
import {
  AnalysisState,
  AgentResult,
  CoordinatorResult,
  PersonaResult,
  PolicyClassification,
  ConfidenceResult,
  AnalysisSeal,
} from './types'
import Stage1Input from './components/Stage1Input'
import Stage2Simulation from './components/Stage2Simulation'
import Stage3Findings from './components/Stage3Findings'
import ValidationExample from './components/ValidationExample'
import { API_BASE } from './config'

const INITIAL_STATE: AnalysisState = {
  stage: 'idle',
  agents: [],
  activeAgent: 0,
  personaCount: 0,
  mode: 'demo',
  personaResults: [],
  personaProgress: { current: 0, total: 0 },
  coordinator: null,
  overall_severity: '',
  policy_title: '',
  classification: null,
  confidence: null,
  seal: null,
}

const TABS = ['Analyse Policy', 'Historical Validation']

export default function App() {
  const [state, setState] = useState<AnalysisState>(INITIAL_STATE)
  const [activeTab, setActiveTab] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const abortRef = useRef<AbortController | null>(null)

  const startAnalysis = useCallback(async (title: string, description: string, mode: 'demo' | 'full') => {
    abortRef.current?.abort()
    const controller = new AbortController()
    abortRef.current = controller
    setError(null)
    setState({
      ...INITIAL_STATE,
      stage: 'agents',
      mode,
      policy_title: title,
    })

    try {
      const response = await fetch(
        `${API_BASE}/api/analyse/stream?title=${encodeURIComponent(title)}&description=${encodeURIComponent(description)}&mode=${mode}`,
        { signal: controller.signal }
      )

      if (!response.ok || !response.body) {
        throw new Error('Stream connection failed')
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() ?? ''

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          try {
            const event = JSON.parse(line.slice(6).trim())

            if (event.type === 'agent') {
              setState(prev => ({
                ...prev,
                agents: [...prev.agents, event.data as AgentResult],
                activeAgent: prev.activeAgent + 1,
              }))
            }

            if (event.type === 'classification') {
              setState(prev => ({ ...prev, classification: event.data as PolicyClassification }))
            }

            if (event.type === 'coordinator') {
              setState(prev => ({ ...prev, coordinator: event.data as CoordinatorResult }))
            }

            if (event.type === 'persona') {
              setState(prev => ({
                ...prev,
                stage: 'personas',
                personaResults: [...prev.personaResults, event.data as PersonaResult],
                personaProgress: {
                  current: (event.index as number) + 1,
                  total: event.total as number,
                },
                personaCount: prev.personaCount + 1,
              }))
            }

            if (event.type === 'done') {
              setState(prev => ({
                ...prev,
                overall_severity: event.overall_severity as string,
                policy_title: (event.policy_title as string) ?? prev.policy_title,
                confidence: (event.confidence as ConfidenceResult) ?? prev.confidence,
                seal: (event.seal as AnalysisSeal) ?? prev.seal,
                stage: 'complete',
              }))
            }
          } catch (e) {
            console.error('SSE parse error:', e)
          }
        }
      }
    } catch (e) {
      if ((e as Error).name === 'AbortError') {
        return
      }
      setError('Analysis failed — check that the backend is running on port 8000.')
      setState(prev => ({ ...prev, stage: 'idle' }))
    }
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
              <Stage1Input onSubmit={startAnalysis} error={error} classification={state.classification} />
            )}

            {/* Stage 2 — agents + personas */}
            {(state.stage === 'agents' || state.stage === 'personas') && (
              <Stage2Simulation state={state} />
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
