// Shared palette lookups: action classes, teams, urgency emoji.

const CLASS_COLORS: Record<string, string> = {
  killing: '#ff4d4d',
  protection: '#3ddc84',
  information: '#4da3ff',
  'role-block': '#b06cff',
  manipulation: '#ff9a3d',
}

export function classColor(cls: string | undefined): string {
  const key = (cls ?? '').toLowerCase().split(/[ /]/)[0]
  return CLASS_COLORS[key] ?? '#9aa0a6'
}

export const TEAM_COLORS: Record<string, string> = {
  village: '#7fd37f',
  wolves: '#ff5c5c',
  neutral: '#c9a7ff',
}

export function teamColor(team: string | undefined): string {
  return TEAM_COLORS[team ?? ''] ?? '#cccccc'
}

export function urgencyEmoji(u: number): string {
  if (u <= 2) return '😶'
  if (u <= 5) return '🤨'
  if (u <= 7) return '🙋'
  return '😤'
}

export function urgencyColor(u: number): string {
  const t = Math.max(0, Math.min(10, u)) / 10
  const hue = 130 - t * 130 // green -> red
  return `hsl(${hue}, 85%, 55%)`
}

export const THINKING_EMOJIS = ['🤔', '💭', '✍️', '🧐', '🤫']

export function channelTint(channel: string | undefined): string | undefined {
  if (!channel || channel === 'public') return undefined
  if (channel.includes('wolf')) return 'var(--tint-wolf)'
  if (channel.includes('lover')) return 'var(--tint-love)'
  if (channel.includes('last')) return 'var(--tint-last)'
  return 'var(--tint-private)'
}
