export interface AgentResult {
  agent: string
  risks: string[]
  opportunities: string[]
  severity: 'High' | 'Medium' | 'Low'
  most_affected: string
  summary: string
}

export interface CoordinatorResult {
  verdict: string
  key_risk: string
  blind_spot: string
  sharpest_disagreement: string
  confidence: 'High' | 'Medium' | 'Low'
}

export interface AnalysisState {
  stage: 'idle' | 'agents' | 'personas' | 'complete'
  agents: AgentResult[]
  activeAgent: number
  personaCount: number
  coordinator: CoordinatorResult | null
  overall_severity: string
  policy_title: string
}

export interface ValidationResult {
  policy_title: string
  note: string
  agents: AgentResult[]
  coordinator: CoordinatorResult
  overall_severity: string
}
