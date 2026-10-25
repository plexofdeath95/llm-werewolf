// DOM content of the bubble floating above a player's head.
import { THINKING_EMOJIS, urgencyEmoji } from '../lib/colors'
import { clip, tail } from '../lib/format'
import { useTick } from '../hooks/useTick'
import type { Bubble } from '../state/viewTypes'

export interface BubbleCardProps {
  bubble?: Bubble
  thinking: boolean
  liveText?: string
  showThoughts: boolean
}

function Thinking({ text, showText }: { text?: string; showText: boolean }) {
  const tick = useTick(true)
  const emoji = THINKING_EMOJIS[tick % THINKING_EMOJIS.length]
  return (
    <div className="bubble thought thinking">
      <span className="think-emoji">{emoji}</span>
      {showText && text ? <span className="live-text">{tail(text, 160)}</span> : null}
      <span className="dots"><i /><i /><i /></span>
    </div>
  )
}

export function BubbleCard({ bubble, thinking, liveText, showThoughts }: BubbleCardProps) {
  if (thinking) return <Thinking text={liveText} showText={showThoughts} />
  if (!bubble) return null
  if (bubble.kind === 'thought') {
    if (!showThoughts) return null
    return (
      <div className="bubble thought" key={bubble.seq}>
        {bubble.urgency !== undefined && (
          <span className="urgency-emoji" title={`urgency ${bubble.urgency}/10`}>
            {urgencyEmoji(bubble.urgency)}
          </span>
        )}
        <em>{clip(bubble.text || '…', 170)}</em>
      </div>
    )
  }
  if (bubble.kind === 'vote') {
    return <div className="bubble vote" key={bubble.seq}>🗳️ {bubble.text}</div>
  }
  return (
    <div className={`bubble speech${bubble.private ? ' private' : ''}`} key={bubble.seq}>
      {bubble.interrupt && <span className="interrupt-burst">INTERRUPTS!</span>}
      {bubble.channel && bubble.channel !== 'public' && (
        <span className="bubble-channel">{bubble.channel}</span>
      )}
      {clip(bubble.text, 260)}
    </div>
  )
}
