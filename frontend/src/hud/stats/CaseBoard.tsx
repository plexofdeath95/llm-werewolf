// "Who's who" at a glance: claims (and bluffs), suspicion heat, current votes, status.
import { actSentence, nightActs } from '../../lib/nightText'
import { channelTip, roleTip } from '../../lib/tips'
import { heat } from '../../state/insightReducer'
import { nameOf, roleEmoji, roleLabel, shownRole } from '../../state/selectors'
import { PlayerName } from './PlayerName'
import type { StatsProps } from './StatsPanel'

export function CaseBoard(props: StatsProps) {
  const acts = props.god ? nightActs(props.view) : []
  return (
    <div>
      <Board {...props} />
      {acts.length > 0 && <div className="stat-label">🌙 Last night</div>}
      <ol className="night-log">{acts.map((ev) => <li key={ev.seq}>{actSentence(props.view, ev)}</li>)}</ol>
    </div>
  )
}

function Board({ view, god, onSelect }: StatsProps) {
  return (
    <table className="stat-table case-board">
      <thead>
        <tr>
          <th>Player</th>
          <th data-tip="Role they publicly claimed (🤥 = bluff, god view)">Claim</th>
          {god && <th data-tip="How many living players suspect them most">🎯</th>}
          <th data-tip="Who they voted for this round">🗳️</th>
          <th data-tip="Alive, or dead with their revealed role">Status</th>
        </tr>
      </thead>
      <tbody>
        {view.order.map((pid) => {
          const p = view.players[pid]
          const claim = view.insight.claims[pid]
          const bluff = god && claim && claim !== p.role
          const sus = god ? heat(view, pid) : []
          const vote = view.votes[pid]
          const role = shownRole(p, god)
          const showVote = vote && (god || !vote.private)
          return (
            <tr key={pid} className={p.alive ? '' : 'dead'}>
              <td>
                <PlayerName view={view} pid={pid} onSelect={onSelect} />
                <div className="case-model" style={{ color: p.model?.color }}>{p.model?.label}</div>
              </td>
              <td data-tip={claim ? `Claims ${roleLabel(view, claim)}${bluff ? ` (really ${roleLabel(view, p.role)})` : ''}` : 'No claim yet'}>
                {claim ? `${roleEmoji(view, claim)}${bluff ? ' 🤥' : ''}` : <span className="muted">—</span>}
              </td>
              {god && (
                <td className={sus.length ? 'hot' : 'muted'}
                  data-tip={sus.length ? `Suspected most by ${sus.map((id) => nameOf(view, id)).join(', ')}` : 'Nobody suspects them most'}>
                  {sus.length || '·'}
                </td>
              )}
              <td data-tip={showVote ? channelTip(vote.private ? 'night' : 'public') : 'No vote yet'}>
                {showVote ? nameOf(view, vote.target) : ''}
              </td>
              <td data-tip={roleTip(view, role)}>
                {p.alive ? `✓ ${role ? roleEmoji(view, role) : ''}` : `☠ ${roleEmoji(view, p.revealedRole ?? role)}`}
              </td>
            </tr>
          )
        })}
      </tbody>
    </table>
  )
}
