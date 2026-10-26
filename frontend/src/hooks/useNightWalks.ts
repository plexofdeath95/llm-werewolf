// God view: replay each night's moves as walks. When the first action of a night is revealed,
// the pacing queue holds while the whole batch plays out in resolution order (actors in the
// same order group walk together), then it jumps past the batch. Seeking cancels cleanly.
import { useEffect, useRef, useState } from 'react'
import type { GameEvent } from '../api/types'
import { isAct, walkCaption } from '../lib/nightText'
import { roleEmoji } from '../state/selectors'
import type { GameView } from '../state/viewTypes'
import type { EventQueue } from './useEventQueue'

export interface Walk {
  toSeat: number
  movement: string // visit | travel | none
  start: number // performance.now() ms
  out: number // seconds walking there, waiting, walking back
  pause: number
  back: number
  emoji: string
}

const OUT = 1.5, PAUSE = 1.2, BACK = 1.2

function groups(batch: GameEvent[]): GameEvent[][] {
  const by = new Map<number, GameEvent[]>()
  for (const ev of batch) by.set(ev.data.order ?? 0, [...(by.get(ev.data.order ?? 0) ?? []), ev])
  return [...by.entries()].sort((a, b) => a[0] - b[0]).map(([, g]) => g)
}

export function useNightWalks(events: GameEvent[], queue: EventQueue, view: GameView, god: boolean) {
  const [walks, setWalks] = useState<Record<string, Walk>>({})
  const [caption, setCaption] = useState<string>()
  const prev = useRef(queue.cursor)
  const run = useRef(0)
  const speed = useRef(queue.speed)
  speed.current = queue.speed

  const wait = (ms: number, token: number) => new Promise<void>((done) => {
    const t0 = performance.now()
    const tick = () => (run.current !== token || performance.now() - t0 >= ms ? done() : setTimeout(tick, 80))
    tick()
  })

  const play = async (batch: GameEvent[], token: number) => {
    for (const g of groups(batch)) {
      if (run.current !== token) return
      const sp = speed.current
      const walk = (ev: GameEvent): [string, Walk] => {
        const target = view.players[(ev.data.targets ?? [ev.target])[0] ?? '']
        const self = !target || target.id === ev.actor
        return [ev.actor!, { toSeat: target?.seat ?? 0, movement: self ? 'none' : String(ev.data.movement ?? 'visit'),
          start: performance.now(), out: OUT / sp, pause: PAUSE / sp, back: BACK / sp,
          emoji: roleEmoji(view, view.players[ev.actor!]?.role) }]
      }
      setWalks(Object.fromEntries(g.map(walk)))
      setCaption(g.map((ev) => walkCaption(view, ev)).join('   ·   '))
      await wait(((OUT + PAUSE + BACK) / sp) * 1000, token)
    }
  }

  useEffect(() => {
    const step = queue.cursor - prev.current
    prev.current = queue.cursor
    if (step !== 1) { // seek / jump: stop any walk in progress
      run.current++
      setWalks({})
      setCaption(undefined)
      return
    }
    const first = events[queue.cursor - 1]
    if (!god || !isAct(first) || queue.fastForward) return
    let end = queue.cursor - 1
    while (end < events.length && isAct(events[end]) && events[end].round === first.round) end++
    const token = ++run.current
    queue.hold(play(events.slice(queue.cursor - 1, end), token).then(() => {
      if (run.current !== token) return
      setWalks({})
      setCaption(undefined)
      queue.seek(end) // the rest of the batch has been shown as walks: reveal it at once
    }))
  }, [queue.cursor]) // eslint-disable-line react-hooks/exhaustive-deps

  return { walks, caption }
}
