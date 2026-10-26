// Game settings: seed, narrator, reasoning caps, cost cap, demo mode, reveal toggles.
import type { LobbyForm, LobbySettings } from './useLobbyForm'

export function SettingsCard({ form }: { form: LobbyForm }) {
  const { settings: s, setSettings, catalog } = form
  const set = <K extends keyof LobbySettings>(k: K, v: LobbySettings[K]) => setSettings({ ...s, [k]: v })
  const num = (k: 'quick' | 'deep' | 'maxCost' | 'rounds', label: string, step: number, tip: string) => (
    <label title={tip}>
      {label}
      <input type="number" step={step} min={k === 'rounds' ? 1 : 0} value={s[k]}
        onChange={(e) => set(k, Number(e.target.value))} />
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
            {catalog?.models.filter((m) => m.enabled).map((m) => <option key={m.id} value={m.id}>{m.label}</option>)}
          </select>
        </label>
        {num('rounds', 'discussion rounds', 1, 'Time limit: each day ends after this many rounds '
          + '(one round = one message per living player). Everyone is heard at least once.')}
        {num('quick', 'reaction reasoning (0 = off, fastest)', 128, 'Hidden reasoning tokens for quick '
          + 'reaction calls. 0 = off: reactions stay fast and the in-character thought still shows; '
          + 'votes and night actions keep their own reasoning cap.')}
        {num('deep', 'decision reasoning cap', 256, 'Max reasoning tokens for votes and night actions')}
        {num('maxCost', 'max cost (USD)', 1, 'The game pauses when it has spent this much')}
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
