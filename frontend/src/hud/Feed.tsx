// Scrolling chat log; sticks to the bottom unless the viewer scrolled up.
import { useEffect, useRef } from 'react'
import { visibleFeed } from '../state/selectors'
import type { GameView } from '../state/viewTypes'
import { FeedItem } from './FeedItem'

const MAX_ROWS = 300

export function Feed({ view, god }: { view: GameView; god: boolean }) {
  const box = useRef<HTMLDivElement>(null)
  const stick = useRef(true)
  const items = visibleFeed(view, god)
  const shown = items.slice(-MAX_ROWS)

  useEffect(() => {
    const el = box.current
    if (el && stick.current) el.scrollTop = el.scrollHeight
  }, [shown.length, view.lastSeq])

  const onScroll = () => {
    const el = box.current
    if (el) stick.current = el.scrollHeight - el.scrollTop - el.clientHeight < 60
  }

  return (
    <div className="panel feed" ref={box} onScroll={onScroll}>
      {items.length > MAX_ROWS && <div className="feed-more">… {items.length - MAX_ROWS} earlier</div>}
      {shown.map((ev) => <FeedItem key={ev.seq} ev={ev} view={view} />)}
      {!items.length && <div className="feed-empty">The tavern is quiet… for now.</div>}
    </div>
  )
}
