// Plain-language sentences for night actions: the dawn recap, the case board, walk captions.
import type { GameEvent } from '../api/types'
import { nameOf, roleEmoji, roleLabel } from '../state/selectors'
import type { GameView } from '../state/viewTypes'

const VERBS: Record<string, string> = {
  kill: 'attacked', shoot: 'shot at', alert: 'went on alert', heal: 'protected', guard: 'guarded',
  shield: 'shielded', jail: 'jailed', block: 'blocked', hide: 'hid', inspect: 'inspected',
  divine: 'read', scry: 'scried', watch: 'watched', follow: 'followed', peep: 'spied on',
  disguise: 'disguised', frame: 'framed', douse: 'doused', ignite: 'set the fires',
  hypnotize: 'hypnotized', transport: 'swapped', convert: 'tried to convert', drink: 'drank with',
}
const BY_CLASS: Record<string, string> = {
  killing: 'attacked', protection: 'protected', information: 'investigated', role_block: 'blocked',
  manipulation: 'meddled with', support: 'helped', role_copy: 'studied', influence: 'swayed',
  early: 'moved',
}

export const isAct = (ev?: GameEvent): ev is GameEvent =>
  !!ev && ev.kind === 'action' && !!ev.actor && ev.data.action !== 'result' && !!ev.data.cls

export function verb(ev: GameEvent): string {
  const a = String(ev.data.action ?? '')
  return VERBS[a] ?? BY_CLASS[String(ev.data.cls)] ?? `used ${a.replace(/_/g, ' ')} on`
}

function who(v: GameView, pid: string | null): string {
  const p = pid ? v.players[pid] : undefined
  return p ? `${roleEmoji(v, p.role)} ${p.name} (${roleLabel(v, p.role)})` : '?'
}

const targetsOf = (ev: GameEvent): string[] => ev.data.targets ?? (ev.target ? [ev.target] : [])

/** What the actor learned, from their dawn result note ("…is the Orphan." -> "Orphan"). */
export function learned(v: GameView, ev: GameEvent): string | undefined {
  const note = v.nightLog.find((e) => e.actor === ev.actor && e.data.action === 'result')
  const m = note?.text.match(/\bis (?:the |an? |NOT )?([A-Z][\w' -]+?)\.?$/)
  return m ? m[1] : undefined
}

/** "🐺 Alice (Alpha) attacked Dave" (+ " → Orphan" when they learned something). */
export function actSentence(v: GameView, ev: GameEvent): string {
  const targets = targetsOf(ev).map((t) => nameOf(v, t)).join(' & ')
  const found = learned(v, ev)
  return `${who(v, ev.actor)} ${verb(ev)}${targets ? ` ${targets}` : ''}${found ? ` → ${found}` : ''}`
}

/** Caption while the action is being walked out: "🐺 Alice sneaks to Dave's house". */
export function walkCaption(v: GameView, ev: GameEvent): string {
  const p = ev.actor ? v.players[ev.actor] : undefined
  const t = nameOf(v, targetsOf(ev)[0])
  const icon = p ? roleEmoji(v, p.role) : '🌙'
  const name = p?.name ?? '?'
  if (ev.data.movement === 'travel') return `👀 ${name} watches ${t}'s house`
  if (ev.data.movement === 'none') return `${icon} ${name} ${verb(ev)}${targetsOf(ev).length ? ` ${t}` : ''} from home`
  if (ev.data.cls === 'killing') return `${icon} ${name} sneaks to ${t}'s house`
  return `${icon} ${name} visits ${t}'s house (${String(ev.data.action ?? 'visit').replace(/_/g, ' ')})`
}

/** Tonight's (or last night's) acts in resolution order. */
export function nightActs(v: GameView): GameEvent[] {
  const seat = (e: GameEvent) => v.players[e.actor ?? '']?.seat ?? 0
  return v.nightLog.filter(isAct)
    .sort((a, b) => (a.data.order ?? 0) - (b.data.order ?? 0) || seat(a) - seat(b))
}
