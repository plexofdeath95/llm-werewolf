// Read-side helpers over GameView / event lists (visibility, labels, marks).
import type { GameEvent } from '../api/types'
import type { Bubble, GameView, PlayerView } from './viewTypes'

export function visibleFeed(v: GameView, god: boolean): GameEvent[] {
  return god ? v.feed : v.feed.filter((e) => e.visible_to === null)
}

export function visibleBubble(b: Bubble | undefined, god: boolean): Bubble | undefined {
  if (!b) return undefined
  if (god) return b
  return b.private || b.kind === 'thought' ? undefined : b
}

/** Role shown on a name tag: always in god view, else only once revealed. */
export function shownRole(p: PlayerView, god: boolean): string | undefined {
  return god ? p.role : p.revealedRole
}

export function roleEmoji(v: GameView, role: string | undefined): string {
  if (!role) return ''
  return v.mode?.roles?.[role]?.emoji ?? '❔'
}

export function roleLabel(v: GameView, role: string | undefined): string {
  if (!role) return ''
  return v.mode?.roles?.[role]?.label ?? role
}

export function nameOf(v: GameView, pid: string | null | undefined): string {
  if (!pid) return 'nobody'
  return v.players[pid]?.name ?? pid
}

export const isNight = (phase: string) => phase === 'night'

export interface PhaseMark { index: number; label: string; night: boolean }

/** Seek targets: index into the event list of every PHASE event. */
export function phaseMarks(events: GameEvent[]): PhaseMark[] {
  const marks: PhaseMark[] = []
  events.forEach((e, index) => {
    if (e.kind === 'phase') marks.push({ index, label: e.text, night: e.data.phase === 'night' })
  })
  return marks
}
