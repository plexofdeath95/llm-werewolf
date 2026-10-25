// One global tooltip: any element with data-tip (or a native title, converted on first hover)
// gets an instant, styled tooltip that follows the cursor and is never clipped by panels.
import { useEffect, useState } from 'react'

interface Tip { text: string; x: number; y: number }

function tipTarget(el: EventTarget | null): HTMLElement | null {
  let node = el instanceof Element ? (el as HTMLElement) : null
  while (node && node !== document.body) {
    const title = node.getAttribute('title')
    if (title) { // adopt native titles so there is never a second, slow browser tooltip
      node.dataset.tip = title
      node.removeAttribute('title')
    }
    if (node.dataset?.tip) return node
    node = node.parentElement
  }
  return null
}

export function TooltipLayer() {
  const [tip, setTip] = useState<Tip | null>(null)
  useEffect(() => {
    const move = (e: MouseEvent) => {
      const t = tipTarget(e.target)
      setTip(t ? { text: t.dataset.tip ?? '', x: e.clientX, y: e.clientY } : null)
    }
    const hide = () => setTip(null)
    document.addEventListener('mousemove', move, { passive: true })
    document.addEventListener('mouseleave', hide)
    window.addEventListener('blur', hide)
    return () => {
      document.removeEventListener('mousemove', move)
      document.removeEventListener('mouseleave', hide)
      window.removeEventListener('blur', hide)
    }
  }, [])
  if (!tip?.text) return null
  const left = Math.max(8, Math.min(tip.x + 14, window.innerWidth - 320))
  const below = tip.y + 90 < window.innerHeight
  return (
    <div className="tooltip" role="tooltip"
      style={{ left, top: below ? tip.y + 18 : tip.y - 12, transform: below ? undefined : 'translateY(-100%)' }}>
      {tip.text}
    </div>
  )
}
