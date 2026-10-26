// Moves a seated player through a night walk: out around the table to the target's door
// (visit) or a watching spot beside it (travel), a pause, then back to their seat.
import { useFrame } from '@react-three/fiber'
import { useRef, type ReactNode } from 'react'
import * as THREE from 'three'
import type { Walk } from '../hooks/useNightWalks'
import { SEAT_RADIUS, seatAngle, seatFacing, seatPosition } from '../lib/seats'

const DOOR_R = 4.05 // just in front of the cottage (scene/House.tsx)
const WATCH_OFFSET = 0.24 // radians beside the door: "a few steps away"
const ease = (k: number) => (k < 0.5 ? 2 * k * k : 1 - (-2 * k + 2) ** 2 / 2)

export function Walker({ seat, count, walk, children }: {
  seat: number; count: number; walk?: Walk; children: ReactNode
}) {
  const g = useRef<THREE.Group>(null)
  const home = seatPosition(seat, count)
  useFrame(() => {
    const grp = g.current
    if (!grp) return
    if (!walk || walk.movement === 'none') {
      grp.position.set(...home)
      grp.rotation.y = seatFacing(seat, count)
      return
    }
    const t = (performance.now() - walk.start) / 1000
    const k = t < walk.out ? ease(t / walk.out)
      : t < walk.out + walk.pause ? 1 : 1 - ease(Math.min(1, (t - walk.out - walk.pause) / walk.back))
    const a0 = seatAngle(seat, count)
    const a1 = seatAngle(walk.toSeat, count) + (walk.movement === 'travel' ? WATCH_OFFSET : 0)
    const d = ((a1 - a0 + Math.PI * 3) % (Math.PI * 2)) - Math.PI // shortest way round
    const a = a0 + d * k
    const r = SEAT_RADIUS + (DOOR_R - SEAT_RADIUS) * Math.min(1, k * 1.8) // step back from the table first
    const x = Math.cos(a) * r
    const z = Math.sin(a) * r
    const moving = k > 0.001 && k < 0.999
    grp.position.set(x, moving ? Math.abs(Math.sin(t * 11)) * 0.09 : 0, z)
    const outward = Math.atan2(x, z)
    const heading = outward + (t < walk.out ? -1 : 1) * Math.sign(d || 1) * (Math.PI / 2)
    grp.rotation.y = k >= 0.999 ? outward : moving ? heading : seatFacing(seat, count)
  })
  const lit = !!walk && walk.movement !== 'none'
  return (
    <group ref={g} position={home} rotation={[0, seatFacing(seat, count), 0]}>
      {lit && (
        <>
          <pointLight position={[0, 2.6, 0.6]} intensity={9} distance={5.5} decay={1.6} color="#ffe2b0" />
          <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.03, 0]}>
            <circleGeometry args={[0.75, 32]} />
            <meshBasicMaterial color="#ffd27a" transparent opacity={0.45} />
          </mesh>
        </>
      )}
      {children}
    </group>
  )
}
