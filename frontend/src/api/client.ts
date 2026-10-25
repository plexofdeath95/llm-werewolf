// Thin REST client for the FastAPI backend (proxied at /api by Vite).
import type { GameConfig, GameRow, ModeInfo, ModelsResponse, SetupPlayer } from './types'

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`/api${path}`)
  if (!res.ok) throw new Error(`${res.status} ${res.statusText} on ${path}`)
  return res.json() as Promise<T>
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`/api${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(`${res.status}: ${await res.text()}`)
  return res.json() as Promise<T>
}

export interface GameDetail extends GameRow {
  players: Array<Omit<SetupPlayer, 'id' | 'model' | 'persona'> & { player_id: string; slug: string }>
}

export const api = {
  models: () => get<ModelsResponse>('/models'),
  roster: (n: number) => get<string[]>(`/roster?n=${n}`),
  modes: () => get<ModeInfo[]>('/modes'),
  deck: (mode: string, n: number) => get<string[]>(`/modes/${mode}/deck?n=${n}`),
  games: () => get<GameRow[]>('/games'),
  game: (id: string) => get<GameDetail>(`/games/${id}`),
  start: (cfg: GameConfig) => post<{ id: string }>('/games', cfg),
}

export function socketUrl(gameId: string): string {
  const proto = location.protocol === 'https:' ? 'wss' : 'ws'
  return `${proto}://${location.host}/api/games/${gameId}/ws`
}
