// Collapsible game-stats panel so humans can keep track: tabs derived from the reducer state.
import { useState } from 'react'
import type { GameView } from '../../state/viewTypes'
import { NightTab } from './NightTab'
import { OverviewTab } from './OverviewTab'
import { PlayersTab } from './PlayersTab'
import { TalkTab } from './TalkTab'
import { VotesTab } from './VotesTab'

export interface StatsProps {
  view: GameView
  god: boolean
  thinking: Set<string>
  onSelect: (pid: string) => void
}

const TABS = ['Overview', 'Talk', 'Votes', 'Players', 'Night'] as const
type Tab = (typeof TABS)[number]

export function StatsPanel(props: StatsProps) {
  const [open, setOpen] = useState(true)
  const [tab, setTab] = useState<Tab>('Overview')
  const tabs = TABS.filter((t) => t !== 'Night' || props.god)
  const active = tabs.includes(tab) ? tab : 'Overview'
  return (
    <div className={`panel stats${open ? '' : ' collapsed'}`}>
      <div className="stats-head">
        <button className="icon-btn" onClick={() => setOpen(!open)} title="toggle stats">
          {open ? '▾' : '▸'} 📊
        </button>
        {open && tabs.map((t) => (
          <button key={t} className={`tab${t === active ? ' on' : ''}`} onClick={() => setTab(t)}>{t}</button>
        ))}
        {!open && <span className="stats-mini">Round {props.view.round} · {props.view.phaseLabel}</span>}
      </div>
      {open && (
        <div className="stats-body">
          {active === 'Overview' && <OverviewTab {...props} />}
          {active === 'Talk' && <TalkTab {...props} />}
          {active === 'Votes' && <VotesTab {...props} />}
          {active === 'Players' && <PlayersTab {...props} />}
          {active === 'Night' && <NightTab {...props} />}
        </div>
      )}
    </div>
  )
}
