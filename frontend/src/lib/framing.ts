// Camera framing: the HUD reports how many pixels it covers on each side (useHudInsets), and
// frame() finds how far back the camera must sit for a ring of the given radius
// (seats by day, houses by night) to land entirely in the uncovered part of the screen.
import { HOUSE_R } from '../scene/House'

export const insets = { left: 0, right: 0, top: 0, bottom: 0 } // px covered by the HUD

export const DAY_RING = 4.6 // seats + name tags
export const NIGHT_RING = HOUSE_R + 0.6 // cottages behind the seats
const HEIGHTS = [0, 1.6] // floor and heads
const SAMPLES = 24

export interface Framing { distance: number; lookZ: number }

/** Closest framing that fits the ring. Perspective makes the near side loom larger, so the
 *  look-at point may slide toward the camera (lookZ) to centre the ring in the free area. */
export function frame(ring: number, dir: [number, number, number], fovDeg: number,
  w: number, h: number): Framing {
  let best: Framing = { distance: Infinity, lookZ: 0 }
  for (const lookZ of [0, 0.5, 1, 1.5, 2, 2.5]) {
    const distance = fitDistance(ring, dir, fovDeg, w, h, lookZ)
    if (distance < best.distance) best = { distance, lookZ }
  }
  return best
}

function fitDistance(ring: number, dir: [number, number, number], fovDeg: number,
  w: number, h: number, lookZ: number): number {
  const t = Math.tan((fovDeg * Math.PI) / 360)
  const aspect = w / h
  const lim = { l: -(1 - (2 * insets.left) / w), r: 1 - (2 * insets.right) / w,
    b: -(1 - (2 * insets.bottom) / h), t: 1 - (2 * insets.top) / h }
  // camera basis: forward f (toward the table), right = +x, up = right x f
  const [dx, dy, dz] = dir
  const f = [-dx, -dy, -dz]
  const up = [0, dz, -dy] // cross((1,0,0), f) for a camera in the y-z plane
  const fits = (d: number) => {
    for (let i = 0; i < SAMPLES; i++) {
      const a = (i / SAMPLES) * Math.PI * 2
      for (const y of HEIGHTS) {
        const rel = [Math.cos(a) * ring - dx * d, y - dy * d, Math.sin(a) * ring - lookZ - dz * d]
        const z = rel[0] * f[0] + rel[1] * f[1] + rel[2] * f[2]
        const nx = rel[0] / (z * t * aspect)
        const ny = (rel[1] * up[1] + rel[2] * up[2]) / (z * t)
        if (z <= 0 || nx < lim.l || nx > lim.r || ny < lim.b || ny > lim.t) return false
      }
    }
    return true
  }
  let lo = 4
  let hi = 60
  for (let k = 0; k < 22; k++) {
    const mid = (lo + hi) / 2
    if (fits(mid)) hi = mid
    else lo = mid
  }
  return hi
}
