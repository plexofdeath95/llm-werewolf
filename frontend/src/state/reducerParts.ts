// Helpers used by gameReducer; each copies only the slice it changes.
import type { GameEvent } from '../api/types'
import type { Bubble, GameView, MindEntry } from './viewTypes'

const MIND_CAP = 400

export function setBubble(v: GameView, pid: string, bubble: Bubble): void {
  v.bubbles = { ...v.bubbles, [pid]: bubble }
}

export function addMind(
  v: GameView, ev: GameEvent, kind: MindEntry['kind'], text: string,
  extra: Partial<MindEntry> = {},
): GameView {
  if (!ev.actor) return v
  const entry: MindEntry = { seq: ev.seq, round: ev.round, phase: ev.phase, kind, text, ...extra }
  const list = v.mind[ev.actor] ?? []
  const trimmed = list.length >= MIND_CAP ? list.slice(list.length - MIND_CAP + 1) : list
  v.mind = { ...v.mind, [ev.actor]: [...trimmed, entry] }
  return v
}
