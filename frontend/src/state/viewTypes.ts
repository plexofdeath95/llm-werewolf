// The derived, render-ready view of a game at some point in its event stream.
import type { GameEvent, ModeInfo, SetupPlayer } from '../api/types'
import type { PlayerStats, TimelineMark, VoteView } from './statsTypes'

export type { PlayerStats, TimelineMark, VoteView }

export interface PlayerView extends SetupPlayer {
  revealedRole?: string
  deathCause?: string
  diedRound?: number
}

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

export interface Arc {
  seq: number
  from: string
  to: string
  cls: string
  action: string
  private: boolean
}

export interface GameView {
  players: Record<string, PlayerView>
  order: string[]
  mode?: ModeInfo
  round: number
  phase: string
  phaseLabel: string
  feed: GameEvent[]
  bubbles: Record<string, Bubble>
  reactions: Record<string, ReactionView>
  roundOpen: boolean
  speaker?: string
  interruptSeq?: number
  mind: Record<string, MindEntry[]>
  arcs: Arc[]
  spent: number
  paused: boolean
  winner?: string
  lastSeq: number
  // stats slices (statsReducer)
  timeline: TimelineMark[]
  talk: { order: string[]; counts: Record<string, number> }
  votes: Record<string, VoteView>
  voteResult?: { counts: Record<string, number>; eliminated: string | null; seq: number }
  nightLog: GameEvent[]
  stats: Record<string, PlayerStats>
}

export const emptyView: GameView = {
  players: {},
  order: [],
  round: 0,
  phase: 'setup',
  phaseLabel: 'Gathering at the tavern…',
  feed: [],
  bubbles: {},
  reactions: {},
  roundOpen: false,
  mind: {},
  arcs: [],
  spent: 0,
  paused: false,
  lastSeq: 0,
  timeline: [],
  talk: { order: [], counts: {} },
  votes: {},
  nightLog: [],
  stats: {},
}
