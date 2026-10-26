// DOM content of the bubble above a player's head: "thinking…", or what they said.
// Full text, typed out as it is said. Reasoning never pops up in the scene; click a
// player to read it in the Mind panel.
import { useTypewriter } from '../hooks/useTypewriter'
import { THINKING_EMOJIS } from '../lib/colors'
import { INTERRUPT_TIP } from '../lib/tips'
import { useTick } from '../hooks/useTick'
import type { Bubble } from '../state/viewTypes'

export interface BubbleCardProps {
  bubble?: Bubble
  thinking: boolean
  charsPerSecond: number
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

function Speech({ bubble, cps }: { bubble: Bubble; cps: number }) {
  const typed = useTypewriter(bubble.text, bubble.seq, cps)
  return (
    <div className={`bubble speech${bubble.private ? ' private' : ''}`} data-tip={bubble.text}>
      {bubble.interrupt && <span className="interrupt-burst" data-tip={INTERRUPT_TIP}>INTERRUPTS!</span>}
      {bubble.channel && bubble.channel !== 'public' && (
        <span className="bubble-channel">{bubble.channel}</span>
      )}
      {/* the full text reserves the bubble's final size, so it doesn't jump while typing */}
      <span className="typed-wrap">
        <span className="typed-ghost" aria-hidden>{bubble.text}</span>
        <span className="typed">{typed}</span>
      </span>
    </div>
  )
}

export function BubbleCard({ bubble, thinking, charsPerSecond }: BubbleCardProps) {
  if (bubble?.kind === 'speech') return <Speech key={bubble.seq} bubble={bubble} cps={charsPerSecond} />
  return thinking ? <Thinking /> : null
}
