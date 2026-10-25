// Clickable player name in model color (reused across all stats tabs).
import { playerTip } from '../../lib/tips'
import type { GameView } from '../../state/viewTypes'

export function PlayerName({ view, pid, onSelect }: {
  view: GameView; pid: string | null | undefined; onSelect?: (pid: string) => void
}) {
  if (!pid) return <span className="muted">nobody</span>
  const p = view.players[pid]
  return (
    <button className="pname" style={{ color: p?.model?.color }} onClick={() => onSelect?.(pid)}
      data-tip={playerTip(view, pid, false)}>
      {p?.name ?? pid}{p && !p.alive ? ' 👻' : ''}
    </button>
  )
}
