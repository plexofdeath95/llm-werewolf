// Big, short-lived banner for deaths, eliminations and the winner (replays per event seq).
import type { GameView } from '../state/viewTypes'

export function DramaBanner({ view }: { view: GameView }) {
  const b = view.insight.banner
  if (!b) return null
  return <div key={b.seq} className={`drama-banner ${b.kind}`}>{b.text}</div>
}
