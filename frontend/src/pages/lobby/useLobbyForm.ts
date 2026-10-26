// Lobby form state: seats, deck and settings, with server-provided defaults.
import { useCallback, useEffect, useState } from 'react'
import { api } from '../../api/client'
import type { GameConfig, ModeInfo, ModelsResponse, SeatConfig } from '../../api/types'

export interface LobbySettings {
  seed: string
  narrator: string
  quick: number
  deep: number
  maxCost: number
  rounds: number
  fake: boolean
  revealModels: boolean
  revealOnDeath: boolean
}

const DEFAULTS: LobbySettings = {
  seed: '', narrator: '', quick: 0, deep: 2048, maxCost: 10, rounds: 3,
  fake: false, revealModels: false, revealOnDeath: true,
}

export function useLobbyForm() {
  const [catalog, setCatalog] = useState<ModelsResponse>()
  const [modes, setModes] = useState<ModeInfo[]>([])
  const [mode, setMode] = useState('werewolf')
  const [seats, setSeats] = useState<SeatConfig[]>([])
  const [deck, setDeck] = useState<string[]>([])
  const [settings, setSettings] = useState<LobbySettings>(DEFAULTS)
  const [error, setError] = useState<string>()

  const autofill = useCallback(async (n: number) => {
    const ids = await api.roster(n)
    setSeats((old) => ids.map((model_id, i) => ({ model_id, persona: old[i]?.persona ?? null })))
  }, [])

  const resetDeck = useCallback(async (m: string, n: number) => {
    setDeck(await api.deck(m, n))
  }, [])

  useEffect(() => {
    Promise.all([api.models(), api.modes()])
      .then(async ([cat, ms]) => {
        setCatalog(cat)
        setModes(ms)
        const m = ms[0]?.id ?? 'werewolf'
        setMode(m)
        await autofill(cat.default_players)
        await resetDeck(m, cat.default_players)
      })
      .catch((e: Error) => setError(`Backend unreachable: ${e.message}`))
  }, [autofill, resetDeck])

  const setCount = (n: number) => {
    setSeats((old) => Array.from({ length: n }, (_, i) => old[i] ?? old[i % Math.max(1, old.length)] ?? { model_id: catalog?.models[0]?.id ?? '' }))
    void resetDeck(mode, n)
  }

  const config = (): GameConfig => ({
    mode, seats, deck,
    seed: settings.seed ? Number(settings.seed) : null,
    max_cost_usd: settings.maxCost,
    quick_reasoning: settings.quick,
    deep_reasoning: settings.deep,
    narrator_model: settings.narrator || null,
    reveal_on_death: settings.revealOnDeath,
    reveal_models: settings.revealModels,
    fake: settings.fake,
    fake_delay: 0.8,
    talk: { rounds: settings.rounds },
  })

  const modeInfo = modes.find((m) => m.id === mode)
  return {
    catalog, modes, modeInfo, mode, setMode, seats, setSeats, deck, setDeck, settings,
    setSettings, error, setError, autofill, resetDeck, setCount, config,
  }
}

export type LobbyForm = ReturnType<typeof useLobbyForm>
