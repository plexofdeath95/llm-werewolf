// Types for the stats slices of GameView (see statsReducer).
export interface PlayerStats {
  messages: number
  interrupts: number
  urgencySum: number
  urgencyN: number
  cost: number
  latencySum: number
  calls: number
}

export interface TimelineMark { label: string; phase: string; round: number; seq: number }
export interface VoteView { target: string | null; private: boolean; verb?: string }
