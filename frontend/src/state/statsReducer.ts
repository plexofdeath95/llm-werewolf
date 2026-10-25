// Stats reducer: timeline, speaking queue, vote tally, night log, per-player counters.
import type { GameEvent } from '../api/types'
import type { GameView, PlayerStats } from './viewTypes'

const ZERO: PlayerStats = {
  messages: 0, interrupts: 0, urgencySum: 0, urgencyN: 0, cost: 0, latencySum: 0, calls: 0,
}

function bump(v: GameView, pid: string | null, patch: (s: PlayerStats) => Partial<PlayerStats>) {
  if (!pid) return
  const cur = v.stats[pid] ?? ZERO
  v.stats = { ...v.stats, [pid]: { ...cur, ...patch(cur) } }
}

/** Expects `v` to already be a fresh top-level copy (coreReducer returns one). */
export function statsReducer(v: GameView, ev: GameEvent): GameView {
  switch (ev.kind) {
    case 'phase': {
      const phase = String(ev.data.phase ?? ev.phase)
      v.timeline = [...v.timeline, { label: ev.text, phase, round: ev.round, seq: ev.seq }]
      v.talk = { order: [], counts: {} }
      v.votes = {}
      if (phase === 'vote') v.voteResult = undefined
      if (phase === 'night') v.nightLog = []
      return v
    }
    case 'speech': {
      const pid = ev.actor
      if (!pid) return v
      v.talk = {
        order: [...v.talk.order, pid],
        counts: { ...v.talk.counts, [pid]: (v.talk.counts[pid] ?? 0) + 1 },
      }
      bump(v, pid, (s) => ({ messages: s.messages + 1, interrupts: s.interrupts + (ev.data.interrupt ? 1 : 0) }))
      return v
    }
    case 'reaction':
      bump(v, ev.actor, (s) => ({ urgencySum: s.urgencySum + (ev.data.urgency ?? 0), urgencyN: s.urgencyN + 1 }))
      return v
    case 'thought':
      bump(v, ev.actor, (s) => ({
        cost: s.cost + (ev.data.cost ?? 0),
        latencySum: s.latencySum + (ev.data.latency ?? 0),
        calls: s.calls + 1,
      }))
      return v
    case 'vote':
      if (!ev.actor) return v
      v.votes = { ...v.votes, [ev.actor]: { target: ev.target, private: ev.visible_to !== null, verb: ev.data.verb } }
      return v
    case 'vote_result':
      v.voteResult = { counts: ev.data.counts ?? {}, eliminated: ev.data.eliminated ?? null, seq: ev.seq }
      return v
    case 'action':
      v.nightLog = [...v.nightLog, ev]
      return v
    default:
      return v
  }
}

export const avgUrgency = (s?: PlayerStats) => (s && s.urgencyN ? s.urgencySum / s.urgencyN : 0)
export const avgLatency = (s?: PlayerStats) => (s && s.calls ? s.latencySum / s.calls : 0)
