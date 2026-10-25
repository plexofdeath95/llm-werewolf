// One seat: positions an Avatar around the table and attaches its Html overlays.
import { Html } from '@react-three/drei'
import type { LiveThought } from '../hooks/useGameSocket'
import { seatFacing, seatPosition } from '../lib/seats'
import { roleEmoji, roleLabel, shownRole, visibleBubble } from '../state/selectors'
import type { GameView, PlayerView } from '../state/viewTypes'
import { Avatar } from './Avatar'
import { BubbleCard } from './BubbleCard'

export interface SeatProps {
  view: GameView
  player: PlayerView
  god: boolean
  thinking: boolean
  live?: LiveThought
  selected: boolean
  onSelect: (pid: string) => void
}

export function Seat({ view, player, god, thinking, live, selected, onSelect }: SeatProps) {
  const count = view.order.length
  const pos = seatPosition(player.seat, count)
  const reaction = view.roundOpen ? view.reactions[player.id] : undefined
  const role = shownRole(player, god)
  const color = player.model?.color ?? '#999'
  const liveText = live ? live.draft || live.thought : undefined
  return (
    <group position={pos} rotation={[0, seatFacing(player.seat, count), 0]}>
      <Avatar
        id={player.id}
        color={color}
        alive={player.alive}
        speaking={view.speaker === player.id}
        thinking={thinking}
        selected={selected}
        urgency={god ? reaction?.urgency : undefined}
        onSelect={() => onSelect(player.id)}
      >
        <Html position={[0, 2.35, 0]} center zIndexRange={[20, 0]}>
          <div className="bubble-anchor">
            <BubbleCard
              bubble={visibleBubble(view.bubbles[player.id], god)}
              thinking={thinking && player.alive}
              liveText={liveText}
              showThoughts={god}
            />
          </div>
        </Html>
        <Html position={[0, -0.05, 0.55]} center zIndexRange={[10, 0]}>
          {/* stopPropagation: otherwise the click bubbles to the canvas, which sees no 3D hit
              and fires onPointerMissed, deselecting the player we just selected. */}
          <div className={`nametag${player.alive ? '' : ' dead'}`} style={{ borderColor: color }}
            onClick={(e) => { e.stopPropagation(); onSelect(player.id) }}>
            <div className="nametag-name">
              {role ? <span title={roleLabel(view, role)}>{roleEmoji(view, role)} </span> : null}
              {player.name}
              {!player.alive && ' 👻'}
            </div>
            <div className="nametag-model" style={{ color }}>{player.model?.label ?? player.model_id}</div>
          </div>
        </Html>
      </Avatar>
    </group>
  )
}
