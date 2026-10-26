// Report how much of the screen the HUD covers (for camera framing, lib/framing.ts).
// Cinematic mode slides the side panels away; then only their edge tabs count.
import { useEffect } from 'react'
import { insets } from '../lib/framing'

const EDGE = 26 // px left visible of a hidden side panel (its tab)
const GAP = 12

function measure(hideLeft: boolean, hideRight: boolean) {
  const rect = (sel: string) => document.querySelector(sel)?.getBoundingClientRect()
  const w = window.innerWidth
  const h = window.innerHeight
  const left = rect('.hud-left')
  const right = rect('.hud-right')
  const top = rect('.caption-bar') ?? rect('.phase-banner') // not the transient recap card
  const bottom = rect('.hud-bottom')
  insets.left = hideLeft || !left?.width ? EDGE : left.right + GAP
  insets.right = hideRight || !right?.width ? EDGE : w - right.left + GAP
  insets.top = top ? top.bottom + GAP : 120
  insets.bottom = bottom ? h - bottom.top + GAP : 110
}

export function useHudInsets(hideLeft: boolean, hideRight: boolean) {
  useEffect(() => {
    const run = () => measure(hideLeft, hideRight)
    run()
    const ro = new ResizeObserver(run)
    for (const sel of ['.hud-left', '.hud-right', '.phase-banner', '.hud-bottom']) {
      const el = document.querySelector(sel)
      if (el) ro.observe(el)
    }
    window.addEventListener('resize', run)
    const t = setInterval(run, 1500) // panels change content (and height) all the time
    return () => {
      ro.disconnect()
      window.removeEventListener('resize', run)
      clearInterval(t)
    }
  }, [hideLeft, hideRight])
}
