// A selected player's mind: thoughts, native reasoning, votes, with cost + latency per call.
import { teamColor } from '../lib/colors'
import { seconds, usd } from '../lib/format'
import { roleEmoji, roleLabel } from '../state/selectors'
import type { GameView, MindEntry } from '../state/viewTypes'

const ICON: Record<MindEntry['kind'], string> = {
  reaction: '💭', thought: '🧠', vote: '🗳️', speech: '🗣️', action: '🌙',
}

function Entry({ e }: { e: MindEntry }) {
  if (e.kind === 'thought' && !e.text) {
    return <div className="mind-meta">⏱ {e.schema} call · {seconds(e.latency)} · {usd(e.cost)}</div>
  }
  return (
    <div className={`mind-entry kind-${e.kind}`}>
      <div className="mind-head">
        {ICON[e.kind]} <span>R{e.round} · {e.phase}</span>
        {e.urgency !== undefined && <span className="mind-urg">urgency {e.urgency}</span>}
        {e.cost !== undefined && <span className="mind-cost">{seconds(e.latency)} · {usd(e.cost)}</span>}
      </div>
      <div className={e.kind === 'thought' ? 'mind-native' : 'mind-text'}>{e.text}</div>
    </div>
  )
}

export function MindPanel({ view, pid, god, onClose }: {
  view: GameView; pid: string; god: boolean; onClose: () => void
}) {
  const p = view.players[pid]
  if (!p) return null
  const entries = [...(view.mind[pid] ?? [])].reverse()
  const spent = entries.reduce((s, e) => s + (e.cost ?? 0), 0)
  return (
    <div className="panel mind">
      <div className="mind-title" style={{ borderColor: p.model?.color }}>
        <div>
          <b>{p.name}</b> {!p.alive && '👻'}
          <div className="mind-model" style={{ color: p.model?.color }}>{p.model?.label}</div>
        </div>
        {god && (
          <span className="mind-role" style={{ color: teamColor(p.team) }}>
            {roleEmoji(view, p.role)} {roleLabel(view, p.role)}
          </span>
        )}
        <button className="icon-btn" onClick={onClose} title="close">✕</button>
      </div>
      {p.persona && <div className="mind-persona">🎭 {p.persona}</div>}
      {!god ? (
        <div className="mind-locked">🔮 Turn on God view to read {p.name}'s mind.</div>
      ) : (
        <div className="mind-list">
          <div className="mind-meta">{entries.length} entries · {usd(spent)} spent</div>
          {entries.map((e) => <Entry key={`${e.seq}-${e.kind}`} e={e} />)}
        </div>
      )}
    </div>
  )
}
