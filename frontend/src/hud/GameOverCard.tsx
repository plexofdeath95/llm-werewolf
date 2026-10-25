// End-of-game card: winning team + every player's role and model.
import { useState } from 'react'
import { teamColor } from '../lib/colors'
import { usd } from '../lib/format'
import { roleEmoji, roleLabel } from '../state/selectors'
import type { GameView } from '../state/viewTypes'

const WIN_EMOJI: Record<string, string> = { village: '🏡', wolves: '🐺', neutral: '🃏' }

export function GameOverCard({ view }: { view: GameView }) {
  const [closed, setClosed] = useState(false)
  if (!view.winner || closed) return null
  return (
    <div className="gameover">
      <div className="gameover-card" style={{ borderColor: teamColor(view.winner) }}>
        <button className="icon-btn close" onClick={() => setClosed(true)}>✕</button>
        <div className="gameover-emoji">{WIN_EMOJI[view.winner] ?? '🏆'}</div>
        <h2 style={{ color: teamColor(view.winner) }}>The {view.winner} win!</h2>
        <div className="muted">{view.round} rounds · {usd(view.spent)} spent</div>
        <table className="stat-table">
          <tbody>
            {view.order.map((id) => {
              const p = view.players[id]
              return (
                <tr key={id} className={p.alive ? '' : 'dead'}>
                  <td style={{ color: p.model?.color }}><b>{p.name}</b></td>
                  <td>{p.model?.label}</td>
                  <td style={{ color: teamColor(p.team) }}>{roleEmoji(view, p.role)} {roleLabel(view, p.role)}</td>
                  <td>{p.alive ? '🙂 alive' : `💀 R${p.diedRound ?? '?'}`}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
