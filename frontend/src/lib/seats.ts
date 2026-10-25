// Seat geometry around the round table (y-up, table centered at origin).

export const TABLE_RADIUS = 2.2
export const SEAT_RADIUS = 3.15

export type Vec3 = [number, number, number]

export function seatAngle(seat: number, count: number): number {
  // Seat 0 faces the camera side (+z), then clockwise.
  return Math.PI / 2 + (seat / Math.max(1, count)) * Math.PI * 2
}

export function seatPosition(seat: number, count: number, radius = SEAT_RADIUS): Vec3 {
  const a = seatAngle(seat, count)
  return [Math.cos(a) * radius, 0, Math.sin(a) * radius]
}

/** Y rotation so an avatar at this seat faces the table center. */
export function seatFacing(seat: number, count: number): number {
  const [x, , z] = seatPosition(seat, count)
  return Math.atan2(-x, -z)
}

export function midpoint(a: Vec3, b: Vec3, lift = 2): Vec3 {
  return [(a[0] + b[0]) / 2, Math.max(a[1], b[1]) + lift, (a[2] + b[2]) / 2]
}

/** Deterministic small hash so each seat gets stable cosmetic variety. */
export function hashSeed(s: string): number {
  let h = 2166136261
  for (let i = 0; i < s.length; i++) h = Math.imul(h ^ s.charCodeAt(i), 16777619)
  return Math.abs(h)
}
