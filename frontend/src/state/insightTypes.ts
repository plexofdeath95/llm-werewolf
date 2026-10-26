// "At a glance" slices of GameView: suspicions, claims, emote pops, drama banners.

export interface Emote {
  emoji: string
  seq: number
  tip: string
  private: boolean
}

export interface Banner {
  text: string
  seq: number
  kind: 'death' | 'elimination' | 'winner'
}

export interface Cap { text: string; seq: number }

export interface InsightView {
  suspects: Record<string, string> // pid -> pid they privately suspect most (god view only)
  claims: Record<string, string> // pid -> role id they publicly claimed
  emotes: Record<string, Emote> // latest pop per player
  banner?: Banner
  caption: { public?: Cap; secret?: Cap } // "what's happening" (secret = god-view only)
}

export const emptyInsight: InsightView = { suspects: {}, claims: {}, emotes: {}, caption: {} }
