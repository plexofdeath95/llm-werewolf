// Small display formatters.

export function usd(n: number | undefined): string {
  const v = n ?? 0
  return v < 0.01 && v > 0 ? `$${v.toFixed(4)}` : `$${v.toFixed(2)}`
}

export function seconds(n: number | undefined): string {
  return n === undefined ? '' : `${n.toFixed(1)}s`
}

export function when(ts: number | undefined | null): string {
  if (!ts) return '—'
  return new Date(ts * 1000).toLocaleString(undefined, {
    month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
  })
}

export function tail(text: string, max = 220): string {
  const t = text.trim()
  return t.length <= max ? t : '…' + t.slice(t.length - max)
}

export function clip(text: string, max = 140): string {
  const t = text.trim()
  return t.length <= max ? t : t.slice(0, max - 1) + '…'
}

export function titleCase(s: string): string {
  return s.replace(/[_-]/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}
