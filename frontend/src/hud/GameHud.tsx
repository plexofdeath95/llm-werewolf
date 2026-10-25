// Overlay layout on top of the 3D scene: banner, controls, feed, stats, mind, strip, scrubber.
import type { ControlAction, GameEvent } from '../api/types'
import type { EventQueue } from '../hooks/useEventQueue'
import type { ServerState } from '../hooks/useGameSocket'
import type { GameView } from '../state/viewTypes'
import { Controls, type ViewToggles } from './Controls'
import { CostMeter } from './CostMeter'
import { Feed } from './Feed'
import { GameOverCard } from './GameOverCard'
import { MindPanel } from './MindPanel'
import { MusicControls } from './MusicControls'
import { PhaseBanner } from './PhaseBanner'
import { ReactionStrip } from './ReactionStrip'
import { ReplayBar } from './ReplayBar'
import { StatsPanel } from './stats/StatsPanel'

export interface GameHudProps {
  view: GameView
  events: GameEvent[]
  queue: EventQueue
  server: ServerState | null
  liveGame: boolean
  send: (a: ControlAction, amount?: number) => void
  toggles: ViewToggles
  setToggle: (k: keyof ViewToggles) => void
  thinking: Set<string>
  selected?: string
  onSelect: (pid: string) => void
}

export function GameHud(p: GameHudProps) {
  const { view, toggles } = p
  return (
    <div className="hud">
      <div className="hud-top">
        <PhaseBanner view={view} />
      </div>
      <div className="hud-top-right">
        <CostMeter spent={Math.max(view.spent, p.server?.spent ?? 0)} max={p.server?.max_usd} />
        <MusicControls />
      </div>
      {view.paused && p.liveGame && <div className="paused-flag">⏸ Game paused on the server</div>}
      <div className="hud-left">
        {toggles.stats && (
          <StatsPanel view={view} god={toggles.god} thinking={p.thinking} onSelect={p.onSelect} />
        )}
        {p.selected && (
          <MindPanel view={view} pid={p.selected} god={toggles.god} onClose={() => p.onSelect('')} />
        )}
      </div>
      <div className="hud-right">
        <Feed view={view} god={toggles.god} />
      </div>
      <div className="hud-bottom">
        {toggles.god && <ReactionStrip view={view} thinking={p.thinking} onSelect={p.onSelect} />}
        <ReplayBar events={p.events} queue={p.queue} />
        <Controls queue={p.queue} server={p.server} liveGame={p.liveGame} send={p.send}
          toggles={toggles} setToggle={p.setToggle} />
      </div>
      <GameOverCard view={view} />
    </div>
  )
}
