// Speaking queue for the current discussion: order, counts, now speaking, thinking.
import { PlayerName } from './PlayerName'
import type { StatsProps } from './StatsPanel'

export function TalkTab({ view, thinking, onSelect }: StatsProps) {
  const alive = view.order.filter((id) => view.players[id]?.alive)
  const silent = alive.filter((id) => !view.talk.counts[id])
  return (
    <div>
      <div className="stat-row">
        🗣️ Now: {view.speaker ? <PlayerName view={view} pid={view.speaker} onSelect={onSelect} /> : <span className="muted">—</span>}
      </div>
      <div className="stat-row">
        🤔 Thinking:{' '}
        {thinking.size
          ? [...thinking].map((id) => <PlayerName key={id} view={view} pid={id} onSelect={onSelect} />)
          : <span className="muted">nobody</span>}
      </div>
      <div className="stat-label">Turn order this discussion ({view.talk.order.length} messages)</div>
      <div className="turn-order">
        {view.talk.order.map((id, i) => (
          <span key={i} className="turn-chip" style={{ borderColor: view.players[id]?.model?.color }}>
            {i + 1}. {view.players[id]?.name}
          </span>
        ))}
        {!view.talk.order.length && <span className="muted">No one has spoken yet.</span>}
      </div>
      <table className="stat-table">
        <tbody>
          {alive.map((id) => (
            <tr key={id}>
              <td><PlayerName view={view} pid={id} onSelect={onSelect} /></td>
              <td>{'💬'.repeat(Math.min(view.talk.counts[id] ?? 0, 8))} {view.talk.counts[id] ?? 0}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {silent.length > 0 && view.talk.order.length > 0 && (
        <div className="muted">Still silent: {silent.map((id) => view.players[id]?.name).join(', ')}</div>
      )}
    </div>
  )
}
