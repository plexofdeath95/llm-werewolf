// Speech styles for the lobby dropdown and the phase-banner chip. The server's list
// (GET /api/models -> speech_styles) wins; this fallback keeps the default usable without it.
import type { SpeechStyle } from '../api/types'

export const DEFAULT_STYLE = 'caveman'
const FALLBACK: SpeechStyle[] = [{ id: 'caveman', label: 'cave-man speak', text: '' }]
const EMOJI: Record<string, string> = { caveman: '🦴' }

export function speechStyles(fromServer?: SpeechStyle[]): SpeechStyle[] {
  return fromServer?.length ? fromServer : FALLBACK
}

/** "🦴 cave-man speak" for a style id (undefined for normal speech). */
export function styleChip(id: string | null | undefined, list?: SpeechStyle[]): string | undefined {
  if (!id) return undefined
  const label = speechStyles(list).find((s) => s.id === id)?.label ?? id.replace(/_/g, ' ')
  return /^\p{L}/u.test(label) ? `${EMOJI[id] ?? '🗣️'} ${label}` : label // server labels carry an emoji
}
