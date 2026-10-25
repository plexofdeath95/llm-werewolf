// Background music: one engine for the whole app (survives page changes).
// Random track per mood, ~2s crossfade between moods, auto-advance, gesture unlock.
import { fadeTo, loadPref, savePref, trackName } from './util'

type Listener = () => void
const CROSSFADE_MS = 2000

class MusicEngine {
  moods: Record<string, string[]> = {}
  enabled = false
  mood?: string
  track?: string
  volume = loadPref('music.volume', 0.45)
  muted = loadPref('music.muted', false)
  blocked = false
  private cur?: HTMLAudioElement
  private loading?: Promise<void>
  private listeners = new Set<Listener>()
  private version = 0

  load(): Promise<void> {
    this.loading ??= fetch('/api/music')
      .then((r) => r.json())
      .then((d) => { this.moods = d.moods ?? {}; this.enabled = !!d.enabled })
      .catch(() => { this.enabled = false })
      .finally(() => { if (this.mood) this.play(this.mood) ; this.emit() })
    return this.loading
  }

  setMood(mood: string) {
    if (mood === this.mood) return
    this.mood = mood
    void this.load().then(() => this.play(mood))
  }

  private tracksFor(mood: string): string[] {
    const list = this.moods[mood]
    if (list?.length) return list
    return mood.endsWith('_wins') ? this.moods.neutral_wins ?? [] : []
  }

  private play(mood: string) {
    if (!this.enabled || mood !== this.mood) return
    const list = this.tracksFor(mood)
    const old = this.cur
    if (!list.length) { this.cur = undefined; this.track = undefined; if (old) fadeTo(old, 0, CROSSFADE_MS, true); return this.emit() }
    const options = list.length > 1 ? list.filter((u) => u !== old?.src.replace(location.origin, '')) : list
    const url = options[Math.floor(Math.random() * options.length)]
    const audio = new Audio(url)
    audio.volume = 0
    audio.onended = () => this.play(this.mood ?? mood)
    this.cur = audio
    this.track = trackName(url)
    this.start(audio)
    if (old) fadeTo(old, 0, CROSSFADE_MS, true)
    this.emit()
  }

  private start(audio: HTMLAudioElement) {
    audio.play().then(() => {
      this.blocked = false
      fadeTo(audio, this.target(), CROSSFADE_MS)
      this.emit()
    }).catch(() => {
      this.blocked = true
      this.emit()
      const unlock = () => { if (this.cur === audio) this.start(audio) }
      document.addEventListener('pointerdown', unlock, { once: true })
    })
  }

  private target() { return this.muted ? 0 : this.volume }

  setVolume(v: number) {
    this.volume = v
    savePref('music.volume', v)
    if (this.cur) this.cur.volume = this.target()
    this.emit()
  }

  toggleMute() {
    this.muted = !this.muted
    savePref('music.muted', this.muted)
    if (this.cur) fadeTo(this.cur, this.target(), 300)
    this.emit()
  }

  subscribe = (l: Listener) => { this.listeners.add(l); return () => { this.listeners.delete(l) } }
  snapshot = () => this.version
  private emit() { this.version += 1; this.listeners.forEach((l) => l()) }
}

export const music = new MusicEngine()
