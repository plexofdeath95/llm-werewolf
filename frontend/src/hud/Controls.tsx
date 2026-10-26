// Playback + server controls and view toggles.
import type { ControlAction } from '../api/types'
import type { EventQueue } from '../hooks/useEventQueue'
import type { ServerState } from '../hooks/useGameSocket'

export interface ViewToggles {
  god: boolean
  follow: boolean
  orbit: boolean
  stats: boolean
  voices: boolean
  strip: boolean
  cinematic: boolean
}

export interface ControlsProps {
  queue: EventQueue
  server: ServerState | null
  liveGame: boolean
  send: (a: ControlAction, amount?: number) => void
  toggles: ViewToggles
  setToggle: (k: keyof ViewToggles) => void
}

const SPEEDS = [0.5, 1, 2, 4, 8]

function Toggle({ on, label, onClick, title }: { on: boolean; label: string; onClick: () => void; title: string }) {
  return <button className={`chip-btn${on ? ' on' : ''}`} onClick={onClick} title={title}>{label}</button>
}

export function Controls({ queue, server, liveGame, send, toggles, setToggle }: ControlsProps) {
  const paused = server?.paused
  return (
    <div className="controls">
      {liveGame && (
        <div className="ctl-group" title="Controls the running game on the server">
          <span className="ctl-label">game</span>
          {paused
            ? <button onClick={() => send('resume')} title="resume the game">▶️</button>
            : <button onClick={() => send('pause')} title="pause before the next LLM round">⏸️</button>}
          <button onClick={() => send('step')} title="run one more LLM round">⏭️</button>
          <button onClick={() => send('raise_budget', 5)} title="raise the budget by $5 and resume">💰+5</button>
        </div>
      )}
      <div className="ctl-group">
        <span className="ctl-label">view</span>
        <button onClick={queue.toggle} title="pause/play the playback">{queue.playing ? '⏸' : '▶'}</button>
        <select value={queue.speed} onChange={(e) => queue.setSpeed(Number(e.target.value))} title="playback speed">
          {SPEEDS.map((s) => <option key={s} value={s}>{s}×</option>)}
        </select>
        {liveGame && !queue.atEdge && <button onClick={queue.toEdge} title="jump to live">⏩ live</button>}
      </div>
      <div className="ctl-group">
        <Toggle on={toggles.god} label="👁 god" onClick={() => setToggle('god')} title="show roles, private chats and thoughts" />
        <Toggle on={toggles.follow} label="🎥 follow" onClick={() => setToggle('follow')} title="camera follows the speaker" />
        <Toggle on={toggles.orbit} label="🌀 orbit" onClick={() => setToggle('orbit')} title="free camera" />
        <Toggle on={toggles.stats} label="📊 stats" onClick={() => setToggle('stats')} title="game stats panel" />
        <Toggle on={toggles.voices} label="🔊 voices" onClick={() => setToggle('voices')} title="read every line aloud, one voice per player" />
        <Toggle on={toggles.cinematic} label="🎬 cinematic" onClick={() => setToggle('cinematic')} title="hide the side panels during the night walk, dawn and the vote (hover an edge tab to peek)" />
        <Toggle on={toggles.strip} label="🎚 bids" onClick={() => setToggle('strip')} title="show the live urgency bids of every player" />
      </div>
    </div>
  )
}
