// Game view (live or replay): socket -> pacing queue -> reducer -> 3D scene + HUD.
import { useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api/client'
import { useEventQueue } from '../hooks/useEventQueue'
import { useFetch } from '../hooks/useFetch'
import { useGameSocket } from '../hooks/useGameSocket'
import { useGameView, usePendingThinkers } from '../hooks/useGameView'
import { useNightWalks } from '../hooks/useNightWalks'
import { moodFor, useMusic } from '../hooks/useMusic'
import { useSpeechSync } from '../hooks/useSpeechSync'
import { styleChip } from '../lib/speechStyles'
import { charsPerSecond } from '../lib/voices'
import type { ViewToggles } from '../hud/Controls'
import { GameHud } from '../hud/GameHud'
import { loadPref, savePref } from '../music/util'
import { GameScene } from '../scene/GameScene'

const DEFAULT_TOGGLES: ViewToggles = {
  god: true, follow: true, orbit: false, stats: true, voices: true, strip: false, cinematic: true,
}
const TOGGLES_KEY = 'view.toggles.v6'
const CINEMATIC_PHASES = new Set(['night', 'dawn', 'vote']) // bumped whenever the defaults change meaning
const NO_LIVE = {}
const LIVE_EDGE = 6 // events; closer than this to the newest event = "watching live"

export function GamePage() {
  const { id = '' } = useParams()
  const sock = useGameSocket(id)
  const liveGame = !!sock.server?.live && !sock.ended
  const [toggles, setToggles] = useState<ViewToggles>(() => loadPref(TOGGLES_KEY, DEFAULT_TOGGLES))
  const queue = useEventQueue(sock.events, liveGame, toggles.voices)
  const view = useGameView(sock.events, queue.cursor)
  useSpeechSync(sock.events, queue, view, toggles.voices, toggles.god)
  const night = useNightWalks(sock.events, queue, view, toggles.god)
  const detail = useFetch(() => Promise.all([api.game(id), api.models()]), [id])
  const style = styleChip(detail.data?.[0].config.speech_style, detail.data?.[1].speech_styles)
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

  const setToggle = (k: keyof ViewToggles) => setToggles((t) => {
    const next = { ...t, [k]: !t[k] }
    savePref(TOGGLES_KEY, next)
    return next
  })
  const [selected, setSelected] = useState<string>('')

  return (
    <div className="game-page">
      <GameScene view={view} god={toggles.god} thinking={thinking}
        follow={toggles.follow} orbit={toggles.orbit}
        charsPerSecond={charsPerSecond(toggles.voices, queue.speed)} walks={night.walks}
        selected={selected || undefined} onSelect={setSelected} />
      <GameHud view={view} events={sock.events} queue={queue} server={sock.server}
        liveGame={liveGame} send={sock.send} toggles={toggles} setToggle={setToggle}
        thinking={thinking} selected={selected || undefined} onSelect={setSelected}
        walkCaption={night.caption} speechStyle={style}
        cinematic={toggles.cinematic && (CINEMATIC_PHASES.has(view.phase) || !!night.caption)} />
      <Link to="/" className="back-btn" title="back to lobby">⟵ Lobby</Link>
      {!sock.connected && !sock.ended && <div className="conn-flag">connecting to game {id}…</div>}
    </div>
  )
}
