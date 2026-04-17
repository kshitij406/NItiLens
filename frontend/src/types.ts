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
  mode: 'demo' | 'full'
  personaResults: PersonaResult[]
  personaProgress: PersonaProgress
  coordinator: CoordinatorResult | null
  overall_severity: string
  policy_title: string
}

export interface PersonaValidation {
  risk_index: number
  applies: boolean
  severity_for_me: number
  reason: string
}

export interface PersonaResult {
  persona_id: number
  name: string
  state: string
  occupation?: string
  caste_category?: string
  validations: PersonaValidation[]
  missed_risk: string | null
}

export interface PersonaProgress {
  current: number
  total: number
}

export interface ValidationResult {
  policy_title: string
  note: string
  agents: AgentResult[]
  coordinator: CoordinatorResult
  overall_severity: string
}
