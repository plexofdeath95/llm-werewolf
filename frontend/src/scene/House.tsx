// Each player's cottage behind their seat: it rises at night (the night walk's destinations)
// and goes dark once its owner is dead.
import { useFrame } from '@react-three/fiber'
import { useRef } from 'react'
import * as THREE from 'three'
import { seatAngle } from '../lib/seats'
import type { GameView } from '../state/viewTypes'

export const HOUSE_R = 4.7

function House({ seat, count, shown, dead }: { seat: number; count: number; shown: boolean; dead: boolean }) {
  const ref = useRef<THREE.Group>(null)
  useFrame((_, dt) => {
    const g = ref.current
    if (!g) return
    const s = g.scale.x + ((shown ? 1 : 0.001) - g.scale.x) * Math.min(1, dt * 3)
    g.scale.setScalar(s)
    g.visible = s > 0.01
  })
  const a = seatAngle(seat, count)
  const x = Math.cos(a) * HOUSE_R
  const z = Math.sin(a) * HOUSE_R
  const glow = dead ? '#000000' : '#ffb347'
  return (
    <group ref={ref} position={[x, 0, z]} rotation={[0, Math.atan2(-x, -z), 0]} scale={0.001}>
      <mesh position={[0, 0.42, 0]} castShadow>
        <boxGeometry args={[1.15, 0.84, 0.95]} />
        <meshStandardMaterial color={dead ? '#3b342f' : '#c49a6c'} flatShading
          emissive={dead ? '#000000' : '#3a2210'} emissiveIntensity={0.6} />
      </mesh>
      <mesh position={[0, 1.13, 0]} rotation={[0, Math.PI / 4, 0]} castShadow>
        <coneGeometry args={[0.92, 0.62, 4]} />
        <meshStandardMaterial color={dead ? '#2b2422' : '#b8452f'} flatShading
          emissive={dead ? '#000000' : '#30100a'} emissiveIntensity={0.6} />
      </mesh>
      <mesh position={[0, 0.27, 0.48]}>
        <boxGeometry args={[0.3, 0.52, 0.04]} />
        <meshStandardMaterial color="#3a2414" />
      </mesh>
      <mesh position={[0.34, 0.52, 0.481]}>
        <planeGeometry args={[0.24, 0.22]} />
        <meshStandardMaterial color={dead ? '#111' : '#ffd38a'} emissive={glow} emissiveIntensity={dead ? 0 : 1.4} />
      </mesh>
      <mesh position={[-0.3, 0.62, 0.53]}>
        <sphereGeometry args={[0.06, 8, 6]} />
        <meshStandardMaterial color={dead ? '#333' : '#ffcc66'} emissive={glow} emissiveIntensity={dead ? 0 : 2.5} />
      </mesh>
    </group>
  )
}

export function Houses({ view }: { view: GameView }) {
  const shown = view.phase === 'night' || view.phase === 'dawn'
  return (
    <group>
      {view.order.map((pid) => {
        const p = view.players[pid]
        return <House key={pid} seat={p.seat} count={view.order.length} shown={shown} dead={!p.alive} />
      })}
    </group>
  )
}
