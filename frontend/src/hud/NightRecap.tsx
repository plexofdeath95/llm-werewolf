// God view, at dawn: what really happened last night, one icon sentence per action, in the
// order the night resolved. Fades after a few seconds (or close it); the case board keeps it.
import { useState } from 'react'
import { actSentence, nightActs } from '../lib/nightText'
import type { GameView } from '../state/viewTypes'

export function NightRecap({ view, god }: { view: GameView; god: boolean }) {
  const dawn = [...view.timeline].reverse().find((m) => m.phase === 'dawn')
  const [closed, setClosed] = useState<number>()
  const acts = nightActs(view)
  const fresh = view.phase === 'dawn' || view.phase === 'discussion'
  if (!god || !dawn || !fresh || closed === dawn.seq || !acts.length) return null
  return (
    <div className="panel night-recap" key={dawn.seq}>
      <div className="recap-head">
        <b>🌙 Last night</b>
        <button className="icon-btn" onClick={() => setClosed(dawn.seq)} title="close">✕</button>
      </div>
      <ol>{acts.map((ev) => <li key={ev.seq}>{actSentence(view, ev)}</li>)}</ol>
    </div>
  )
}
