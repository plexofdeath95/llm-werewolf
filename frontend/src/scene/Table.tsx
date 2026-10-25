// Round wooden table with a flickering candle (and magic sparkles at night).
import { Sparkles } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { useRef } from 'react'
import * as THREE from 'three'
import { TABLE_RADIUS } from '../lib/seats'

function Candle({ night }: { night: boolean }) {
  const light = useRef<THREE.PointLight>(null)
  const flame = useRef<THREE.Mesh>(null)
  useFrame(({ clock }) => {
    const t = clock.elapsedTime
    const flicker = Math.sin(t * 13) * 0.25 + Math.sin(t * 7.3) * 0.2
    if (light.current) light.current.intensity = (night ? 5 : 2.2) + flicker
    if (flame.current) flame.current.scale.y = 1 + flicker * 0.4
  })
  return (
    <group position={[0, 0.98, 0]}>
      <mesh castShadow>
        <cylinderGeometry args={[0.12, 0.14, 0.4, 12]} />
        <meshStandardMaterial color="#f3e6c4" />
      </mesh>
      <mesh ref={flame} position={[0, 0.3, 0]}>
        <coneGeometry args={[0.06, 0.2, 8]} />
        <meshStandardMaterial color="#ffd36b" emissive="#ffae2b" emissiveIntensity={3} />
      </mesh>
      <pointLight ref={light} position={[0, 0.45, 0]} color="#ffb25a" distance={9} decay={1.7} castShadow />
      {night && <Sparkles count={30} scale={[2.2, 1.2, 2.2]} position={[0, 0.6, 0]} size={2.5} speed={0.3} color="#b9c8ff" />}
    </group>
  )
}

export function Table({ night }: { night: boolean }) {
  return (
    <group>
      <mesh position={[0, 0.72, 0]} castShadow receiveShadow>
        <cylinderGeometry args={[TABLE_RADIUS, TABLE_RADIUS, 0.16, 40]} />
        <meshStandardMaterial color="#7a4b29" roughness={0.75} />
      </mesh>
      <mesh position={[0, 0.81, 0]} receiveShadow>
        <cylinderGeometry args={[TABLE_RADIUS - 0.25, TABLE_RADIUS - 0.25, 0.02, 40]} />
        <meshStandardMaterial color="#8a5a33" roughness={0.6} />
      </mesh>
      <mesh position={[0, 0.36, 0]} castShadow>
        <cylinderGeometry args={[0.35, 0.6, 0.72, 12]} />
        <meshStandardMaterial color="#4f3019" flatShading />
      </mesh>
      <Candle night={night} />
    </group>
  )
}
