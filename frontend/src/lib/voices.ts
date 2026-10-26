// Browser text-to-speech (Web Speech API, free and local): a distinct, stable voice per seat
// plus a deeper narrator. If the API or voices are missing, speak() resolves immediately.
import { hashSeed } from './seats'

const synth = typeof window !== 'undefined' && 'speechSynthesis' in window
  ? window.speechSynthesis : undefined
let pool: SpeechSynthesisVoice[] = []

function voices(): SpeechSynthesisVoice[] {
  if (!synth) return []
  if (!pool.length) { // Edge's "Online (Natural)" voices first, then any other English voice
    const en = synth.getVoices().filter((v) => v.lang.toLowerCase().startsWith('en'))
    const natural = (v: SpeechSynthesisVoice) => /natural|neural|online/i.test(v.name)
    pool = [...en.filter(natural), ...en.filter((v) => !natural(v))]
  }
  return pool
}
synth?.addEventListener?.('voiceschanged', () => { pool = [] })

const DEEP = /guy|christopher|eric|roger|ryan|davis|andrew|brian|william|thomas|george|david/i

export interface VoiceSpec { voice?: SpeechSynthesisVoice; pitch: number; rate: number }

/** By seat, so a table gets as many different voices as the browser has. */
export function seatVoice(seat: number, id: string): VoiceSpec {
  const list = voices()
  const h = hashSeed(id)
  return { voice: list[(seat * 3) % Math.max(1, list.length)], pitch: 0.85 + (h % 7) * 0.05,
    rate: 1.0 + (h % 5) * 0.04 }
}

export function narratorVoice(): VoiceSpec {
  const list = voices()
  return { voice: list.find((v) => DEEP.test(v.name)) ?? list[0], pitch: 0.75, rate: 0.95 }
}

/** Speak, resolving when done, on error, or after a safety timeout. Never rejects. */
export function speak(text: string, spec: VoiceSpec, speed = 1): Promise<void> {
  if (!synth || !text.trim()) return Promise.resolve()
  return new Promise((resolve) => {
    const u = new SpeechSynthesisUtterance(text)
    if (spec.voice) u.voice = spec.voice
    u.pitch = spec.pitch
    u.rate = Math.min(2, spec.rate * speed)
    let done = false
    const finish = () => {
      if (done) return
      done = true
      clearTimeout(guard)
      resolve()
    }
    // onend is unreliable in some browsers: never hold the game longer than ~1.6x the estimate
    const guard = setTimeout(finish, (text.length / (14 * u.rate)) * 1600 + 2500)
    u.onend = finish
    u.onerror = finish
    synth.speak(u)
  })
}

export function stopSpeaking(): void {
  synth?.cancel()
}

/** Typewriter speed that roughly matches the voice (or a comfortable reading pace). */
export function charsPerSecond(voiced: boolean, speed: number): number {
  return (voiced ? 14 : 40) * speed
}
