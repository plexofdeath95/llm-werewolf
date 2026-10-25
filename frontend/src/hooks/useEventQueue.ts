// Pacing: reveals events one at a time with human-friendly delays.
// Used for BOTH live (follows the growing stream, fast-forwards backlogs) and replay.
import { useCallback, useEffect, useState } from 'react'
import type { GameEvent } from '../api/types'

const BACKLOG_FAST = 25 // live: beyond this many unseen events, fast-forward

export function eventDelay(ev: GameEvent): number {
  const len = ev.text?.length ?? 0
  switch (ev.kind) {
    case 'setup': return 300
    case 'phase': return 1600
    case 'speech': return 1100 + Math.min(len * 28, 5200)
    case 'moderator': return 700 + Math.min(len * 14, 2200)
    case 'narration': return 1400 + Math.min(len * 22, 3000)
    case 'thought': return Math.min(Math.max((ev.data.latency ?? 1) * 140, 160), 1400)
    case 'reaction': return 380
    case 'vote': return 650
    case 'vote_result': return 1500
    case 'death': return 2200
    case 'reveal': return 1300
    case 'action': return 900
    case 'game_over': return 500
    default: return 250
  }
}

export function useEventQueue(events: GameEvent[], live: boolean) {
  const [cursor, setCursor] = useState(0)
  const [playing, setPlaying] = useState(true)
  const [speed, setSpeed] = useState(1)

  useEffect(() => {
    if (!playing || cursor >= events.length) return
    const backlog = events.length - cursor
    const base = eventDelay(events[cursor]) / speed
    const delay = live && backlog > BACKLOG_FAST ? 12 : base
    const t = setTimeout(() => setCursor((c) => Math.min(c + 1, events.length)), delay)
    return () => clearTimeout(t)
  }, [cursor, events, playing, speed, live])

  const seek = useCallback((index: number) => {
    setCursor(Math.max(0, Math.min(index, events.length)))
  }, [events.length])

  return {
    cursor,
    total: events.length,
    next: events[cursor] as GameEvent | undefined,
    playing,
    speed,
    setSpeed,
    play: () => setPlaying(true),
    pause: () => setPlaying(false),
    toggle: () => setPlaying((p) => !p),
    seek,
    toEdge: () => setCursor(events.length),
    atEdge: cursor >= events.length - 1,
  }
}

export type EventQueue = ReturnType<typeof useEventQueue>
