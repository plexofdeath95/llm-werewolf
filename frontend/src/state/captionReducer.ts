// "What's happening" in one plain sentence, updated per event. Private events (wolf den,
// night choices) produce a separate god-view caption so nothing secret leaks to the public one.
import type { GameEvent } from '../api/types'
import { namedIn } from './insightReducer'
import { nameOf, roleEmoji, roleLabel, voteTally } from './selectors'
import type { GameView } from './viewTypes'

function set(v: GameView, text: string, seq: number, secret: boolean) {
  v.insight = { ...v.insight, caption: { ...v.insight.caption, [secret ? 'secret' : 'public']: { text, seq } } }
}

function speechCaption(v: GameView, ev: GameEvent, god: boolean): string {
  const name = nameOf(v, ev.actor)
  const claim = v.insight.claims[ev.actor ?? '']
  const who = claim ? `${name} (claims ${roleEmoji(v, claim)} ${roleLabel(v, claim)})` : name
  const named = namedIn(v, ev.text, ev.actor)
  const accused = god && named.find((pid) => nameOf(v, pid).toLowerCase() === String(ev.data.suspect ?? '').toLowerCase())
  if (ev.data.channel === 'last words') return `🪦 ${name}'s last words`
  if (ev.data.nudged) return `👉 ${who} is called on to speak`
  const jump = !!ev.data.interrupt
  const lead = jump ? `⚡ ${who} jumps in` : `🗣️ ${who}`
  if (accused) return `${lead}${jump ? ' and' : ''} accuses ${nameOf(v, accused)}`
  if (named.length) return `${lead}${jump ? ':' : ''} talks to ${named.map((p) => nameOf(v, p)).join(', ')}`
  return jump ? lead : `${lead} speaks`
}

function phaseCaption(ev: GameEvent): [string, string?] {
  const phase = String(ev.data.phase ?? ev.phase)
  const n = ev.round
  if (phase === 'night') return [`🌙 Night ${n}: the village sleeps…`, `🌙 Night ${n}: the wolves are choosing a victim…`]
  if (phase === 'dawn') return [`🌅 Day ${n}: the sun rises…`]
  if (phase === 'discussion') return [`☀️ Day ${n}: who is a werewolf? The village debates`]
  if (phase === 'vote') return [`🗳️ Day ${n}: everyone votes at the same time`]
  return [ev.text]
}

/** Expects `v` to already be a fresh top-level copy (coreReducer returns one). */
export function captionReducer(v: GameView, ev: GameEvent): GameView {
  const priv = ev.visible_to !== null
  switch (ev.kind) {
    case 'phase': {
      const [pub, secret] = phaseCaption(ev)
      set(v, pub, ev.seq, false)
      set(v, secret ?? pub, ev.seq, true)
      return v
    }
    case 'speech':
      set(v, (priv ? `🔒 [${ev.data.channel}] ` : '') + speechCaption(v, ev, priv), ev.seq, priv)
      if (!priv) set(v, speechCaption(v, ev, true), ev.seq, true)
      return v
    case 'vote': {
      const target = ev.target ? nameOf(v, ev.target) : 'nobody'
      if (priv) { set(v, `🔒 ${nameOf(v, ev.actor)} ${ev.data.verb ?? 'picks'} ${target}`, ev.seq, true); return v }
      const tally = Object.entries(voteTally(v, false)).sort((a, b) => b[1] - a[1])
        .map(([pid, k]) => `${nameOf(v, pid)} ${k}`).join(', ')
      set(v, `🗳️ ${nameOf(v, ev.actor)} → ${target}${tally ? ` (${tally})` : ''}`, ev.seq, false)
      return v
    }
    case 'vote_result':
      set(v, ev.data.eliminated
        ? `📊 ${nameOf(v, ev.data.eliminated)} gets the most votes: ${ev.text.replace(/^Votes: /, '')}`
        : `📊 No majority (${ev.text.replace(/^Votes: /, '')}): nobody is eliminated`, ev.seq, false)
      return v
    case 'death': {
      const voted = String(ev.data.cause ?? '').includes('vote')
      set(v, voted ? `⚖️ ${nameOf(v, ev.target)} is voted out`
        : `💀 ${nameOf(v, ev.target)} was found dead (${ev.data.cause ?? 'killed'})`, ev.seq, false)
      return v
    }
    case 'reveal': {
      const cap = v.insight.caption.public
      const tail = `they were the ${roleEmoji(v, ev.data.role)} ${roleLabel(v, ev.data.role)}`
      if (cap && cap.text.includes(nameOf(v, ev.target))) set(v, `${cap.text}: ${tail}`, ev.seq, false)
      return v
    }
    case 'moderator':
      if (!priv && ev.text.length <= 80) set(v, `🎙️ ${ev.text}`, ev.seq, false)
      return v
    case 'game_over':
      set(v, `🏆 The ${ev.data.winner ?? 'nobody'} win!`, ev.seq, false)
      return v
    default:
      return v
  }
}
