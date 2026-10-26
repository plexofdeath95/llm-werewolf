// Speak each newly revealed line (plus phase changes and deaths, in the narrator's voice) and
// hold the pacing queue until the voice finishes, so audio and text stay in sync.
// Seeking, fast-forwarding, very high speeds or muting cancel speech; nothing ever blocks.
import { useEffect, useRef } from 'react'
import type { GameEvent } from '../api/types'
import { narratorVoice, seatVoice, speak, stopSpeaking, type VoiceSpec } from '../lib/voices'
import type { GameView } from '../state/viewTypes'
import type { EventQueue } from './useEventQueue'

const NARRATED = new Set(['phase', 'death', 'game_over'])

function utterance(ev: GameEvent, view: GameView, god: boolean): { text: string; spec: VoiceSpec } | null {
  if (ev.kind === 'speech' && ev.actor && (god || ev.visible_to === null)) {
    const p = view.players[ev.actor]
    return p ? { text: ev.text, spec: seatVoice(p.seat, p.id) } : null
  }
  if (NARRATED.has(ev.kind) && ev.visible_to === null) return { text: ev.text, spec: narratorVoice() }
  return null
}

export function useSpeechSync(events: GameEvent[], queue: EventQueue, view: GameView,
  on: boolean, god: boolean) {
  const prev = useRef(queue.cursor)
  useEffect(() => {
    const step = queue.cursor - prev.current
    prev.current = queue.cursor
    if (!on || step !== 1 || queue.speed > 2 || queue.fastForward) {
      if (!on || step !== 1) stopSpeaking()
      return
    }
    const ev = events[queue.cursor - 1]
    const line = ev && utterance(ev, view, god)
    if (line) queue.hold(speak(line.text, line.spec, queue.speed))
  }, [queue.cursor, on]) // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => () => stopSpeaking(), [])
}
