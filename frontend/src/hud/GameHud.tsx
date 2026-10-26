// Overlay layout on top of the 3D scene: banner, controls, feed, stats, mind, strip, scrubber.
import { useEffect, useState } from 'react'
import type { ControlAction, GameEvent } from '../api/types'
import { useHudInsets } from '../hooks/useHudInsets'
import type { EventQueue } from '../hooks/useEventQueue'
import type { ServerState } from '../hooks/useGameSocket'
import type { GameView } from '../state/viewTypes'
import { Controls, type ViewToggles } from './Controls'
import { Caption } from './Caption'
import { CostMeter } from './CostMeter'
import { DramaBanner } from './DramaBanner'
import { Feed } from './Feed'
import { GameOverCard } from './GameOverCard'
import { MindPanel } from './MindPanel'
import { MusicControls } from './MusicControls'
import { NightRecap } from './NightRecap'
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
  walkCaption?: string // night walk in progress (god view)
  cinematic: boolean // side panels slide away so the room is visible
  speechStyle?: string // chip under the phase title, e.g. '🦴 cave-man speak'
}

export function GameHud(p: GameHudProps) {
  const { view, toggles } = p
  const [pin, setPin] = useState({ left: false, right: false })
  useEffect(() => { if (!p.cinematic) setPin({ left: false, right: false }) }, [p.cinematic])
  useHudInsets(p.cinematic && !pin.left, p.cinematic && !pin.right)
  const cls = `hud${p.cinematic ? ' cinematic' : ''}${pin.left ? ' pin-left' : ''}${pin.right ? ' pin-right' : ''}`
  return (
    <div className={cls}>
      {p.cinematic && (
        <>
          <button className="edge-tab left" title="show the stats panel"
            onClick={() => setPin((s) => ({ ...s, left: !s.left }))}>📊</button>
          <button className="edge-tab right" title="show the chat feed"
            onClick={() => setPin((s) => ({ ...s, right: !s.right }))}>💬</button>
        </>
      )}
      <div className="hud-top">
        <PhaseBanner view={view} style={p.speechStyle} />
        <Caption view={view} god={toggles.god} walk={p.walkCaption} />
      </div>
      <NightRecap view={view} god={toggles.god} />
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
      <DramaBanner view={view} />
      <div className="hud-right">
        <Feed view={view} god={toggles.god} />
      </div>
      <div className="hud-bottom">
        {toggles.god && toggles.strip && (
          <ReactionStrip view={view} thinking={p.thinking} onSelect={p.onSelect} />
        )}
        <ReplayBar events={p.events} queue={p.queue} />
        <Controls queue={p.queue} server={p.server} liveGame={p.liveGame} send={p.send}
          toggles={toggles} setToggle={p.setToggle} />
      </div>
      <GameOverCard view={view} />
    </div>
  )
}
