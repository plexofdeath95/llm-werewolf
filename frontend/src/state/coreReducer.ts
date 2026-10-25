// Core reducer: players, phase, bubbles, reactions, mind, arcs (stats live in statsReducer).
import type { GameEvent, SetupPlayer } from '../api/types'
import { addArcs, addMind, setBubble } from './reducerParts'
import type { GameView, PlayerView } from './viewTypes'

const FEED_KINDS = new Set([
  'phase', 'moderator', 'narration', 'speech', 'vote', 'vote_result', 'action',
  'death', 'reveal', 'status', 'error', 'game_over',
])

export function coreReducer(v: GameView, ev: GameEvent): GameView {
  const next: GameView = { ...v, lastSeq: ev.seq }
  if (FEED_KINDS.has(ev.kind)) next.feed = [...v.feed, ev]
  const isPrivate = ev.visible_to !== null
  switch (ev.kind) {
    case 'setup': {
      const list = (ev.data.players ?? []) as SetupPlayer[]
      next.players = Object.fromEntries(list.map((p) => [p.id, { ...p } as PlayerView]))
      next.order = [...list].sort((a, b) => a.seat - b.seat).map((p) => p.id)
      next.mode = ev.data.mode
      return next
    }
    case 'phase':
      next.phase = ev.data.phase ?? ev.phase
      next.phaseLabel = ev.text
      next.round = ev.round
      next.bubbles = {}
      next.reactions = {}
      next.roundOpen = false
      next.speaker = undefined
      if (next.phase === 'night' || next.phase === 'discussion') next.arcs = []
      return next
    case 'reaction': {
      if (!v.roundOpen) next.reactions = {}
      next.roundOpen = true
      const r = { urgency: ev.data.urgency ?? 0, thought: ev.data.thought ?? '',
        message: ev.data.message ?? '', seq: ev.seq, channel: ev.data.channel }
      next.reactions = { ...next.reactions, [ev.actor!]: r }
      setBubble(next, ev.actor!, { kind: 'thought', text: r.thought, seq: ev.seq,
        urgency: r.urgency, channel: r.channel, private: true })
      return addMind(next, ev, 'reaction', r.thought, { urgency: r.urgency })
    }
    case 'speech':
      next.roundOpen = false
      next.speaker = ev.actor ?? undefined
      if (ev.data.interrupt) next.interruptSeq = ev.seq
      next.bubbles = {}
      setBubble(next, ev.actor!, { kind: 'speech', text: ev.text, seq: ev.seq,
        interrupt: !!ev.data.interrupt, channel: ev.data.channel, private: isPrivate })
      return ev.data.thought ? addMind(next, ev, 'speech', ev.data.thought) : next
    case 'thought':
      next.spent = typeof ev.data.spent === 'number' ? ev.data.spent : v.spent
      return addMind(next, ev, 'thought', ev.text, {
        cost: ev.data.cost, latency: ev.data.latency, schema: ev.data.schema })
    case 'vote': {
      const target = ev.target ? v.players[ev.target]?.name ?? '?' : 'nobody'
      setBubble(next, ev.actor!, { kind: 'vote', text: `${ev.data.verb ?? 'votes for'} ${target}`,
        seq: ev.seq, channel: ev.data.channel, private: isPrivate })
      return addMind(next, ev, 'vote', ev.data.thought ?? ev.text)
    }
    case 'action':
      addArcs(next, ev)
      return ev.actor && ev.data.thought ? addMind(next, ev, 'action', ev.data.thought) : next
    case 'death':
    case 'reveal':
      return markPlayer(next, ev)
    case 'status':
      next.paused = !!ev.data.paused
      return next
    case 'game_over':
      next.winner = ev.data.winner ?? 'nobody'
      next.phaseLabel = `Game over: ${next.winner} win`
      return next
    default:
      return next
  }
}

function markPlayer(v: GameView, ev: GameEvent): GameView {
  const p = ev.target ? v.players[ev.target] : undefined
  if (!p) return v
  const upd: PlayerView = ev.kind === 'death'
    ? { ...p, alive: false, deathCause: ev.data.cause, diedRound: ev.round }
    : { ...p, revealedRole: ev.data.role ?? p.role }
  v.players = { ...v.players, [p.id]: upd }
  return v
}
