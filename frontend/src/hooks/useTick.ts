// A shared ticker so many components can animate (emoji cycling, dots) off one interval.
import { useEffect, useState } from 'react'

const listeners = new Set<(n: number) => void>()
let count = 0
let timer: ReturnType<typeof setInterval> | undefined

function ensureTimer() {
  if (timer) return
  timer = setInterval(() => {
    count += 1
    listeners.forEach((l) => l(count))
  }, 450)
}

export function useTick(active = true): number {
  const [n, setN] = useState(count)
  useEffect(() => {
    if (!active) return
    listeners.add(setN)
    ensureTimer()
    return () => {
      listeners.delete(setN)
      if (!listeners.size && timer) {
        clearInterval(timer)
        timer = undefined
      }
    }
  }, [active])
  return n
}
