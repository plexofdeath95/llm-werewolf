// One seat: model dropdown (with color swatch), persona preset and free-text persona.
import type { ModelEntry, Persona, SeatConfig } from '../../api/types'

export interface SeatRowProps {
  index: number
  seat: SeatConfig
  models: ModelEntry[]
  personas: Persona[]
  onChange: (seat: SeatConfig) => void
  onRemove?: () => void
}

export function SeatRow({ index, seat, models, personas, onChange, onRemove }: SeatRowProps) {
  const model = models.find((m) => m.id === seat.model_id)
  const preset = personas.find((p) => p.text === seat.persona)?.id ?? (seat.persona ? 'custom' : '')
  return (
    <div className="seat-row">
      <span className="seat-no">{index + 1}</span>
      <span className="swatch" style={{ background: model?.color ?? '#555' }} />
      <select value={seat.model_id} onChange={(e) => onChange({ ...seat, model_id: e.target.value })}>
        {models.map((m) => (
          <option key={m.id} value={m.id}>
            {m.label}{m.tier === 'economy' ? ' (economy)' : ''}
          </option>
        ))}
      </select>
      <select
        value={preset}
        onChange={(e) => {
          const p = personas.find((x) => x.id === e.target.value)
          onChange({ ...seat, persona: p ? p.text : e.target.value === 'custom' ? seat.persona ?? ' ' : null })
        }}
        title="persona (optional)"
      >
        <option value="">🙂 default self</option>
        {personas.map((p) => <option key={p.id} value={p.id}>🎭 {p.label}</option>)}
        <option value="custom">✏️ custom…</option>
      </select>
      {preset === 'custom' && (
        <input className="persona-input" placeholder="Describe a persona…" value={seat.persona ?? ''}
          onChange={(e) => onChange({ ...seat, persona: e.target.value || null })} />
      )}
      {onRemove && <button className="icon-btn" onClick={onRemove} title="remove seat">✕</button>}
    </div>
  )
}
