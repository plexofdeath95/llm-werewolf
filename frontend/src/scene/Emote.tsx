// A short emoji pop beside a player's head (named, interrupt, vote, death, saved...).
// Keyed by event seq, so each new emote replays the CSS pop-and-fade animation.
import type { Emote as EmoteData } from '../state/viewTypes'

export function Emote({ emote, god }: { emote?: EmoteData; god: boolean }) {
  if (!emote || (emote.private && !god)) return null
  return (
    <div className="emote-pop" key={emote.seq} data-tip={emote.tip}>
      {emote.emoji}
    </div>
  )
}
