// One line in the chat feed, styled by event kind and channel.
import type { GameEvent } from '../api/types'
import { channelTint } from '../lib/colors'
import { channelTip, INTERRUPT_TIP, NUDGE_TIP } from '../lib/tips'
import { nameOf } from '../state/selectors'
import type { GameView } from '../state/viewTypes'

const ICONS: Record<string, string> = {
  moderator: '🎙️', narration: '📜', vote: '🗳️', vote_result: '📊', action: '🌙',
  death: '💀', reveal: '🎭', status: '⏸️', error: '⚠️', game_over: '🏆',
}

export function FeedItem({ ev, view }: { ev: GameEvent; view: GameView }) {
  const channel: string | undefined = ev.data.channel
  const tint = channelTint(channel)
  const style = tint ? { background: tint } : undefined
  const tag = channel && channel !== 'public' ? <span className="chan" data-tip={channelTip(channel)}>{channel}</span> : null
  if (ev.kind === 'phase') {
    const night = ev.data.phase === 'night'
    return <div className={`feed-phase${night ? ' night' : ''}`}>{night ? '🌙' : '☀️'} {ev.text}</div>
  }
  if (ev.kind === 'speech') {
    const p = ev.actor ? view.players[ev.actor] : undefined
    const last = channel === 'last words'
    return (
      <div className={`feed-speech${last ? ' last-words' : ''}`} style={style}>
        {tag}
        {ev.data.interrupt && <span className="int-badge" data-tip={INTERRUPT_TIP}>⚡ interrupts</span>}
        {ev.data.nudged && <span className="int-badge nudge" data-tip={NUDGE_TIP}>👉 called on</span>}
        <b style={{ color: p?.model?.color }}>{p?.name ?? '?'}</b>
        <span className="feed-text">{ev.text}</span>
      </div>
    )
  }
  if (ev.kind === 'vote') {
    return (
      <div className="feed-line" style={style}>
        {tag}{ICONS.vote} <b>{nameOf(view, ev.actor)}</b> {ev.data.verb ?? 'votes for'}{' '}
        <b>{nameOf(view, ev.target)}</b>
        {ev.text && <span className="feed-reason"> — {ev.text}</span>}
      </div>
    )
  }
  const cls = ev.kind === 'moderator' ? 'feed-mod'
    : ev.kind === 'narration' ? 'feed-narr'
      : ev.kind === 'game_over' ? 'feed-over' : 'feed-line'
  const who = ev.kind === 'error' && ev.actor ? `${nameOf(view, ev.actor)}: ` : ''
  return (
    <div className={`${cls} kind-${ev.kind}`} style={style}>
      {tag}{ICONS[ev.kind] ?? '•'} {who}{ev.text}
    </div>
  )
}
