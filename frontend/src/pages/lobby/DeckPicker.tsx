// Role deck: the roles in play (one per seat), grouped by team; click to add/remove.
import type { RoleInfo, Team } from '../../api/types'
import { teamColor } from '../../lib/colors'
import type { LobbyForm } from './useLobbyForm'

const TEAMS: Team[] = ['village', 'wolves', 'neutral']

function RoleChip({ id, role, count, onClick, title }: {
  id: string; role: RoleInfo; count?: number; onClick: () => void; title?: string
}) {
  return (
    <button className="role-chip" style={{ borderColor: teamColor(role.team) }} onClick={onClick}
      title={title ?? role.summary ?? id}>
      {role.emoji} {role.label}{count && count > 1 ? ` ×${count}` : ''}
    </button>
  )
}

export function DeckPicker({ form }: { form: LobbyForm }) {
  const roles = form.modeInfo?.roles ?? {}
  const { deck, setDeck, seats } = form
  const counts = deck.reduce<Record<string, number>>((m, r) => ({ ...m, [r]: (m[r] ?? 0) + 1 }), {})
  const remove = (id: string) => {
    const i = deck.indexOf(id)
    setDeck(deck.filter((_, j) => j !== i))
  }
  const diff = deck.length - seats.length
  return (
    <section className="card">
      <div className="card-head">
        <h3>🃏 Role deck</h3>
        <span className={diff ? 'warn' : 'muted'}>
          {deck.length} roles for {seats.length} seats{diff ? ` (${diff > 0 ? 'remove' : 'add'} ${Math.abs(diff)})` : ' ✓'}
        </span>
        <button onClick={() => form.resetDeck(form.mode, seats.length)}>↺ balanced default</button>
      </div>
      <div className="deck-in-play">
        {Object.entries(counts).map(([id, n]) => roles[id] && (
          <RoleChip key={id} id={id} role={roles[id]} count={n} onClick={() => remove(id)} title="click to remove one" />
        ))}
      </div>
      {TEAMS.map((team) => {
        const list = Object.entries(roles).filter(([, r]) => r.team === team)
        if (!list.length) return null
        return (
          <details key={team} className="deck-team">
            <summary style={{ color: teamColor(team) }}>{team} ({list.length})</summary>
            <div className="deck-options">
              {list.map(([id, r]) => (
                <RoleChip key={id} id={id} role={r} onClick={() => setDeck([...deck, id])}
                  title={`${r.summary ?? ''}${r.classes?.length ? ` [${r.classes.join(', ')}]` : ''} (click to add)`} />
              ))}
            </div>
          </details>
        )
      })}
    </section>
  )
}
