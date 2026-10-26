// Insight reducer: who suspects whom, public role claims, emote pops and drama banners.
import type { GameEvent } from '../api/types'
import type { Emote } from './insightTypes'
import type { GameView } from './viewTypes'

const SAVED = /saved them|nursed you|fought off|protection held|kept you safe|gave their life/i

function pidByName(v: GameView, name: unknown): string | undefined {
  const key = String(name ?? '').trim().toLowerCase()
  if (!key) return undefined
  return Object.values(v.players).find((p) => p.name.toLowerCase() === key)?.id
}

/** Players named in a line (whole-word match), excluding the speaker. */
export function namedIn(v: GameView, text: string, speaker: string | null): string[] {
  return Object.values(v.players)
    .filter((p) => p.id !== speaker && new RegExp(`\\b${p.name}\\b`, 'i').test(text))
    .map((p) => p.id)
}

/** A claimed role given as an id ("seer") or a label ("Seer", "Jack of All Trades"). */
function roleId(v: GameView, claim: unknown): string | undefined {
  const key = String(claim ?? '').trim().toLowerCase()
  if (!key || !v.mode?.roles) return undefined
  const roles = v.mode.roles
  return roles[key.replace(/ /g, '_')] ? key.replace(/ /g, '_')
    : Object.keys(roles).find((id) => roles[id].label.toLowerCase() === key)
}

function pop(v: GameView, pid: string | null | undefined, e: Omit<Emote, 'seq'>, seq: number) {
  if (!pid || !v.players[pid]) return
  v.insight = { ...v.insight, emotes: { ...v.insight.emotes, [pid]: { ...e, seq } } }
}

function suspect(v: GameView, ev: GameEvent) {
  const target = pidByName(v, ev.data.suspect)
  if (!ev.actor || !target || target === ev.actor) return
  v.insight = { ...v.insight, suspects: { ...v.insight.suspects, [ev.actor]: target } }
}

/** Expects `v` to already be a fresh top-level copy (coreReducer returns one). */
export function insightReducer(v: GameView, ev: GameEvent): GameView {
  const priv = ev.visible_to !== null
  switch (ev.kind) {
    case 'reaction':
      suspect(v, ev)
      return v
    case 'speech': {
      suspect(v, ev)
      const claim = roleId(v, ev.data.claim)
      if (ev.actor && claim && !priv) {
        v.insight = { ...v.insight, claims: { ...v.insight.claims, [ev.actor]: claim } }
      }
      for (const pid of namedIn(v, ev.text, ev.actor)) {
        pop(v, pid, { emoji: '😠', tip: `Named by ${v.players[ev.actor ?? '']?.name ?? 'someone'}`, private: priv }, ev.seq)
      }
      if (ev.data.interrupt) pop(v, ev.actor, { emoji: '⚡', tip: 'Interrupted!', private: priv }, ev.seq)
      else if (ev.data.nudged) pop(v, ev.actor, { emoji: '👉', tip: 'Called on by the moderator', private: priv }, ev.seq)
      return v
    }
    case 'action':
      if (ev.data.action === 'result' && SAVED.test(ev.text)) {
        pop(v, ev.actor, { emoji: '🛡️', tip: ev.text, private: true }, ev.seq)
      }
      return v
    case 'death': {
      pop(v, ev.target, { emoji: '💀', tip: ev.text, private: false }, ev.seq)
      const voted = String(ev.data.cause ?? '').includes('vote')
      const name = v.players[ev.target ?? '']?.name ?? 'Someone'
      v.insight = { ...v.insight, banner: voted
        ? { text: `⚖️ ${name} is eliminated`, seq: ev.seq, kind: 'elimination' }
        : { text: `💀 ${name} was found dead`, seq: ev.seq, kind: 'death' } }
      return v
    }
    case 'game_over':
      v.insight = { ...v.insight, banner: { text: `🏆 The ${ev.data.winner ?? 'nobody'} win!`, seq: ev.seq, kind: 'winner' } }
      return v
    default:
      return v
  }
}

/** How many living players currently suspect `pid` most. */
export function heat(v: GameView, pid: string): string[] {
  return Object.entries(v.insight.suspects)
    .filter(([who, target]) => target === pid && v.players[who]?.alive)
    .map(([who]) => who)
}
