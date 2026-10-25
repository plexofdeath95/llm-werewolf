// Running cost of the game vs. its budget cap.
import { usd } from '../lib/format'

export function CostMeter({ spent, max }: { spent: number; max?: number }) {
  const pct = max ? Math.min(100, (spent / max) * 100) : 0
  const hot = pct > 85
  return (
    <div className="cost-meter" title="LLM spend for this game">
      <span>💸 {usd(spent)}{max ? ` / ${usd(max)}` : ''}</span>
      {max ? (
        <div className="cost-bar">
          <div style={{ width: `${pct}%`, background: hot ? 'var(--danger)' : 'var(--gold)' }} />
        </div>
      ) : null}
    </div>
  )
}
