// Per-player counters: messages, interrupts, avg urgency, cost, avg latency.
import { usd } from '../../lib/format'
import { avgLatency, avgUrgency } from '../../state/statsReducer'
import { PlayerName } from './PlayerName'
import type { StatsProps } from './StatsPanel'

export function PlayersTab({ view, onSelect }: StatsProps) {
  return (
    <table className="stat-table counters">
      <thead>
        <tr>
          <th>Player</th><th title="messages">💬</th><th title="interrupts">⚡</th>
          <th title="average urgency">🔥</th><th title="total cost">💸</th><th title="average latency">⏱</th>
        </tr>
      </thead>
      <tbody>
        {view.order.map((id) => {
          const s = view.stats[id]
          return (
            <tr key={id}>
              <td>
                <PlayerName view={view} pid={id} onSelect={onSelect} />
                <div className="muted small">{view.players[id]?.model?.label}</div>
              </td>
              <td>{s?.messages ?? 0}</td>
              <td>{s?.interrupts ?? 0}</td>
              <td>{avgUrgency(s).toFixed(1)}</td>
              <td>{usd(s?.cost)}</td>
              <td>{avgLatency(s).toFixed(1)}s</td>
            </tr>
          )
        })}
      </tbody>
    </table>
  )
}
