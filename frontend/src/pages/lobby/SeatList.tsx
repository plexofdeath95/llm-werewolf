// Player count + auto-fill (unique models first) + one SeatRow per seat.
import type { LobbyForm } from './useLobbyForm'
import { SeatRow } from './SeatRow'

export function SeatList({ form }: { form: LobbyForm }) {
  const { catalog, seats, setSeats, modeInfo } = form
  if (!catalog) return null
  const min = modeInfo?.min_players ?? 5
  const max = modeInfo?.max_players ?? 16
  const unique = new Set(seats.map((s) => s.model_id)).size
  return (
    <section className="card">
      <div className="card-head">
        <h3>🪑 Players</h3>
        <label className="inline">
          count
          <input type="number" min={min} max={max} value={seats.length}
            onChange={(e) => form.setCount(Math.max(min, Math.min(max, Number(e.target.value))))} />
        </label>
        <button onClick={() => form.autofill(seats.length)} title="as many unique models as possible, then repeat">
          ✨ auto-fill unique
        </button>
        <span className="muted">{unique} unique model{unique === 1 ? '' : 's'}</span>
      </div>
      {seats.map((seat, i) => (
        <SeatRow key={i} index={i} seat={seat} models={catalog.models.filter((m) => m.enabled)} personas={catalog.personas}
          onChange={(s) => setSeats(seats.map((x, j) => (j === i ? s : x)))}
          onRemove={seats.length > min ? () => form.setCount(seats.length - 1) : undefined} />
      ))}
    </section>
  )
}
