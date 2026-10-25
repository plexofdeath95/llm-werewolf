// Wire types mirroring the backend (aiplays/core/events.py, api/*).

export type Kind =
  | 'setup' | 'phase' | 'moderator' | 'narration' | 'speech' | 'reaction' | 'thought'
  | 'vote' | 'vote_result' | 'action' | 'death' | 'reveal' | 'status' | 'error' | 'game_over'

export type Data = Record<string, any> // eslint-disable-line @typescript-eslint/no-explicit-any

export interface GameEvent {
  kind: Kind
  seq: number
  game_id: string
  round: number
  phase: string
  actor: string | null
  target: string | null
  text: string
  data: Data
  visible_to: string[] | null
  ts: number
}

export interface ModelEntry {
  id: string
  label: string
  slug: string
  provider: string
  color: string
  tier: string
}

export interface Persona { id: string; label: string; text: string }

export interface ModelsResponse {
  models: ModelEntry[]
  default_players: number
  personas: Persona[]
}

export type Team = 'village' | 'wolves' | 'neutral'

export interface RoleInfo {
  label: string
  team: Team
  emoji: string
  classes?: string[]
  summary?: string
}

export interface ModeInfo {
  id: string
  name: string
  min_players: number
  max_players: number
  roles: Record<string, RoleInfo>
}

export type { GameConfig, GameRow, SeatConfig } from './configTypes'

export interface SetupPlayer {
  id: string
  name: string
  seat: number
  model_id: string
  persona: string | null
  role: string
  team: Team
  alive: boolean
  model: ModelEntry
}

export type ServerMsg =
  | { type: 'event'; event: GameEvent }
  | { type: 'live'; actor: string; thought: string; draft: string | null }
  | { type: 'state'; live: boolean; paused: boolean; spent: number; max_usd: number }
  | { type: 'end' }

export type ControlAction = 'pause' | 'resume' | 'step' | 'raise_budget'
