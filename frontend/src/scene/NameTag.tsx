// The tag under each avatar: name, model, role (god view / revealed) and claim badges.
import { cameraHold } from '../lib/cameraHold'
import { playerTip, roleTip } from '../lib/tips'
import { nameOf, roleEmoji, roleLabel, shownRole } from '../state/selectors'
import type { GameView, PlayerView } from '../state/viewTypes'

export interface NameTagProps {
  view: GameView
  player: PlayerView
  god: boolean
  suspectedBy: string[]
  compact: boolean // night: just name + role, so tags don't crowd the walk
  onSelect: (pid: string) => void
}

export function NameTag({ view, player, god, suspectedBy, compact, onSelect }: NameTagProps) {
  const role = shownRole(player, god)
  const color = player.model?.color ?? '#999'
  const claim = view.insight.claims[player.id]
  const bluff = god && claim && claim !== player.role
  const vote = view.phase === 'vote' ? view.votes[player.id] : undefined
  const showVote = vote && (god || !vote.private)
  const heatTip = god && suspectedBy.length
    ? `\nSuspected most by: ${suspectedBy.map((id) => view.players[id]?.name).join(', ')}` : ''
  return (
    // stopPropagation: otherwise the click bubbles to the canvas, which sees no 3D hit
    // and fires onPointerMissed, deselecting the player we just selected.
    <div className={`nametag${player.alive ? '' : ' dead'}`} style={{ borderColor: color }}
      data-tip={playerTip(view, player.id, god) + heatTip}
      onPointerEnter={() => { cameraHold.on = true }}
      onPointerLeave={() => { cameraHold.on = false }}
      onClick={(e) => { e.stopPropagation(); onSelect(player.id) }}>
      <div className="nametag-name">
        {role ? <span data-tip={roleTip(view, role)}>{roleEmoji(view, role)} </span> : null}
        {player.name}
        {!player.alive && ' 👻'}
      </div>
      {!compact && <div className="nametag-model" style={{ color }}>{player.model?.label ?? player.model_id}</div>}
      {showVote && (
        <div className="vote-tag" data-tip={`${player.name} voted to eliminate ${nameOf(view, vote.target)}`}>
          🗳️ → {nameOf(view, vote.target)}
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
