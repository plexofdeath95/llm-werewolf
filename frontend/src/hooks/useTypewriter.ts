// Reveal text a few characters at a time (restarts whenever `key` changes).
import { useEffect, useState } from 'react'

export function useTypewriter(text: string, key: number, charsPerSecond: number): string {
  const [shown, setShown] = useState(0)
  useEffect(() => {
    setShown(0)
    if (!text) return
    const step = Math.max(1, Math.round(charsPerSecond / 30))
    const t = setInterval(() => {
      setShown((n) => {
        if (n + step >= text.length) clearInterval(t)
        return Math.min(text.length, n + step)
      })
    }, 1000 / 30)
    return () => clearInterval(t)
  }, [text, key, charsPerSecond])
  return text.slice(0, shown)
}
