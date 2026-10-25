// Mute toggle, volume slider and now-playing name for the background music.
import { useMusic } from '../hooks/useMusic'

export function MusicControls() {
  const m = useMusic()
  if (!m.enabled) return null
  return (
    <div className="music-controls" title={m.track ? `Now playing: ${m.track}` : 'Music'}>
      <button className="icon-btn" onClick={() => m.toggleMute()}>
        {m.muted ? '🔇' : '🎵'}
      </button>
      <input
        type="range" min={0} max={1} step={0.01} value={m.volume}
        onChange={(e) => m.setVolume(Number(e.target.value))}
        aria-label="music volume"
      />
      <span className="now-playing">
        {m.blocked ? 'click anywhere to start music' : m.track ?? '—'}
      </span>
    </div>
  )
}
