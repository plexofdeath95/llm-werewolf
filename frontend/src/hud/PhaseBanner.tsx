// Big phase title at the top: "🌙 Night 2" / "☀️ Day 2: discussion".
import { isNight } from '../state/selectors'
import type { GameView } from '../state/viewTypes'

export function PhaseBanner({ view }: { view: GameView }) {
  const night = isNight(view.phase)
  const alive = view.order.filter((id) => view.players[id]?.alive).length
  return (
    <div className={`phase-banner${night ? ' night' : ''}`} key={view.phaseLabel}>
      <div className="phase-title">
        {view.winner ? '🏆' : night ? '🌙' : '☀️'} {view.phaseLabel}
      </div>
      {view.order.length > 0 && (
        <div className="phase-sub">{alive} of {view.order.length} alive · {view.mode?.name ?? ''}</div>
      )}
    </div>
  )
}
