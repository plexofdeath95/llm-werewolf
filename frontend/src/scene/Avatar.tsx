// A procedural low-poly player: stool, body tinted by model color, head, eyes, hat.
// Speaking -> bounce + glow ring; thinking -> head tilt; dead -> floating ghost.
import { useFrame } from '@react-three/fiber'
import { useRef, type ReactNode } from 'react'
import * as THREE from 'three'
import { urgencyColor } from '../lib/colors'
import { hashSeed } from '../lib/seats'
import { Hat } from './Hat'

const SKINS = ['#f1c9a5', '#d9a77c', '#a8714a', '#7a4e2d', '#ffd9b8', '#c68c5f']

export interface AvatarProps {
  id: string
  color: string
  alive: boolean
  speaking: boolean
  thinking: boolean
  selected: boolean
  urgency?: number
  onSelect: () => void
  children?: ReactNode // Html overlays (name tag, bubbles)
}

export function Avatar(p: AvatarProps) {
  const seed = hashSeed(p.id)
  const body = useRef<THREE.Group>(null)
  const head = useRef<THREE.Group>(null)
  const ghost = !p.alive

  useFrame(({ clock }, dt) => {
    const t = clock.elapsedTime + (seed % 100)
    if (body.current) {
      const target = ghost ? 0.35 + Math.sin(t * 1.5) * 0.12 : p.speaking ? Math.abs(Math.sin(t * 9)) * 0.08 : 0
      body.current.position.y += (target - body.current.position.y) * Math.min(1, dt * 10)
    }
    if (head.current) {
      head.current.rotation.z = p.thinking ? Math.sin(t * 2.2) * 0.18 : head.current.rotation.z * 0.9
      head.current.rotation.x = p.speaking ? Math.sin(t * 7) * 0.08 : 0
    }
  })

  const mat = (color: string) => (
    <meshStandardMaterial color={ghost ? '#cfe3ff' : color} flatShading
      transparent={ghost} opacity={ghost ? 0.32 : 1}
      emissive={p.speaking ? color : '#000000'} emissiveIntensity={p.speaking ? 0.35 : 0} />
  )

  return (
    <group onClick={(e) => { e.stopPropagation(); p.onSelect() }}>
      {!ghost && (
        <mesh position={[0, 0.25, -0.15]} castShadow>
          <cylinderGeometry args={[0.32, 0.36, 0.5, 8]} />
          <meshStandardMaterial color="#4a2e1a" flatShading />
        </mesh>
      )}
      <group ref={body}>
        <mesh position={[0, 0.95, 0]} castShadow={!ghost}>
          <capsuleGeometry args={[0.3, 0.5, 4, 10]} />
          {mat(p.color)}
        </mesh>
        <group ref={head} position={[0, 1.62, 0]}>
          <mesh castShadow={!ghost}>
            <sphereGeometry args={[0.3, 14, 10]} />
            {mat(SKINS[seed % SKINS.length])}
          </mesh>
          {[-0.1, 0.1].map((x) => (
            <mesh key={x} position={[x, 0.04, 0.27]}>
              <sphereGeometry args={[0.045, 8, 6]} />
              <meshStandardMaterial color={ghost ? '#6a8bd6' : '#1a1a1a'} transparent={ghost} opacity={ghost ? 0.5 : 1} />
            </mesh>
          ))}
          {!ghost && <Hat variant={seed % 97} />}
        </group>
      </group>
      {(p.speaking || p.selected) && !ghost && (
        <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.03, 0]}>
          <ringGeometry args={[0.55, 0.7, 32]} />
          <meshBasicMaterial color={p.selected ? '#ffffff' : p.color} transparent opacity={0.8} />
        </mesh>
      )}
      {p.urgency !== undefined && !ghost && (
        <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.02, 0]} scale={0.6 + p.urgency * 0.06}>
          <ringGeometry args={[0.75, 0.82, 32]} />
          <meshBasicMaterial color={urgencyColor(p.urgency)} transparent opacity={0.85} />
        </mesh>
      )}
      {p.children}
    </group>
  )
}
