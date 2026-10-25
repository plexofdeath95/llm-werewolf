// The one reducer shared by live and replay: core view + derived stats, in one pass.
import type { GameEvent } from '../api/types'
import { coreReducer } from './coreReducer'
import { statsReducer } from './statsReducer'
import { emptyView, type GameView } from './viewTypes'

export function gameReducer(v: GameView, ev: GameEvent): GameView {
  return statsReducer(coreReducer(v, ev), ev)
}

export function reduceAll(events: GameEvent[], from: GameView = emptyView): GameView {
  return events.reduce(gameReducer, from)
}
