// Per-player scene slices of GameView: bubbles, reactions, mind log.

export interface Bubble {
  kind: 'thought' | 'speech' | 'vote'
  text: string
  seq: number
  urgency?: number
  interrupt?: boolean
  channel?: string
  private: boolean
}

export interface ReactionView {
  urgency: number
  thought: string
  message: string
  seq: number
  channel?: string
}

export interface MindEntry {
  seq: number
  round: number
  phase: string
  kind: 'reaction' | 'thought' | 'vote' | 'speech' | 'action'
  text: string
  urgency?: number
  cost?: number
  latency?: number
  schema?: string
}
