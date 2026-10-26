// Badges floating over a head: votes received (vote phase) and, in god view, how many
// players suspect them most. Labels instead of lines: readable from one screenshot.
import { nameOf } from '../state/selectors'
import type { GameView } from '../state/viewTypes'

export interface HeadBadgesProps {
  view: GameView
  pid: string
  votes: number
  suspectedBy: string[]
}

export function HeadBadges({ view, pid, votes, suspectedBy }: HeadBadgesProps) {
  const out = view.voteResult?.eliminated === pid
  if (!votes && !suspectedBy.length) return null
  const name = nameOf(view, pid)
  return (
    <div className="head-badges">
      {votes > 0 && (
        <span className={`hb vote${out ? ' out' : ''}`}
          data-tip={`${votes} vote${votes > 1 ? 's' : ''} to eliminate ${name}`}>🗳️ {votes}</span>
      )}
      {suspectedBy.length > 0 && (
        <span className="hb sus" data-tip={`Suspected most by ${suspectedBy.map((id) => nameOf(view, id)).join(', ')}`}>
          🎯 {suspectedBy.length}
        </span>
      )}
    </div>
  )
}
