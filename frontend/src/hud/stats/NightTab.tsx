// God view: last night's ACTION events in resolution order.
import { classColor } from '../../lib/colors'
import { titleCase } from '../../lib/format'
import { PlayerName } from './PlayerName'
import type { StatsProps } from './StatsPanel'

export function NightTab({ view, onSelect }: StatsProps) {
  if (!view.nightLog.length) return <div className="muted">No night actions yet.</div>
  return (
    <ol className="night-log">
      {view.nightLog.map((ev) => {
        const targets: string[] = ev.data.targets ?? (ev.target ? [ev.target] : [])
        const result = ev.data.action === 'result'
        return (
          <li key={ev.seq} className={result ? 'result' : ''}>
            <span className="cls-dot" style={{ background: classColor(ev.data.cls) }} />
            {ev.actor && <PlayerName view={view} pid={ev.actor} onSelect={onSelect} />}{' '}
            <b>{result ? '📜 learns' : titleCase(String(ev.data.action ?? 'acts'))}</b>
            {!result && targets.map((t) => <PlayerName key={t} view={view} pid={t} onSelect={onSelect} />)}
            <div className="muted small">{ev.text}</div>
          </li>
        )
      })}
    </ol>
  )
}
