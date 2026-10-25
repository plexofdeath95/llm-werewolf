// Tooltip texts, shared so every panel explains things the same way.
import { roleEmoji, roleLabel, shownRole } from '../state/selectors'
import type { GameView } from '../state/viewTypes'

const CHANNELS: Record<string, string> = {
  'wolf den': 'Private werewolf chat: only the pack can see this.',
  masons: 'Private Mason chat: only the Masons can see this.',
  lovers: 'Private chat between the two Lovers.',
  "cupid's lovers": "Private chat between Cupid's two lovers.",
  creed: 'Private Creed chat: only Creed members can see this.',
  cult: 'Private cult chat: only cult members can see this.',
  'last words': 'Final words of a player the village just voted out.',
  night: 'A secret night action: only this player knows about it.',
  day: 'A secret day action (e.g. the Mayor preparing a power).',
}

export function channelTip(channel?: string): string {
  if (!channel || channel === 'public') return 'Said in public: everyone at the table heard this.'
  return CHANNELS[channel] ?? `Private channel "${channel}": only its members see this.`
}

export function urgencyTip(u: number, thought?: string): string {
  const mood = u <= 2 ? 'happy to stay quiet' : u <= 5 ? 'has something to add'
    : u <= 7 ? 'wants the floor' : 'must respond right now'
  return `Urgency ${u}/10: ${mood}.` + (thought ? `\n\n"${thought}"` : '')
}

export function roleTip(v: GameView, role?: string): string {
  if (!role) return 'Role unknown (hidden until revealed or god view).'
  const r = v.mode?.roles?.[role]
  return `${roleEmoji(v, role)} ${roleLabel(v, role)}` + (r?.team ? ` (${r.team})` : '')
    + (r?.summary ? `\n${r.summary}` : '')
}

export function playerTip(v: GameView, pid: string, god: boolean): string {
  const p = v.players[pid]
  if (!p) return pid
  const lines = [`${p.name} · played by ${p.model?.label ?? p.model_id}`]
  const role = shownRole(p, god)
  if (role) lines.push(roleTip(v, role))
  if (!p.alive) lines.push(`☠ Died in round ${p.diedRound ?? '?'}: ${p.deathCause ?? 'dead'}`)
  lines.push('Click to see their thoughts.')
  return lines.join('\n')
}

export const INTERRUPT_TIP = 'Interrupted: they were just named and urgently jumped in to reply.'
export const NUDGE_TIP = "Called on by the moderator: they hadn't spoken yet, and everyone gets heard."
