// Live vote tally as VOTEs arrive, plus the final VOTE_RESULT.
import { PlayerName } from './PlayerName'
import type { StatsProps } from './StatsPanel'

export function VotesTab({ view, god, onSelect }: StatsProps) {
  const votes = Object.entries(view.votes).filter(([, v]) => god || !v.private)
  const tally: Record<string, string[]> = {}
  for (const [voter, v] of votes) {
    const key = v.target ?? 'nobody'
    ;(tally[key] ??= []).push(voter)
  }
  const rows = Object.entries(tally).sort((a, b) => b[1].length - a[1].length)
  const max = Math.max(1, ...rows.map(([, v]) => v.length))
  const result = view.voteResult
  return (
    <div>
      <div className="stat-label">Current tally ({votes.length} votes)</div>
      {rows.map(([target, voters]) => (
        <div key={target} className="tally-row">
          <span className="tally-name">
            {target === 'nobody' ? <span className="muted">nobody</span> : <PlayerName view={view} pid={target} onSelect={onSelect} />}
          </span>
          <div className="tally-bar"><div style={{ width: `${(voters.length / max) * 100}%` }} /></div>
          <span className="tally-n">{voters.length}</span>
          <span className="tally-voters muted">{voters.map((id) => view.players[id]?.name).join(', ')}</span>
        </div>
      ))}
      {!rows.length && <div className="muted">No votes cast yet this phase.</div>}
      {result && (
        <div className="vote-result">
          📊 Result:{' '}
          {Object.entries(result.counts)
            .map(([pid, n]) => `${view.players[pid]?.name ?? pid} ${n}`)
            .join(' · ') || 'no votes'}
          <div>
            {result.eliminated
              ? <>⚖️ Eliminated: <PlayerName view={view} pid={result.eliminated} onSelect={onSelect} /></>
              : '⚖️ Nobody eliminated (tie)'}
          </div>
        </div>
      )}
    </div>
  )
}
