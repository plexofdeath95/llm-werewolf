// Seek scrubber with phase tick marks and jump-to-phase buttons (live + replay).
import { useMemo } from 'react'
import type { GameEvent } from '../api/types'
import type { EventQueue } from '../hooks/useEventQueue'
import { phaseMarks } from '../state/selectors'

export function ReplayBar({ events, queue }: { events: GameEvent[]; queue: EventQueue }) {
  const marks = useMemo(() => phaseMarks(events), [events])
  const total = Math.max(1, events.length)
  const prev = [...marks].reverse().find((m) => m.index < queue.cursor - 1)
  const next = marks.find((m) => m.index > queue.cursor)
  return (
    <div className="replay-bar">
      <button disabled={!prev} onClick={() => prev && queue.seek(prev.index)} title={prev?.label}>⏮</button>
      <div className="scrub">
        <input
          type="range" min={0} max={events.length} value={queue.cursor}
          onChange={(e) => queue.seek(Number(e.target.value))}
          aria-label="seek"
        />
        <div className="ticks">
          {marks.map((m) => (
            <button
              key={m.index}
              className={`tick${m.night ? ' night' : ''}`}
              style={{ left: `${(m.index / total) * 100}%` }}
              title={m.label}
              onClick={() => queue.seek(m.index)}
            />
          ))}
        </div>
      </div>
      <button disabled={!next} onClick={() => next && queue.seek(next.index)} title={next?.label}>⏭</button>
      <span className="scrub-count">{queue.cursor}/{events.length}</span>
    </div>
  )
}
