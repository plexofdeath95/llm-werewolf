// "What's happening": one big sentence under the phase banner, readable at a glance.
// A night walk in progress (god view) overrides it with what is being done right now.
import type { GameView } from '../state/viewTypes'

export function Caption({ view, god, walk }: { view: GameView; god: boolean; walk?: string }) {
  const { public: pub, secret } = view.insight.caption
  const cap = walk ? { text: walk, seq: -1 }
    : god && secret && (!pub || secret.seq >= pub.seq) ? secret : pub
  if (!cap) return null
  return (
    <div className={`caption-bar${walk ? ' walk' : ''}`} key={`${cap.seq}-${cap.text}`}
      data-tip="What's happening right now">
      {cap.text}
    </div>
  )
}
