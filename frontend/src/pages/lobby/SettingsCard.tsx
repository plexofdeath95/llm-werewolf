// Game settings: seed, narrator, reasoning caps, cost cap, demo mode, reveal toggles.
import type { LobbyForm, LobbySettings } from './useLobbyForm'

export function SettingsCard({ form }: { form: LobbyForm }) {
  const { settings: s, setSettings, catalog } = form
  const set = <K extends keyof LobbySettings>(k: K, v: LobbySettings[K]) => setSettings({ ...s, [k]: v })
  const num = (k: 'quick' | 'deep' | 'maxCost', label: string, step: number) => (
    <label>
      {label}
      <input type="number" step={step} min={0} value={s[k]} onChange={(e) => set(k, Number(e.target.value))} />
    </label>
  )
  return (
    <section className="card settings">
      <h3>⚙️ Settings</h3>
      <div className="settings-grid">
        <label>
          seed
          <input placeholder="random" value={s.seed} onChange={(e) => set('seed', e.target.value.replace(/\D/g, ''))} />
        </label>
        <label>
          narrator
          <select value={s.narrator} onChange={(e) => set('narrator', e.target.value)}>
            <option value="">— none —</option>
            {catalog?.models.map((m) => <option key={m.id} value={m.id}>{m.label}</option>)}
          </select>
        </label>
        {num('quick', 'react reasoning cap', 128)}
        {num('deep', 'decision reasoning cap', 256)}
        {num('maxCost', 'max cost (USD)', 1)}
      </div>
      <div className="settings-toggles">
        <label className="toggle">
          <input type="checkbox" checked={s.fake} onChange={(e) => set('fake', e.target.checked)} />
          🧪 Demo mode (no API, fake players)
        </label>
        <label className="toggle">
          <input type="checkbox" checked={s.revealOnDeath} onChange={(e) => set('revealOnDeath', e.target.checked)} />
          🎭 Reveal roles on death
        </label>
        <label className="toggle">
          <input type="checkbox" checked={s.revealModels} onChange={(e) => set('revealModels', e.target.checked)} />
          🤖 Players know which model each other is
        </label>
      </div>
    </section>
  )
}
