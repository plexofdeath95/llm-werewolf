// Reduce events[0:cursor] into a GameView incrementally (full rebuild only on backward seek).
import { useMemo, useRef } from 'react'
import type { GameEvent } from '../api/types'
import { gameReducer } from '../state/gameReducer'
import { emptyView, type GameView } from '../state/viewTypes'

// The ref-in-memo is deliberate: stepping the cursor applies one event (O(1)) instead of
// re-reducing the whole history every frame. Only a backward seek or a new stream rebuilds.
export function useGameView(events: GameEvent[], cursor: number): GameView {
  const memo = useRef<{ cursor: number; view: GameView; first?: GameEvent }>({
    cursor: 0, view: emptyView,
  })
  return useMemo(() => {
    const m = memo.current
    const restart = cursor < m.cursor || events[0] !== m.first
    let view = restart ? emptyView : m.view
    for (let i = restart ? 0 : m.cursor; i < cursor && i < events.length; i++) {
      view = gameReducer(view, events[i])
    }
    memo.current = { cursor: Math.min(cursor, events.length), view, first: events[0] }
    return view
  }, [events, cursor])
}

/** Players whose answers are queued just ahead of the cursor: show them "thinking". */
export function usePendingThinkers(events: GameEvent[], cursor: number): Set<string> {
  return useMemo(() => {
    const set = new Set<string>()
    for (let i = cursor; i < events.length && i < cursor + 40; i++) {
      const e = events[i]
      if (e.kind === 'thought' && e.actor) set.add(e.actor)
      else if (e.kind !== 'reaction' && e.kind !== 'vote' && e.kind !== 'error') break
    }
    return set
  }, [events, cursor])
}
