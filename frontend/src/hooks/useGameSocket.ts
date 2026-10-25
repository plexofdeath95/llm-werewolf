// WebSocket to one game: buffers stored + live events, live thought deltas, server state.
import { useCallback, useEffect, useRef, useState } from 'react'
import { socketUrl } from '../api/client'
import type { ControlAction, GameEvent, ServerMsg } from '../api/types'

export interface LiveThought { thought: string; draft: string | null; at: number }
export interface ServerState { live: boolean; paused: boolean; spent: number; max_usd: number }

export function useGameSocket(gameId: string) {
  const [events, setEvents] = useState<GameEvent[]>([])
  const [live, setLive] = useState<Record<string, LiveThought>>({})
  const [server, setServer] = useState<ServerState | null>(null)
  const [ended, setEnded] = useState(false)
  const [connected, setConnected] = useState(false)
  const ws = useRef<WebSocket | null>(null)
  const buf = useRef<{ events: GameEvent[]; live: Record<string, LiveThought | null> }>(
    { events: [], live: {} })
  const frame = useRef(0)

  useEffect(() => {
    setEvents([]); setLive({}); setEnded(false); setServer(null)
    const flush = () => {
      frame.current = 0
      const { events: evs, live: lv } = buf.current
      buf.current = { events: [], live: {} }
      if (evs.length) setEvents((prev) => [...prev, ...evs])
      if (Object.keys(lv).length) setLive((prev) => applyLive(prev, lv))
    }
    const schedule = () => { if (!frame.current) frame.current = requestAnimationFrame(flush) }
    const sock = new WebSocket(socketUrl(gameId))
    ws.current = sock
    sock.onopen = () => setConnected(true)
    sock.onclose = () => setConnected(false)
    sock.onmessage = (m) => {
      const msg = JSON.parse(m.data) as ServerMsg
      if (msg.type === 'event') {
        buf.current.events.push(msg.event)
        if (msg.event.kind === 'thought' && msg.event.actor) buf.current.live[msg.event.actor] = null
      } else if (msg.type === 'live') {
        buf.current.live[msg.actor] = { thought: msg.thought, draft: msg.draft, at: Date.now() }
      } else if (msg.type === 'state') {
        setServer({ live: msg.live, paused: msg.paused, spent: msg.spent, max_usd: msg.max_usd })
      } else if (msg.type === 'end') {
        setEnded(true)
      }
      schedule()
    }
    return () => {
      sock.close()
      if (frame.current) cancelAnimationFrame(frame.current)
      frame.current = 0
    }
  }, [gameId])

  const send = useCallback((action: ControlAction, amount?: number) => {
    if (ws.current?.readyState === WebSocket.OPEN) ws.current.send(JSON.stringify({ action, amount }))
  }, [])

  return { events, live, server, ended, connected, send }
}

function applyLive(prev: Record<string, LiveThought>, delta: Record<string, LiveThought | null>) {
  const next = { ...prev }
  for (const [pid, value] of Object.entries(delta)) {
    if (value) next[pid] = value
    else delete next[pid]
  }
  return next
}
