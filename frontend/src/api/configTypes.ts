// Game configuration (lobby -> POST /api/games) and stored game rows.

export interface SeatConfig { model_id: string; name?: string; persona?: string | null }

export interface GameConfig {
  mode: string
  seats: SeatConfig[]
  deck?: string[] | null
  seed?: number | null
  max_cost_usd: number
  quick_reasoning: number
  deep_reasoning: number
  narrator_model?: string | null
  reveal_on_death: boolean
  reveal_models: boolean
  fake: boolean
  fake_delay: number
  talk?: { rounds: number }
}

export interface GameRow {
  id: string
  mode: string
  seed: number
  status: string
  winner: string | null
  rounds: number
  cost_usd: number
  created_at: number
  ended_at: number | null
  config: GameConfig
}
