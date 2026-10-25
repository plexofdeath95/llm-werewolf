// Round + phase, phase timeline, and the alive/dead roster.
import { teamColor } from '../../lib/colors'
import { roleTip } from '../../lib/tips'
import { roleEmoji, roleLabel, shownRole } from '../../state/selectors'
import { PlayerName } from './PlayerName'
import type { StatsProps } from './StatsPanel'

export function OverviewTab({ view, god, onSelect }: StatsProps) {
  const marks = view.timeline.filter((m) => m.phase === 'night' || m.phase === 'dawn')
  return (
    <div>
      <div className="stat-row">
        <b>Round {view.round}</b> · {view.phaseLabel}
      </div>
      <div className="timeline">
        {marks.map((m, i) => (
          <span key={m.seq} className={`tl-chip${m.phase === 'night' ? ' night' : ''}${i === marks.length - 1 ? ' now' : ''}`}>
            {m.phase === 'night' ? '🌙' : '☀️'} {m.label}
          </span>
        ))}
      </div>
      <table className="stat-table">
        <tbody>
          {view.order.map((pid) => {
            const p = view.players[pid]
            const role = shownRole(p, god)
            return (
              <tr key={pid} className={p.alive ? '' : 'dead'}>
                <td><PlayerName view={view} pid={pid} onSelect={onSelect} /></td>
                <td style={{ color: role ? teamColor(view.mode?.roles?.[role]?.team) : undefined }}
                  data-tip={roleTip(view, role)}>
                  {role ? `${roleEmoji(view, role)} ${roleLabel(view, role)}` : '❔'}
                </td>
                <td className="muted">
                  {p.alive ? 'alive' : `☠ R${p.diedRound ?? '?'} · ${p.deathCause ?? 'dead'}`}
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
