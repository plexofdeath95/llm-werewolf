// Live urgency bars + thought snippets for the current react round.
import { urgencyColor, urgencyEmoji } from '../lib/colors'
import { urgencyTip } from '../lib/tips'
import type { GameView } from '../state/viewTypes'

export interface ReactionStripProps {
  view: GameView
  thinking: Set<string>
  onSelect: (pid: string) => void
}

export function ReactionStrip({ view, thinking, onSelect }: ReactionStripProps) {
  const ids = view.order.filter((id) => view.reactions[id] || thinking.has(id))
  if (!ids.length) return null
  return (
    <div className="reaction-strip">
      {ids.map((id) => {
        const p = view.players[id]
        const r = view.reactions[id]
        const won = r && view.speaker === id && !view.roundOpen
        return (
          <button key={id} className={`reaction-chip${won ? ' won' : ''}`} onClick={() => onSelect(id)}
            data-tip={r ? urgencyTip(r.urgency, r.thought) + (won ? '\n\nWon the floor.' : '') : 'Thinking…'}
            style={{ borderColor: p?.model?.color }}>
            <div className="chip-head">
              <span className="chip-emoji">{r ? urgencyEmoji(r.urgency) : '🤔'}</span>
              <b>{p?.name}</b>
              {r && <span className="chip-urg">{r.urgency}</span>}
            </div>
            <div className="urg-bar">
              <div style={{ width: `${(r?.urgency ?? 0) * 10}%`, background: urgencyColor(r?.urgency ?? 0) }} />
            </div>
            <div className="chip-thought">{r ? urgencyTip(r.urgency).split(':')[1] : 'thinking…'}</div>
          </button>
        )
      })}
    </div>
  )
}
