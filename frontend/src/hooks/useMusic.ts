// useMusic(mood): set the background mood and subscribe to the music engine state.
import { useEffect, useSyncExternalStore } from 'react'
import { music } from '../music/engine'
import type { GameView } from '../state/viewTypes'

export function useMusic(mood?: string) {
  useEffect(() => {
    if (mood) music.setMood(mood)
    else void music.load()
  }, [mood])
  useSyncExternalStore(music.subscribe, music.snapshot)
  return music
}

/** Mood for a game view: phase-driven, winner theme at the end. */
export function moodFor(view: GameView): string {
  if (view.winner) return `${view.winner}_wins`
  switch (view.phase) {
    case 'setup': return 'lobby'
    case 'night': return 'night'
    case 'dawn': return 'dawn'
    case 'vote': return 'vote'
    default: return 'day'
  }
}
