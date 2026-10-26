// The tag under each avatar. At rest: name, model and a claim chip. Inline count chips show
// only when relevant: 🗳️ votes received (vote phase), 🎯 suspicion (god view, by day).
// The god-view role peeks out on hover; a revealed role (dead players) always shows.
import { cameraHold } from '../lib/cameraHold'
import { playerTip, roleTip } from '../lib/tips'
import { nameOf, roleEmoji, roleLabel, shownRole } from '../state/selectors'
import type { GameView, PlayerView } from '../state/viewTypes'

export interface NameTagProps {
  view: GameView
  player: PlayerView
  god: boolean
  suspectedBy: string[]
  votes: number
  compact: boolean // night: just the name, so tags don't crowd the walk
  dim: boolean // someone else is walking
  onSelect: (pid: string) => void
}

export function NameTag({ view, player, god, suspectedBy, votes, compact, dim, onSelect }: NameTagProps) {
  const role = shownRole(player, god)
  const revealed = !!player.revealedRole
  const color = player.model?.color ?? '#999'
  const claim = view.insight.claims[player.id]
  const bluff = god && claim && claim !== player.role
  const vote = view.phase === 'vote' ? view.votes[player.id] : undefined
  const showVote = vote && (god || !vote.private)
  const heatTip = suspectedBy.length
    ? `\nSuspected most by: ${suspectedBy.map((id) => nameOf(view, id)).join(', ')}` : ''
  return (
    // stopPropagation: otherwise the click bubbles to the canvas, which sees no 3D hit
    // and fires onPointerMissed, deselecting the player we just selected.
    <div className={`nametag${player.alive ? '' : ' dead'}${dim ? ' dim' : ''}`} style={{ borderColor: color }}
      data-tip={playerTip(view, player.id, god) + heatTip}
      onPointerEnter={() => { cameraHold.on = true }}
      onPointerLeave={() => { cameraHold.on = false }}
      onClick={(e) => { e.stopPropagation(); onSelect(player.id) }}>
      <div className="nametag-name">
        {role && (
          <span className={revealed ? '' : 'role-peek'} data-tip={roleTip(view, role)}>{roleEmoji(view, role)} </span>
        )}
        {player.name}
        {!player.alive && ' 👻'}
        {votes > 0 && <span className="chip vote" data-tip={`${votes} vote${votes > 1 ? 's' : ''} to eliminate ${player.name}`}>🗳️{votes}</span>}
        {suspectedBy.length > 1 && <span className="chip sus">🎯{suspectedBy.length}</span>}
      </div>
      {!compact && <div className="nametag-model" style={{ color }}>{player.model?.label ?? player.model_id}</div>}
      {showVote && (
        <div className="vote-tag" data-tip={`${player.name} voted to eliminate ${nameOf(view, vote.target)}`}>
          → {nameOf(view, vote.target)}
        </div>
      )}
      {claim && !compact && (
        <div className={`claim-badge${bluff ? ' bluff' : ''}`}
          data-tip={`${player.name} publicly claimed to be the ${roleLabel(view, claim)}`
            + (bluff ? `. It's a bluff: they are really the ${roleLabel(view, player.role)}.` : '.')}>
          claims {roleEmoji(view, claim)} {roleLabel(view, claim)}{bluff ? ' 🤥' : ''}
        </div>
      )}
    </div>
  )
}
