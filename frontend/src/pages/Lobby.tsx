// Lobby: pick the mode, seats (models + personas), deck and settings, then start.
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import { useMusic } from '../hooks/useMusic'
import { DeckPicker } from './lobby/DeckPicker'
import { SeatList } from './lobby/SeatList'
import { SettingsCard } from './lobby/SettingsCard'
import { useLobbyForm } from './lobby/useLobbyForm'

export function Lobby() {
  useMusic('lobby')
  const form = useLobbyForm()
  const nav = useNavigate()
  const [starting, setStarting] = useState(false)
  const deckOk = form.deck.length === form.seats.length

  const start = async () => {
    setStarting(true)
    try {
      const { id } = await api.start(form.config())
      nav(`/game/${id}`)
    } catch (e) {
      form.setError((e as Error).message)
      setStarting(false)
    }
  }

  return (
    <div className="page lobby">
      <header className="hero">
        <h1>🐺 AI Plays Werewolf</h1>
        <p>Seat a table of LLMs, deal hidden roles, and watch them lie, deduce and vote — thoughts and all.</p>
      </header>
      {form.error && <div className="error-box">⚠️ {form.error}</div>}
      <section className="card">
        <div className="card-head">
          <h3>🎲 Game</h3>
          <select value={form.mode} onChange={(e) => { form.setMode(e.target.value); void form.resetDeck(e.target.value, form.seats.length) }}>
            {form.modes.map((m) => <option key={m.id} value={m.id}>{m.name}</option>)}
          </select>
        </div>
      </section>
      <div className="lobby-grid">
        <SeatList form={form} />
        <div>
          <DeckPicker form={form} />
          <SettingsCard form={form} />
        </div>
      </div>
      <div className="start-bar">
        <button className="start-btn" disabled={starting || !deckOk || !form.seats.length} onClick={start}>
          {starting ? '🕯️ Lighting the candles…' : form.settings.fake ? '🧪 Start demo game' : '🌕 Start game'}
        </button>
        {!deckOk && <span className="warn">Deck size must match the number of seats.</span>}
      </div>
    </div>
  )
}
