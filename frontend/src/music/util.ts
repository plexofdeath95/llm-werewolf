// Music helpers: volume fades, persisted prefs (localStorage, never required), track names.

export function fadeTo(audio: HTMLAudioElement, to: number, ms: number, stopAfter = false) {
  const from = audio.volume
  const start = performance.now()
  const step = (now: number) => {
    const k = Math.min(1, (now - start) / ms)
    audio.volume = Math.max(0, Math.min(1, from + (to - from) * k))
    if (k < 1) requestAnimationFrame(step)
    else if (stopAfter) { audio.pause(); audio.src = '' }
  }
  requestAnimationFrame(step)
}

export function loadPref<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key)
    return raw === null ? fallback : (JSON.parse(raw) as T)
  } catch {
    return fallback
  }
}

export function savePref(key: string, value: unknown) {
  try {
    localStorage.setItem(key, JSON.stringify(value))
  } catch {
    /* storage unavailable: preference just won't persist */
  }
}

export function trackName(url: string): string {
  const file = decodeURIComponent(url.split('/').pop() ?? url)
  return file.replace(/\.[a-z0-9]+$/i, '').replace(/_/g, ' ')
}
