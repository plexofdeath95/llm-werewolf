// Past (and running) games; open any of them to watch live or replay.
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import { useFetch } from '../hooks/useFetch'
import { useMusic } from '../hooks/useMusic'
import { teamColor } from '../lib/colors'
import { usd, when } from '../lib/format'

const STATUS: Record<string, string> = {
  running: '🟢 live', finished: '🏁 finished', error: '💥 error', cancelled: '⛔ cancelled',
}

export function History() {
  useMusic('lobby')
  const games = useFetch(api.games)
  const models = useFetch(api.models)
  const label = (id: string) => models.data?.models.find((m) => m.id === id)
  return (
    <div className="page history">
      <div className="card-head">
        <h2>📚 Game history</h2>
        <button onClick={games.reload}>↻ refresh</button>
      </div>
      {games.error && <div className="error-box">⚠️ {games.error}</div>}
      <table className="history-table">
        <thead>
          <tr><th>When</th><th>Mode</th><th>Status</th><th>Winner</th><th>Rounds</th><th>Cost</th><th>Players</th><th /></tr>
        </thead>
        <tbody>
          {games.data?.map((g) => (
            <tr key={g.id}>
              <td>{when(g.created_at)}</td>
              <td>{g.mode}{g.config?.fake ? ' 🧪' : ''}</td>
              <td>{STATUS[g.status] ?? g.status}</td>
              <td style={{ color: teamColor(g.winner ?? '') }}>{g.winner ?? '—'}</td>
              <td>{g.rounds}</td>
              <td>{usd(g.cost_usd)}</td>
              <td className="models-cell">
                {g.config?.seats?.map((s, i) => (
                  <span key={i} className="mini-swatch" title={label(s.model_id)?.label ?? s.model_id}
                    style={{ background: label(s.model_id)?.color ?? '#666' }} />
                ))}
              </td>
              <td><Link className="open-link" to={`/game/${g.id}`}>{g.status === 'running' ? '👀 watch' : '▶ replay'}</Link></td>
            </tr>
          ))}
        </tbody>
      </table>
      {games.data && !games.data.length && <p className="muted">No games yet. Start one from the lobby!</p>}
    </div>
  )
}
