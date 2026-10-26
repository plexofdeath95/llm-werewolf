// God view: last night's actions in resolution order, as plain sentences, plus what each
// player privately learned at dawn.
import { actSentence, nightActs } from '../../lib/nightText'
import { PlayerName } from './PlayerName'
import type { StatsProps } from './StatsPanel'

export function NightTab({ view, onSelect }: StatsProps) {
  const acts = nightActs(view)
  const notes = view.nightLog.filter((e) => e.data.action === 'result')
  if (!acts.length && !notes.length) return <div className="muted">No night actions yet.</div>
  return (
    <div>
      <ol className="night-log">
        {acts.map((ev) => <li key={ev.seq} data-tip={ev.text || undefined}>{actSentence(view, ev)}</li>)}
      </ol>
      {notes.length > 0 && <div className="stat-label">Private results at dawn</div>}
      <ul className="night-log">
        {notes.map((ev) => (
          <li key={ev.seq} className="result">
            {ev.actor && <PlayerName view={view} pid={ev.actor} onSelect={onSelect} />} {ev.text}
          </li>
        ))}
      </ul>
    </div>
  )
}
