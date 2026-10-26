// One seat: an Avatar (walking at night in god view) with rings, bubble, emote and name tag.
import { Html } from '@react-three/drei'
import type { Walk } from '../hooks/useNightWalks'
import { heat } from '../state/insightReducer'
import { isNight, visibleBubble, voteTally } from '../state/selectors'
import type { GameView, PlayerView } from '../state/viewTypes'
import { Avatar } from './Avatar'
import { BubbleCard } from './BubbleCard'
import { Emote } from './Emote'
import { NameTag } from './NameTag'
import { Rings } from './Rings'
import { Walker } from './Walker'

export interface SeatProps {
  view: GameView
  player: PlayerView
  god: boolean
  thinking: boolean
  selected: boolean
  charsPerSecond: number
  walk?: Walk // god view night walk in progress
  walking: boolean // some night walk is playing (dim whoever isn't part of it)
  onSelect: (pid: string) => void
}

export function Seat({ view, player, god, thinking, selected, charsPerSecond, walk, walking, onSelect }: SeatProps) {
  const count = view.order.length
  const reaction = view.roundOpen ? view.reactions[player.id] : undefined
  const color = player.model?.color ?? '#999'
  const speaking = view.speaker === player.id
  // Only the current speaker's line gets a bubble (votes show as badges instead);
  // anyone else whose model call is in flight gets a "thinking" indicator.
  const b = visibleBubble(view.bubbles[player.id], god)
  const shown = b?.kind === 'speech' && speaking && !walk ? b : undefined
  const night = isNight(view.phase) || view.phase === 'dawn'
  const voting = view.phase === 'vote'
  const suspectedBy = god && !night && !voting ? heat(view, player.id) : []
  const dim = walking && (!walk || walk.movement === 'none')
  const votes = view.phase === 'vote' ? voteTally(view, god)[player.id] ?? 0 : 0
  // acting from home (Seer, Veteran...): a glow-pop instead of a walk
  const still = walk?.movement === 'none'
    ? { emoji: walk.emoji, seq: walk.start, tip: 'Acting from home tonight', private: true } : undefined
  return (
    <Walker seat={player.seat} count={count} walk={walk}>
      <Avatar id={player.id} color={color} alive={player.alive} speaking={speaking}
        thinking={thinking} onSelect={() => onSelect(player.id)} dim={dim}
        wolfEyes={god && night && player.team === 'wolves'}>
        <Rings color={color} alive={player.alive} speaking={speaking} selected={selected}
          urgency={god ? reaction?.urgency : undefined} />
        <Html position={[0, 2.35, 0]} center zIndexRange={[20, 0]}>
          <div className="bubble-anchor">
            <BubbleCard bubble={shown} thinking={thinking && player.alive && !shown}
              charsPerSecond={charsPerSecond} />
          </div>
        </Html>
        <Html position={[0.55, 1.95, 0]} center zIndexRange={[18, 0]}>
          <Emote emote={still ?? view.insight.emotes[player.id]} god={god} />
        </Html>
        <Html position={[0, -0.05, 0.55]} center zIndexRange={[10, 0]}>
          <NameTag view={view} player={player} god={god} suspectedBy={suspectedBy} compact={night}
            votes={votes} dim={dim} onSelect={onSelect} />
        </Html>
      </Avatar>
    </Walker>
  )
}
