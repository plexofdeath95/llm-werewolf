// DOM content of the bubble above a player's head: "thinking…", or what they said / voted.
// Reasoning never pops up in the scene; click a player to read it in the Mind panel.
import { THINKING_EMOJIS } from '../lib/colors'
import { clip } from '../lib/format'
import { INTERRUPT_TIP } from '../lib/tips'
import { useTick } from '../hooks/useTick'
import type { Bubble } from '../state/viewTypes'

export interface BubbleCardProps {
  bubble?: Bubble
  thinking: boolean
}

function Thinking() {
  const tick = useTick(true)
  return (
    <div className="bubble thought thinking" data-tip="Thinking… (click them to read their reasoning)">
      <span className="think-emoji">{THINKING_EMOJIS[tick % THINKING_EMOJIS.length]}</span>
      <span className="dots"><i /><i /><i /></span>
    </div>
  )
}

export function BubbleCard({ bubble, thinking }: BubbleCardProps) {
  if (bubble?.kind === 'vote') {
    return <div className="bubble vote" key={bubble.seq}>🗳️ {bubble.text}</div>
  }
  if (bubble?.kind === 'speech') {
    return (
      <div className={`bubble speech${bubble.private ? ' private' : ''}`} key={bubble.seq}>
        {bubble.interrupt && <span className="interrupt-burst" data-tip={INTERRUPT_TIP}>INTERRUPTS!</span>}
        {bubble.channel && bubble.channel !== 'public' && (
          <span className="bubble-channel">{bubble.channel}</span>
        )}
        {clip(bubble.text, 180)}
      </div>
    )
  }
  return thinking ? <Thinking /> : null
}
