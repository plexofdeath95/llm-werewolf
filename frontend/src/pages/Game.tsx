// Game view (live or replay): socket -> pacing queue -> reducer -> 3D scene + HUD.
import { useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useEventQueue } from '../hooks/useEventQueue'
import { useGameSocket } from '../hooks/useGameSocket'
import { useGameView, usePendingThinkers } from '../hooks/useGameView'
import { moodFor, useMusic } from '../hooks/useMusic'
import type { ViewToggles } from '../hud/Controls'
import { GameHud } from '../hud/GameHud'
import { loadPref, savePref } from '../music/util'
import { GameScene } from '../scene/GameScene'

const DEFAULT_TOGGLES: ViewToggles = { god: true, follow: true, orbit: false, stats: true }
const NO_LIVE = {}
const LIVE_EDGE = 6 // events; closer than this to the newest event = "watching live"

export function GamePage() {
  const { id = '' } = useParams()
  const sock = useGameSocket(id)
  const liveGame = !!sock.server?.live && !sock.ended
  const queue = useEventQueue(sock.events, liveGame)
  const view = useGameView(sock.events, queue.cursor)
  const pending = usePendingThinkers(sock.events, queue.cursor)
  const nearEdge = sock.events.length - queue.cursor < LIVE_EDGE
  const live = liveGame && nearEdge ? sock.live : NO_LIVE
  useMusic(moodFor(view))

  const thinking = useMemo(() => {
    const s = new Set(pending)
    Object.keys(live).forEach((pid) => s.add(pid))
    for (const pid of s) if (!view.players[pid]?.alive) s.delete(pid)
    return s
  }, [pending, live, view.players])

  const [toggles, setToggles] = useState<ViewToggles>(() => loadPref('view.toggles', DEFAULT_TOGGLES))
  const setToggle = (k: keyof ViewToggles) => setToggles((t) => {
    const next = { ...t, [k]: !t[k] }
    savePref('view.toggles', next)
    return next
  })
  const [selected, setSelected] = useState<string>('')

  return (
    <div className="game-page">
      <GameScene view={view} god={toggles.god} thinking={thinking} live={live}
        follow={toggles.follow} orbit={toggles.orbit}
        selected={selected || undefined} onSelect={setSelected} />
      <GameHud view={view} events={sock.events} queue={queue} server={sock.server}
        liveGame={liveGame} send={sock.send} toggles={toggles} setToggle={setToggle}
        thinking={thinking} selected={selected || undefined} onSelect={setSelected} />
      <Link to="/" className="back-btn" title="back to lobby">⟵ Lobby</Link>
      {!sock.connected && !sock.ended && <div className="conn-flag">connecting to game {id}…</div>}
    </div>
  )
}
