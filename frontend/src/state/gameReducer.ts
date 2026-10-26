// The one reducer shared by live and replay: core view + stats + insights, in one pass.
import type { GameEvent } from '../api/types'
import { captionReducer } from './captionReducer'
import { coreReducer } from './coreReducer'
import { insightReducer } from './insightReducer'
import { statsReducer } from './statsReducer'
import { emptyView, type GameView } from './viewTypes'

export function gameReducer(v: GameView, ev: GameEvent): GameView {
  return captionReducer(insightReducer(statsReducer(coreReducer(v, ev), ev), ev), ev)
}

export function reduceAll(events: GameEvent[], from: GameView = emptyView): GameView {
  return events.reduce(gameReducer, from)
}
