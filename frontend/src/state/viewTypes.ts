// The derived, render-ready view of a game at some point in its event stream.
import type { GameEvent, ModeInfo, SetupPlayer } from '../api/types'
import { emptyInsight, type InsightView } from './insightTypes'
import type { Bubble, MindEntry, ReactionView } from './sceneTypes'
import type { PlayerStats, TimelineMark, VoteView } from './statsTypes'

export type { Bubble, MindEntry, ReactionView } from './sceneTypes'
export type { Banner, Emote, InsightView } from './insightTypes'
export type { PlayerStats, TimelineMark, VoteView }

export interface PlayerView extends SetupPlayer {
  revealedRole?: string
  deathCause?: string
  diedRound?: number
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
  // at-a-glance slices (insightReducer)
  insight: InsightView
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
  spent: 0,
  paused: false,
  lastSeq: 0,
  timeline: [],
  talk: { order: [], counts: {} },
  votes: {},
  nightLog: [],
  stats: {},
  insight: emptyInsight,
}
